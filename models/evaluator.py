"""
CyberShield AI — Evaluator
Computes all evaluation metrics and prepares visualisation data.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score,
    precision_score, recall_score, roc_auc_score,
    matthews_corrcoef, cohen_kappa_score, log_loss,
    brier_score_loss, confusion_matrix, classification_report,
    roc_curve, auc, precision_recall_curve,
)


def evaluate(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    threshold: float = 0.50,
    binary: bool = True,
    class_names: list[str] | None = None,
) -> dict:
    """
    Returns a comprehensive metrics dict including:
    scalar metrics, confusion matrix, ROC/PR curve data.
    """
    avg = "binary" if binary else "weighted"

    # Probabilities
    if hasattr(model, "predict_proba"):
        y_proba_all = model.predict_proba(X_test)
        y_proba = y_proba_all[:, 1] if binary else y_proba_all
    else:
        y_proba = model.decision_function(X_test)
        y_proba_all = None

    # Predictions with threshold (binary only)
    if binary:
        y_pred = (y_proba >= threshold).astype(int)
    else:
        y_pred = model.predict(X_test)

    # ── Scalar metrics
    metrics = {
        "accuracy"      : accuracy_score(y_test, y_pred),
        "balanced_acc"  : balanced_accuracy_score(y_test, y_pred),
        "precision"     : precision_score(y_test, y_pred, average=avg, zero_division=0),
        "recall"        : recall_score(y_test, y_pred, average=avg, zero_division=0),
        "f1"            : f1_score(y_test, y_pred, average=avg, zero_division=0),
        "mcc"           : matthews_corrcoef(y_test, y_pred),
        "kappa"         : cohen_kappa_score(y_test, y_pred),
    }

    if binary:
        metrics["roc_auc"]     = roc_auc_score(y_test, y_proba)
        metrics["log_loss"]    = log_loss(y_test, y_proba)
        metrics["brier_score"] = brier_score_loss(y_test, y_proba)

    # ── Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    metrics["confusion_matrix"] = cm

    # ── Classification report
    target_names = class_names or [str(c) for c in sorted(y_test.unique())]
    metrics["classification_report"] = classification_report(
        y_test, y_pred, target_names=target_names,
        output_dict=True, zero_division=0,
    )

    # ── ROC curve (binary)
    if binary:
        fpr, tpr, roc_thresh = roc_curve(y_test, y_proba)
        metrics["roc_curve"] = {
            "fpr": fpr.tolist(), "tpr": tpr.tolist(),
            "thresholds": roc_thresh.tolist(),
            "auc": auc(fpr, tpr),
        }

        # ── PR curve
        prec, rec, pr_thresh = precision_recall_curve(y_test, y_proba)
        metrics["pr_curve"] = {
            "precision" : prec.tolist(), "recall": rec.tolist(),
            "thresholds": pr_thresh.tolist(),
            "auprc"     : auc(rec[::-1], prec[::-1]),
        }

    metrics["y_pred"]  = y_pred
    metrics["y_proba"] = y_proba

    return metrics


def triage_table(
    y_test: pd.Series,
    y_proba: np.ndarray,
    threshold: float,
    class_names: list[str] | None = None,
) -> pd.DataFrame:
    """Build a SOC-friendly triage table sorted by risk."""
    df = pd.DataFrame({
        "sample_index"      : y_test.index,
        "actual"            : y_test.values,
        "attack_probability": y_proba,
    })
    df["predicted"] = (df["attack_probability"] >= threshold).astype(int)
    df["risk_level"] = pd.cut(
        df["attack_probability"],
        bins=[-0.01, 0.30, 0.70, 1.001],
        labels=["🟢 Low", "🟡 Medium", "🔴 High"],
    )
    df["status"] = np.where(
        df["actual"] == df["predicted"], "✅ Correct", "⚠️ Review"
    )
    if class_names:
        df["actual_label"]    = df["actual"].map(lambda i: class_names[i] if i < len(class_names) else i)
        df["predicted_label"] = df["predicted"].map(lambda i: class_names[i] if i < len(class_names) else i)

    return (
        df.sort_values("attack_probability", ascending=False)
        .head(200)
        .reset_index(drop=True)
    )
