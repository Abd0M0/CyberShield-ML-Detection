"""
CyberShield AI — Preprocessor
Handles cleaning, feature engineering, label encoding, and scaling.
Supports binary mode (BENIGN vs ATTACK) and multiclass mode.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RANDOM_STATE, ATTACK_LABEL_MAP, BENIGN_LABEL

# Metadata columns that are not useful features
_META_COLS = {"Flow ID", "Source IP", "Destination IP",
              "Src IP", "Dst IP", "Timestamp", "timestamp"}


def find_label_column(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if "label" in col.lower():
            return col
    return None


# ── Label normalisation ────────────────────────────────────────────────────
def normalise_label(raw: str) -> str:
    """Map raw CIC label string → friendly attack type name."""
    key = raw.strip().lower()
    if key == BENIGN_LABEL.lower():
        return BENIGN_LABEL
    for pattern, friendly in ATTACK_LABEL_MAP.items():
        if pattern in key:
            return friendly
    return raw.strip()   # unknown, keep as-is


# ── Main preprocessing ─────────────────────────────────────────────────────
def preprocess(
    df: pd.DataFrame,
    mode: str = "binary",          # "binary" | "multiclass"
    sample_size: int | None = None,
) -> dict:
    """
    Returns a dict with keys:
        X, y, feature_names, label_encoder (multiclass only),
        scaler, class_names, label_col, df_clean
    Returns None on failure.
    """
    df = df.copy()

    # ── Find label column
    label_col = find_label_column(df)
    if label_col is None:
        return _fail("No label column found. Expected a column containing 'label'.")

    # ── Normalise labels
    df["_label_norm"] = df[label_col].astype(str).apply(normalise_label)

    # ── Build target
    if mode == "binary":
        df["target"] = (df["_label_norm"] != BENIGN_LABEL).astype(int)
        if df["target"].nunique() < 2:
            return _fail(
                "Only one class found after label processing. "
                "Include both BENIGN and attack CSV files."
            )
        class_names = ["BENIGN", "ATTACK"]
        y = df["target"]
        le = None
    else:  # multiclass
        le = LabelEncoder()
        df["target"] = le.fit_transform(df["_label_norm"])
        class_names = list(le.classes_)
        y = df["target"]

    # ── Drop metadata & label columns
    drop_cols = {label_col, "_label_norm", "target"} | _META_COLS
    drop_cols = [c for c in drop_cols if c in df.columns]
    X_raw = df.drop(columns=drop_cols)

    # ── Convert to numeric
    for col in X_raw.columns:
        X_raw[col] = pd.to_numeric(X_raw[col], errors="coerce")

    # ── Drop all-NaN columns
    X_raw = X_raw.dropna(axis=1, how="all")

    # ── Feature engineering
    X_raw = _engineer_features(X_raw)

    # ── Handle inf / nan
    X_raw.replace([np.inf, -np.inf], np.nan, inplace=True)
    X_raw.fillna(0, inplace=True)

    # ── Remove zero-variance columns
    variances = X_raw.var()
    const_cols = variances[variances == 0].index.tolist()
    if const_cols:
        X_raw.drop(columns=const_cols, inplace=True)

    feature_names = list(X_raw.columns)

    # ── Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    X = pd.DataFrame(X_scaled, columns=feature_names, index=X_raw.index)

    return {
        "X"            : X,
        "y"            : y.reset_index(drop=True),
        "feature_names": feature_names,
        "scaler"       : scaler,
        "label_encoder": le,
        "class_names"  : class_names,
        "label_col"    : label_col,
        "df_clean"     : df,
        "error"        : None,
    }


def _engineer_features(X: pd.DataFrame) -> pd.DataFrame:
    """Add informative derived features where source columns exist."""
    fwd = "Total Fwd Packets"
    bwd = "Total Backward Packets"
    if fwd in X.columns and bwd in X.columns:
        X = X.copy()
        X["Packet_Ratio"] = X[fwd] / (X[bwd] + 1)
        X["Total_Packets"] = X[fwd] + X[bwd]

    fwd_len = "Total Length of Fwd Packets"
    bwd_len = "Total Length of Bwd Packets"
    if fwd_len in X.columns and bwd_len in X.columns:
        X["Total_Bytes"] = X[fwd_len] + X[bwd_len]
        X["Bytes_Ratio"] = X[fwd_len] / (X[bwd_len] + 1)

    dur = "Flow Duration"
    if dur in X.columns and "Total_Packets" in X.columns:
        X["Packets_per_ms"] = X["Total_Packets"] / (X[dur] / 1000 + 1)

    return X


def _fail(msg: str) -> dict:
    return {"error": msg}


# ── Correlation filter (optional, call before training) ────────────────────
def drop_high_correlation(X: pd.DataFrame, threshold: float = 0.97) -> pd.DataFrame:
    """Remove one of each pair of features with correlation > threshold."""
    corr_matrix = X.corr().abs()
    upper = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )
    drop = [col for col in upper.columns if any(upper[col] > threshold)]
    return X.drop(columns=drop)
