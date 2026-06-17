"""
CyberShield AI — Comparison Tab
Side-by-side comparison of all trained models.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.trainer import build_comparison_df
from models.evaluator import evaluate
from sklearn.model_selection import train_test_split
from config import RANDOM_STATE



def _hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    """Convert #rrggbb to rgba(r,g,b,alpha) for Plotly compatibility."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def render(state: dict) -> None:
    st.markdown("## 📊 Model Comparison")

    if "train_results" not in state:
        st.warning("⚠️ Train models in the **Model Training** tab first.")
        return

    results = state["train_results"]
    comp_df = build_comparison_df(results)

    # ── Ranked table ───────────────────────────────────────────────────────
    st.markdown("### 🏆 Ranked Performance Table")
    st.dataframe(
        comp_df.style
               .highlight_max(
                   subset=["Accuracy","F1-Score","Precision","Recall","AUC-ROC","MCC"],
                   color="#00ff8730")
               .highlight_min(
                   subset=["Train Time (s)"], color="#60efff30")
               .format({"Accuracy":"{:.4f}","F1-Score":"{:.4f}",
                        "Precision":"{:.4f}","Recall":"{:.4f}",
                        "AUC-ROC":"{:.4f}","MCC":"{:.4f}",
                        "Train Time (s)":"{:.2f}"}),
        use_container_width=True,
    )

    st.markdown("---")

    # ── Radar chart ────────────────────────────────────────────────────────
    st.markdown("### 🕸️ Performance Radar")
    cats = ["Accuracy", "F1-Score", "Precision", "Recall", "AUC-ROC", "MCC"]
    fig  = go.Figure()
    colors = ["#00ff87","#60efff","#feca57","#ff6b35","#ff4757"]
    for i, (_, row) in enumerate(comp_df.iterrows()):
        vals = [row[c] for c in cats] + [row[cats[0]]]  # close polygon
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]],
            fill="toself", name=row["Model"],
            line=dict(color=colors[i % len(colors)], width=2),
            fillcolor=_hex_to_rgba(colors[i % len(colors)], 0.12),
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0,1], tickfont=dict(color="white")),
            angularaxis=dict(tickfont=dict(color="white")),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"), height=480,
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Bar comparison ─────────────────────────────────────────────────────
    st.markdown("### 📊 Metric Bar Chart")
    metric = st.selectbox("Select metric", cats + ["Train Time (s)"])
    fig2 = px.bar(
        comp_df, x="Model", y=metric,
        color="Model",
        color_discrete_sequence=colors,
        title=f"{metric} by Model",
        text=metric,
    )
    fig2.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0.05)",
        font=dict(color="white"), height=400,
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── ROC overlay (binary only) ──────────────────────────────────────────
    if state.get("binary_mode") and "X_test" in state:
        st.markdown("### 📈 ROC Curve Overlay")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=[0,1], y=[0,1], mode="lines",
            line=dict(dash="dash", color="rgba(255,255,255,0.3)"),
            name="Random Baseline",
        ))
        for i, (name, info) in enumerate(results.items()):
            ev = evaluate(
                info["model"], state["X_test"], state["y_test"],
                binary=True, class_names=state["preprocess"]["class_names"],
            )
            if "roc_curve" in ev:
                rc = ev["roc_curve"]
                fig3.add_trace(go.Scatter(
                    x=rc["fpr"], y=rc["tpr"], mode="lines",
                    name=f"{name} (AUC={rc['auc']:.3f})",
                    line=dict(color=colors[i % len(colors)], width=2),
                ))
        fig3.update_layout(
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor ="rgba(0,0,0,0.05)",
            font=dict(color="white"), height=480,
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Export comparison ──────────────────────────────────────────────────
    st.markdown("---")
    csv = comp_df.to_csv(index=False)
    st.download_button(
        "📥 Download Comparison Table (CSV)",
        data=csv, file_name="model_comparison.csv", mime="text/csv",
    )
