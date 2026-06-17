"""
CyberShield AI — Detection & Analysis
4 tabs: Overview | Model Training | Model Comparison | Attack Analytics
Run: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="CyberShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.styles    import inject, page_header
from dashboard.overview  import render as overview
from dashboard.training  import render as training
from dashboard.comparison import render as comparison
from dashboard.analytics import render as analytics

inject()

if "app_state" not in st.session_state:
    st.session_state["app_state"] = {}
state = st.session_state["app_state"]

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0 8px;">
        <h2 style="background:linear-gradient(135deg,#00ff87,#60efff);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   margin:0;font-size:1.6em;">🛡️ CyberShield AI</h2>
        <p style="color:rgba(255,255,255,0.45);font-size:0.8em;margin:4px 0 0;">
            ML-Powered Intrusion Detection
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    TABS = {
        "🏠  Overview"         : "overview",
        "🤖  Model Training"   : "training",
        "📊  Model Comparison" : "comparison",
        "📈  Attack Analytics" : "analytics",
    }

    if "current_tab" not in st.session_state:
        st.session_state["current_tab"] = "overview"

    for label, key in TABS.items():
        if st.button(label, use_container_width=True, key=f"nav_{key}"):
            st.session_state["current_tab"] = key
            st.rerun()

    st.markdown("---")

    has_data  = "df"         in state
    has_model = "best_model" in state

    st.markdown("### 🟢 System Status")
    st.markdown(
        f"- Dataset: {'✅ Loaded' if has_data else '❌ None'}\n"
        f"- Model:   {'✅ Trained' if has_model else '❌ None'}\n"
        f"- Best:    {state.get('best_name', '—')}\n"
    )

    st.markdown("---")
    st.caption("CyberShield ML Project © 2025")

# ── Header ─────────────────────────────────────────────────────────────────
page_header(
    "CyberShield AI",
    "ML-Powered Network Intrusion Detection System",
)

# ── Route ──────────────────────────────────────────────────────────────────
tab = st.session_state["current_tab"]

if   tab == "overview"  : overview(state)
elif tab == "training"  : training(state)
elif tab == "comparison": comparison(state)
elif tab == "analytics" : analytics(state)
