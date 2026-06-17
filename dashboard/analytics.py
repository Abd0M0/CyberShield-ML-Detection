"""
CyberShield AI — Analytics Tab
Attack pattern breakdown, feature distributions, correlation heatmap.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.preprocessor import find_label_column, normalise_label


def render(state: dict) -> None:
    st.markdown("## 📈 Attack Analytics")

    if "df" not in state:
        st.warning("⚠️ Upload a dataset in the **Overview** tab first.")
        return

    df = state["df"].copy()
    label_col = find_label_column(df)
    if not label_col:
        st.error("No label column found in the dataset.")
        return

    df["_class"] = df[label_col].astype(str).apply(normalise_label)

    tabs = st.tabs(["🥧 Distribution", "📊 Feature by Class",
                    "🔗 Correlation", "🎯 Attack Profiles"])

    # ── Distribution ───────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("### Traffic Class Distribution")
        dist = df["_class"].value_counts().reset_index()
        dist.columns = ["Class", "Count"]
        dist["Percent"] = (dist["Count"] / dist["Count"].sum() * 100).round(2)
        dist["Is_Attack"] = dist["Class"].apply(lambda x: "Attack" if x != "BENIGN" else "Benign")

        col1, col2 = st.columns(2)
        with col1:
            fig = px.treemap(dist, path=["Class"], values="Count",
                             color="Count", color_continuous_scale="Viridis",
                             title="Traffic Treemap")
            _dark(fig)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            dist["Is_Attack"] = dist["Class"].apply(lambda x: "Attack" if x != "BENIGN" else "Benign")
            fig2 = px.sunburst(dist, path=["Is_Attack","Class"], values="Count",
                               color="Is_Attack",
                               color_discrete_map={"Attack":"#ff4757","Benign":"#00ff87"},
                               title="Benign vs Attack Share")
            _dark(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(dist, use_container_width=True)

    # ── Feature by Class ───────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### Feature Distribution by Class")
        num_cols = [c for c in df.select_dtypes(include=[np.number]).columns
                    if c not in (label_col, "_class", "target")]

        selected_feat = st.selectbox("Feature", num_cols[:50])
        top_classes   = df["_class"].value_counts().head(8).index.tolist()
        df_filtered   = df[df["_class"].isin(top_classes)]

        fig = px.violin(
            df_filtered, x="_class", y=selected_feat,
            color="_class", box=True, points=False,
            title=f"{selected_feat} — Distribution by Class",
        )
        _dark(fig)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Box plot multi-feature
        st.markdown("#### Multi-Feature Box Plot")
        sel_feats = st.multiselect("Features to compare",
                                   num_cols[:40], default=num_cols[:4])
        if sel_feats:
            fig2 = go.Figure()
            colors = px.colors.qualitative.Vivid
            for i, feat in enumerate(sel_feats[:8]):
                fig2.add_trace(go.Box(
                    y=df[feat].clip(lower=df[feat].quantile(0.01),
                                    upper=df[feat].quantile(0.99)),
                    name=feat,
                    marker_color=colors[i % len(colors)],
                ))
            _dark(fig2)
            st.plotly_chart(fig2, use_container_width=True)

    # ── Correlation ────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### Feature Correlation Heatmap")
        num_df = df.select_dtypes(include=[np.number]).drop(
            columns=[c for c in ["target","_class"] if c in df.columns], errors="ignore"
        )
        top_n = st.slider("Top N features (by variance)", 10, 40, 20)
        top_feats = num_df.var().nlargest(top_n).index.tolist()
        corr = num_df[top_feats].corr()

        fig = px.imshow(
            corr, color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1, title=f"Correlation Matrix (Top {top_n} features)",
            text_auto=".2f",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=9),
            height=600,
        )
        st.plotly_chart(fig, use_container_width=True)

        highly_corr = []
        for i in range(len(corr)):
            for j in range(i+1, len(corr)):
                val = abs(corr.iloc[i, j])
                if val > 0.95:
                    highly_corr.append({
                        "Feature A": corr.columns[i],
                        "Feature B": corr.columns[j],
                        "Correlation": round(val, 4),
                    })
        if highly_corr:
            st.warning(f"⚠️ {len(highly_corr)} highly correlated pairs found (>0.95). "
                       "Consider removing one of each pair to reduce redundancy.")
            st.dataframe(pd.DataFrame(highly_corr), use_container_width=True)
        else:
            st.success("✅ No highly correlated feature pairs (>0.95) detected.")

    # ── Attack Profiles ────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("### Attack Traffic Profiles")
        st.caption("Mean feature values per attack type — helps understand attack signatures.")

        key_feats = [
            "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
            "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean",
            "SYN Flag Count", "RST Flag Count", "ACK Flag Count",
        ]
        available = [f for f in key_feats if f in df.columns]
        if not available:
            st.info("Key flow features not found. Upload a CIC-IDS2017 CSV.")
        else:
            profiles = df.groupby("_class")[available].mean().reset_index()
            # Encode class labels as integers (parcoords requires numeric color)
            profiles["_class_code"] = pd.Categorical(profiles["_class"]).codes
            fig = px.parallel_coordinates(
                profiles, color="_class_code",
                dimensions=available,
                color_continuous_scale=px.colors.sequential.Plasma,
                title="Parallel Coordinates — Attack Profiles",
                labels={"_class_code": "Attack Class"},
            )
            _dark(fig)
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Mean Feature Values Table"):
                st.dataframe(profiles.set_index("_class").style.background_gradient(
                    cmap="RdYlGn", axis=0), use_container_width=True)


def _dark(fig) -> None:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0.05)",
        font=dict(color="white"), height=440,
    )
