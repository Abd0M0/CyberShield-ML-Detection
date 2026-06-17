"""
CyberShield AI — Data Loader
Handles single CSV, multiple CSVs, uploaded files, and multi-file merging.
"""

from __future__ import annotations
import io
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RANDOM_STATE, MAX_SAMPLE_SIZE


ENCODINGS = ["utf-8", "utf-8-sig", "cp1252", "latin1"]


# ── Core reader ────────────────────────────────────────────────────────────
def read_csv_robust(source) -> pd.DataFrame:
    """Read CSV with automatic encoding fallback."""
    last_err = None
    for enc in ENCODINGS:
        try:
            if hasattr(source, "seek"):
                source.seek(0)
            return pd.read_csv(source, low_memory=False, encoding=enc)
        except UnicodeDecodeError as e:
            last_err = e
    raise ValueError(
        f"Cannot decode CSV. Tried: {ENCODINGS}. Last error: {last_err}"
    )


# ── Single file ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_single(path: str, sample_size: int | None = None) -> pd.DataFrame:
    df = read_csv_robust(path)
    df.columns = df.columns.str.strip()
    if sample_size and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=RANDOM_STATE)
    return df


# ── Multiple files (from disk paths) ──────────────────────────────────────
def load_multiple(paths: list[str], sample_size: int | None = None) -> pd.DataFrame:
    frames = []
    for p in paths:
        try:
            df = read_csv_robust(p)
            df.columns = df.columns.str.strip()
            frames.append(df)
        except Exception as e:
            st.warning(f"⚠️ Skipped {Path(p).name}: {e}")
    if not frames:
        raise ValueError("No valid CSV files could be loaded.")
    merged = pd.concat(frames, ignore_index=True)
    if sample_size and sample_size < len(merged):
        merged = merged.sample(n=sample_size, random_state=RANDOM_STATE)
    return merged


# ── Uploaded files (Streamlit file objects) ───────────────────────────────
def load_uploaded(files, sample_size: int | None = None) -> pd.DataFrame:
    frames = []
    for f in files:
        try:
            df = read_csv_robust(f)
            df.columns = df.columns.str.strip()
            frames.append(df)
        except Exception as e:
            st.warning(f"⚠️ Skipped {f.name}: {e}")
    if not frames:
        raise ValueError("No valid CSV files were uploaded.")
    merged = pd.concat(frames, ignore_index=True)
    if sample_size and sample_size < len(merged):
        merged = merged.sample(n=sample_size, random_state=RANDOM_STATE)
    return merged


# ── Dataset summary ────────────────────────────────────────────────────────
def dataset_summary(df: pd.DataFrame) -> dict:
    label_col = _find_label_col(df)
    summary = {
        "rows"        : len(df),
        "columns"     : len(df.columns),
        "missing"     : int(df.isna().sum().sum()),
        "duplicates"  : int(df.duplicated().sum()),
        "memory_mb"   : round(df.memory_usage(deep=True).sum() / 1_048_576, 2),
        "label_col"   : label_col,
        "class_dist"  : {},
    }
    if label_col:
        dist = (
            df[label_col].astype(str).str.strip().value_counts(dropna=False)
        )
        summary["class_dist"] = dist.to_dict()
    return summary


def _find_label_col(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if "label" in col.lower():
            return col
    return None
