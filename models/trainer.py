"""
CyberShield AI — Model Trainer
Trains Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM.
Uses stratified K-fold cross-validation to produce reliable metric estimates.
"""

from __future__ import annotations
import time
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, f1_score, matthews_corrcoef, precision_score, recall_score
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RANDOM_STATE, CV_FOLDS, MODEL_DIR

try:
    from xgboost import XGBClassifier
    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False

try:
    from lightgbm import LGBMClassifier
    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False


# ── Model definitions ──────────────────────────────────────────────────────
def _build_models(n_classes: int) -> dict:
    obj = "binary:logistic" if n_classes == 2 else "multi:softmax"
    lgb_obj = "binary" if n_classes == 2 else "multiclass"

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=150, max_depth=18, min_samples_leaf=2,
            random_state=RANDOM_STATE, class_weight="balanced", n_jobs=-1,
        ),
    }
    if _HAS_XGB:
        models["XGBoost"] = XGBClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_STATE, eval_metric="logloss",
            objective=obj, n_jobs=-1, verbosity=0,
                    )
    if _HAS_LGB:
        models["LightGBM"] = LGBMClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_STATE, objective=lgb_obj,
            class_weight="balanced", n_jobs=-1, verbose=-1,
        )
    return models


# ── CV scoring ─────────────────────────────────────────────────────────────
def _build_scorers(binary: bool) -> dict:
    avg = "binary" if binary else "weighted"
    return {
        "accuracy" : "accuracy",
        "f1"       : make_scorer(f1_score, average=avg, zero_division=0),
        "precision": make_scorer(precision_score, average=avg, zero_division=0),
        "recall"   : make_scorer(recall_score, average=avg, zero_division=0),
        "roc_auc"  : "roc_auc" if binary else "roc_auc_ovr_weighted",
        "mcc"      : make_scorer(matthews_corrcoef),
    }


# ── Main training function ─────────────────────────────────────────────────
def train_all(
    X: pd.DataFrame,
    y: pd.Series,
    n_classes: int,
    progress_cb=None,      # callable(model_name, pct)
) -> dict:
    """
    Train all available models with cross-validation.
    Returns a dict keyed by model name with sub-keys:
        model, cv_results, mean_metrics, std_metrics, training_time
    """
    binary  = n_classes == 2
    models  = _build_models(n_classes)
    scorers = _build_scorers(binary)
    skf     = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    results = {}
    total   = len(models)

    for idx, (name, model) in enumerate(models.items()):
        if progress_cb:
            progress_cb(name, idx / total)

        t0 = time.time()
        cv = cross_validate(
            model, X, y,
            cv=skf,
            scoring=scorers,
            return_train_score=False,
            n_jobs=1,    # avoid nested parallelism issues
        )
        elapsed = time.time() - t0

        # Final fit on full data for export / inference
        model.fit(X, y)

        means = {k.replace("test_", ""): float(np.mean(v))
                 for k, v in cv.items() if k.startswith("test_")}
        stds  = {k.replace("test_", ""): float(np.std(v))
                 for k, v in cv.items() if k.startswith("test_")}

        results[name] = {
            "model"        : model,
            "cv_results"   : cv,
            "mean_metrics" : means,
            "std_metrics"  : stds,
            "training_time": round(elapsed, 2),
        }

        # Save to disk
        _save_model(name, model, means, elapsed)

    if progress_cb:
        progress_cb("Done", 1.0)

    return results


# ── Persist / load ─────────────────────────────────────────────────────────
def _save_model(name: str, model, metrics: dict, t: float) -> None:
    safe_name = name.replace(" ", "_").lower()
    path = MODEL_DIR / f"{safe_name}.joblib"
    joblib.dump({"model": model, "metrics": metrics, "training_time": t}, path)


def load_model(name: str):
    safe_name = name.replace(" ", "_").lower()
    path = MODEL_DIR / f"{safe_name}.joblib"
    if not path.exists():
        return None
    return joblib.load(path)


def load_best_model(results: dict) -> tuple[str, object]:
    """Return (name, model) of the model with highest mean F1."""
    best = max(results, key=lambda k: results[k]["mean_metrics"].get("f1", 0))
    return best, results[best]["model"]


# ── Comparison table ───────────────────────────────────────────────────────
def build_comparison_df(results: dict) -> pd.DataFrame:
    rows = []
    for name, info in results.items():
        m = info["mean_metrics"]
        s = info["std_metrics"]
        rows.append({
            "Model"         : name,
            "Accuracy"      : round(m.get("accuracy", 0), 4),
            "F1-Score"      : round(m.get("f1", 0), 4),
            "Precision"     : round(m.get("precision", 0), 4),
            "Recall"        : round(m.get("recall", 0), 4),
            "AUC-ROC"       : round(m.get("roc_auc", 0), 4),
            "MCC"           : round(m.get("mcc", 0), 4),
            "Train Time (s)": info["training_time"],
        })
    df = pd.DataFrame(rows).sort_values("F1-Score", ascending=False).reset_index(drop=True)
    df.index += 1
    return df
