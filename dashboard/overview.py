"""
CyberShield AI — Overview Tab
Shows dataset health, class distribution, feature stats, and quick EDA.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.loader import load_uploaded, load_multiple, dataset_summary
from pipeline.preprocessor import find_label_column, normalise_label
from config import THEME


def render(state: dict) -> None:
    st.markdown("## 📂 Dataset Overview")
    st.markdown("Upload one or more **CIC-IDS2017** CSV files — or mix both datasets together.")

    # ── Upload ────────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Upload CSV file(s)",
        type=["csv"],
        accept_multiple_files=True,
        key="csv_uploader",
    )

    sample_size = st.select_slider(
        "Sample size (rows to load per file)",
        options=[10_000, 25_000, 50_000, 100_000, 150_000, 0],
        value=50_000,
        format_func=lambda x: f"{x:,}" if x else "All rows",
    )
    sample_arg = sample_size if sample_size > 0 else None

    if uploaded:
        with st.spinner("Loading and merging files…"):
            try:
                df = load_uploaded(uploaded, sample_size=sample_arg)
                state["df"] = df
                st.success(f"✅ Loaded {len(df):,} rows from {len(uploaded)} file(s).")
            except Exception as e:
                st.error(str(e))
                return
    elif "df" not in state:
        st.info("👆 Upload at least one CIC-IDS2017 CSV file to continue.")
        _show_dataset_guide()
        return

    df = state["df"]
    summary = dataset_summary(df)

    # ── KPI cards ─────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Rows",         f"{summary['rows']:,}")
    c2.metric("Columns",      f"{summary['columns']:,}")
    c3.metric("Missing Cells",f"{summary['missing']:,}")
    c4.metric("Duplicates",   f"{summary['duplicates']:,}")
    c5.metric("Memory",       f"{summary['memory_mb']} MB")

    st.markdown("---")

    # ── Class distribution ─────────────────────────────────────────────────
    label_col = summary["label_col"]
    if label_col:
        st.markdown("### 🏷️ Class Distribution")
        dist_raw  = summary["class_dist"]
        dist_norm = {normalise_label(k): v for k, v in dist_raw.items()}

        # Aggregate duplicates after normalisation
        agg: dict = {}
        for k, v in dist_norm.items():
            agg[k] = agg.get(k, 0) + v
        dist_df = pd.DataFrame(
            list(agg.items()), columns=["Class", "Count"]
        ).sort_values("Count", ascending=False)
        dist_df["Percent"] = (dist_df["Count"] / dist_df["Count"].sum() * 100).round(2)

        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(
                dist_df, x="Class", y="Count", color="Count",
                color_continuous_scale=["#00ff87", "#60efff", "#ff4757"],
                title="Flow Count per Class",
            )
            _dark_layout(fig)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.pie(
                dist_df, names="Class", values="Count",
                color_discrete_sequence=px.colors.sequential.Viridis,
                title="Class Share",
            )
            _dark_layout(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        with st.expander("📋 Full Distribution Table"):
            st.dataframe(dist_df, use_container_width=True)

    st.markdown("---")

    # ── Missing values heatmap ─────────────────────────────────────────────
    st.markdown("### 🔍 Feature Quality")
    miss = df.isnull().mean().sort_values(ascending=False)
    miss = miss[miss > 0].head(30)
    if miss.empty:
        st.success("✅ No missing values detected.")
    else:
        fig = px.bar(
            x=miss.index, y=miss.values * 100,
            labels={"x": "Feature", "y": "Missing (%)"},
            title="Top Features with Missing Values",
            color=miss.values, color_continuous_scale="Reds",
        )
        _dark_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    # ── Numeric summary ────────────────────────────────────────────────────
    with st.expander("📊 Numeric Feature Statistics"):
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if label_col in num_cols:
            num_cols.remove(label_col)
        st.dataframe(
            df[num_cols].describe().T.style.background_gradient(cmap="viridis"),
            use_container_width=True,
        )

    # ── Sample data ────────────────────────────────────────────────────────
    with st.expander("🗂️ Sample Data (first 50 rows)"):
        st.dataframe(df.head(50), use_container_width=True)


def _dark_layout(fig) -> None:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0.05)",
        font=dict(color="white"),
        height=360,
    )


def _show_dataset_guide() -> None:
    st.markdown("""
    ---
    ### 📥 Supported Datasets

    #### CIC-IDS2017
    | Source | Link |
    |--------|------|
    | Official UNB page | https://www.unb.ca/cic/datasets/ids-2017.html |
    | Kaggle mirror | Search "CIC-IDS-2017" on kaggle.com |

    **Recommended 2017 files:**
    - `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`
    - `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`
    - `Tuesday-WorkingHours.pcap_ISCX.csv`
    - `Wednesday-WorkingHours.pcap_ISCX.csv`

    > 💡 **Tip:** Upload files from both datasets at once — CyberShield AI merges and normalises all labels automatically.
    """)
