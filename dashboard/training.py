"""
CyberShield AI — Training Tab
Train all 5 models with configurable CV and display live progress.
"""

import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.preprocessor import preprocess, drop_high_correlation
from models.trainer import train_all, build_comparison_df, load_best_model
from models.evaluator import evaluate
from database.db import save_model_run
from config import TEST_SIZE, CV_FOLDS, RANDOM_STATE
from sklearn.model_selection import train_test_split


def render(state: dict) -> None:
    st.markdown("## 🤖 Model Training")

    if "df" not in state:
        st.warning("⚠️ Upload a dataset in the **Overview** tab first.")
        return

    df = state["df"]

    # ── Config ─────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mode = st.selectbox("Classification Mode", ["binary", "multiclass"], key="train_mode",
                            help="Binary = BENIGN vs ATTACK | Multiclass = per attack type")
    with col2:
        test_split = st.slider("Test Split", 0.15, 0.40, TEST_SIZE, 0.05, key="train_test_split")
    with col3:
        cv_folds = st.slider("CV Folds", 3, 10, CV_FOLDS, key="train_cv_folds")
    with col4:
        drop_corr = st.checkbox("Drop Highly Correlated Features (>0.97)", value=False, key="train_drop_corr")

    st.markdown("---")

    if st.button("🚀 Train All 3 Models", use_container_width=True):
        _run_training(state, df, mode, test_split, cv_folds, drop_corr)

    # ── Show results if already trained ────────────────────────────────────
    if "train_results" in state:
        _show_results(state)


def _run_training(state, df, mode, test_split, cv_folds, drop_corr):
    prog_bar = st.progress(0)
    status   = st.empty()

    # ── Preprocess
    status.info("🔧 Preprocessing data…")
    result = preprocess(df, mode=mode)
    if result.get("error"):
        st.error(result["error"])
        return

    X, y = result["X"], result["y"]
    n_classes = y.nunique()

    if drop_corr:
        status.info("🔗 Removing highly correlated features…")
        before = X.shape[1]
        X = drop_high_correlation(X)
        st.info(f"Removed {before - X.shape[1]} correlated features. {X.shape[1]} remaining.")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_split, random_state=RANDOM_STATE, stratify=y
    )

    prog_bar.progress(10)
    status.info("🏋️ Training models with cross-validation…")

    model_progress = st.empty()

    def progress_cb(name, pct):
        prog_bar.progress(int(10 + pct * 80))
        model_progress.info(f"Training: **{name}**…")

    t0 = time.time()
    results = train_all(X_train, y_train, n_classes=n_classes, progress_cb=progress_cb)
    elapsed = time.time() - t0
    model_progress.empty()

    # Evaluate best model on hold-out test set
    best_name, best_model = load_best_model(results)
    binary = (mode == "binary")
    eval_res = evaluate(best_model, X_test, y_test, binary=binary,
                        class_names=result["class_names"])

    prog_bar.progress(100)
    status.success(f"✅ Training complete in {elapsed:.1f}s. Best model: **{best_name}**")

    # Persist to session state
    state["train_results"]  = results
    state["preprocess"]     = result
    state["X_train"]        = X_train
    state["X_test"]         = X_test
    state["y_train"]        = y_train
    state["y_test"]         = y_test
    state["best_name"]      = best_name
    state["best_model"]     = best_model
    state["eval_res"]       = eval_res
    state["binary_mode"]    = binary

    # Save run to DB
    for name, info in results.items():
        save_model_run(
            dataset_path="uploaded", model_name=name,
            metrics=info["mean_metrics"], training_time=info["training_time"],
        )

    st.rerun()  # Rerun cleanly so render() calls _show_results() exactly once


def _show_results(state: dict) -> None:
    results = state["train_results"]
    comp_df = build_comparison_df(results)

    st.markdown("### 📊 Cross-Validation Results")
    st.dataframe(
        comp_df.style
               .highlight_max(subset=["Accuracy","F1-Score","Precision","Recall","AUC-ROC","MCC"],
                              color="#00ff8722")
               .format({"Accuracy":"{:.4f}","F1-Score":"{:.4f}",
                        "Precision":"{:.4f}","Recall":"{:.4f}",
                        "AUC-ROC":"{:.4f}","MCC":"{:.4f}"}),
        use_container_width=True,
    )

    st.caption(f"Best model by F1-Score: **{state.get('best_name', '—')}**")

    # Hold-out evaluation
    if "eval_res" in state:
        ev = state["eval_res"]
        st.markdown(f"### 🎯 Hold-Out Test Set — {state['best_name']}")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Accuracy",  f"{ev['accuracy']:.4f}")
        c2.metric("F1-Score",  f"{ev['f1']:.4f}")
        c3.metric("Precision", f"{ev['precision']:.4f}")
        c4.metric("Recall",    f"{ev['recall']:.4f}")

        if state.get("binary_mode") and "roc_auc" in ev:
            c1,c2,c3 = st.columns(3)
            c1.metric("AUC-ROC",     f"{ev['roc_auc']:.4f}")
            c2.metric("MCC",         f"{ev['mcc']:.4f}")
            c3.metric("Brier Score", f"{ev['brier_score']:.4f}")


def _model_color(name: str) -> str:
    palette = {
        "Logistic Regression": "#60efff",
        "Decision Tree"      : "#feca57",
        "Random Forest"      : "#00ff87",
        "XGBoost"            : "#ff6b35",
        "LightGBM"           : "#ff4757",
    }
    return palette.get(name, "#ffffff")
