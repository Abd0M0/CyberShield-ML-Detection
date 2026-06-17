"""
CyberShield AI — Dashboard Styles
Inject CSS into Streamlit for consistent dark cybersecurity theme.
"""

import streamlit as st


def inject() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    *, *::before, *::after { font-family: 'Inter', sans-serif; box-sizing: border-box; }
    code, pre { font-family: 'JetBrains Mono', monospace; }

    .stApp { background: radial-gradient(circle at 15% 40%, #050d1a 0%, #000000 100%); }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0,10,25,0.85);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0,255,135,0.08);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00ff87, #60efff);
        color: #000; font-weight: 700; border-radius: 10px;
        padding: 10px 24px; border: none; transition: all 0.25s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 22px rgba(0,255,135,0.45);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; background: rgba(255,255,255,0.02);
        border-radius: 14px; padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px; padding: 9px 20px; font-weight: 600; color: rgba(255,255,255,0.6);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ff87, #60efff); color: #000;
    }

    /* Metrics */
    [data-testid="stMetricValue"] { color: #00ff87; font-weight: 800; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00ff87, #60efff);
        border-radius: 8px;
    }

    /* DataFrames */
    [data-testid="stDataFrame"] { border-radius: 12px; }

    /* Alerts */
    .alert-critical { color: #ff4757; font-weight: 700; }
    .alert-high     { color: #ff6b35; font-weight: 600; }
    .alert-medium   { color: #feca57; font-weight: 600; }
    .alert-low      { color: #00ff87; }

    /* Card */
    .ids-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px; padding: 20px;
        transition: border-color 0.3s;
    }
    .ids-card:hover { border-color: rgba(0,255,135,0.25); }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f"""
    <div style="text-align:center; padding:32px 20px 20px;
                background:linear-gradient(135deg,rgba(0,255,135,0.04),rgba(96,239,255,0.02));
                border-radius:24px; border:1px solid rgba(0,255,135,0.08); margin-bottom:24px;">
        <h1 style="font-size:2.8em; margin:0;
                   background:linear-gradient(135deg,#00ff87,#60efff);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            🛡️ {title}
        </h1>
        <p style="color:rgba(255,255,255,0.6); margin:8px 0 0; font-size:1.05em;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str = "", color: str = "#00ff87") -> None:
    st.markdown(f"""
    <div class="ids-card" style="text-align:center;">
        <div style="font-size:0.85em; color:rgba(255,255,255,0.55); margin-bottom:6px;">{label}</div>
        <div style="font-size:2em; font-weight:800; color:{color};">{value}</div>
        <div style="font-size:0.8em; color:rgba(255,255,255,0.4); margin-top:4px;">{delta}</div>
    </div>
    """, unsafe_allow_html=True)


def badge(text: str, color: str = "#00ff87") -> str:
    bg = color + "22"
    return (f'<span style="display:inline-block;padding:3px 12px;border-radius:20px;'
            f'font-size:12px;font-weight:600;background:{bg};color:{color};">{text}</span>')
