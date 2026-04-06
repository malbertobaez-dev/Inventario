"""
Brand styling — CSS injection and theme constants for Streamlit.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT,
    COLOR_NEUTRAL, COLOR_WHITE, COLOR_DARK_TEXT,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_BG_MAIN, COLOR_CARD_BG,
)


BRAND_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Reset & Global ──────────────────────────────────────────── */
.stApp {{
    font-family: 'Inter', sans-serif;
    background-color: {COLOR_BG_MAIN};
}}

.main .block-container {{
    max-width: 1400px;
    padding-top: 0.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}}

/* ── Hide Streamlit chrome ───────────────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ── Dashboard Header ────────────────────────────────────────── */
.dashboard-header {{
    background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, #003A72 60%, #004B8D 100%);
    color: {COLOR_WHITE};
    padding: 1.75rem 2.5rem;
    margin-bottom: 1.75rem;
    border-bottom: 3px solid {COLOR_ACCENT};
    position: relative;
    overflow: hidden;
}}

.dashboard-header::before {{
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,204,0,0.06);
}}

.dashboard-header::after {{
    content: '';
    position: absolute;
    bottom: -60px; right: 80px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: rgba(255,255,255,0.03);
}}

.dashboard-header h1 {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.5px;
    position: relative;
}}

.dashboard-header p {{
    font-size: 0.9rem;
    opacity: 0.75;
    margin: 0;
    font-weight: 300;
    letter-spacing: 0.3px;
    position: relative;
}}

/* ── KPI Cards ───────────────────────────────────────────────── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 1rem;
    margin-bottom: 1.75rem;
}}

@media (max-width: 1200px) {{
    .kpi-grid {{ grid-template-columns: repeat(3, 1fr); }}
}}

@media (max-width: 768px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}

.kpi-card {{
    background: {COLOR_CARD_BG};
    border-radius: 8px;
    padding: 1.1rem 1.25rem 0.9rem 1.1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.04);
    border-left: 4px solid #CBD5E0;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    position: relative;
}}

.kpi-card:hover {{
    box-shadow: 0 4px 20px rgba(0,45,90,0.12);
    transform: translateY(-2px);
}}

.kpi-card.green  {{ border-left-color: {COLOR_SUCCESS}; }}
.kpi-card.yellow {{ border-left-color: {COLOR_WARNING}; }}
.kpi-card.red    {{ border-left-color: {COLOR_DANGER}; }}
.kpi-card.gray   {{ border-left-color: #CBD5E0; }}

.kpi-dot {{
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 0.4rem;
    vertical-align: middle;
    flex-shrink: 0;
}}
.kpi-dot.green  {{ background: {COLOR_SUCCESS}; box-shadow: 0 0 6px rgba(40,167,69,0.5); }}
.kpi-dot.yellow {{ background: {COLOR_WARNING}; box-shadow: 0 0 6px rgba(230,168,23,0.5); }}
.kpi-dot.red    {{ background: {COLOR_DANGER};  box-shadow: 0 0 6px rgba(220,53,69,0.5); }}
.kpi-dot.gray   {{ background: #CBD5E0; }}

.kpi-label {{
    font-size: 0.72rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
}}

.kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.55rem;
    font-weight: 600;
    color: {COLOR_DARK_TEXT};
    line-height: 1.1;
    margin-bottom: 0.3rem;
}}

.kpi-sub {{
    font-size: 0.72rem;
    color: #94A3B8;
    margin-top: 0.2rem;
    font-weight: 400;
}}

/* ── Section Headers ─────────────────────────────────────────── */
.section-header {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: {COLOR_PRIMARY};
    margin: 1.5rem 0 0.85rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {COLOR_ACCENT};
    letter-spacing: -0.2px;
}}

/* ── Alert Banners ───────────────────────────────────────────── */
.alert-banner {{
    padding: 0.75rem 1.1rem;
    border-radius: 6px;
    margin-bottom: 0.6rem;
    font-size: 0.875rem;
    font-weight: 500;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    border-left: 4px solid transparent;
}}

.alert-banner.danger {{
    background: #FFF5F5;
    border-left-color: {COLOR_DANGER};
    color: #9B1C1C;
}}

.alert-banner.warning {{
    background: #FFFBEB;
    border-left-color: {COLOR_WARNING};
    color: #78350F;
}}

.alert-banner.success {{
    background: #F0FDF4;
    border-left-color: {COLOR_SUCCESS};
    color: #14532D;
}}

/* ── Upload Zone ─────────────────────────────────────────────── */
.upload-zone {{
    border: 2px dashed {COLOR_SECONDARY};
    border-radius: 8px;
    padding: 2.5rem 2rem;
    text-align: center;
    background: linear-gradient(135deg, #F8FBFF 0%, #EEF4FF 100%);
    margin: 1rem 0;
    transition: border-color 0.2s ease;
}}

.upload-zone:hover {{
    border-color: {COLOR_ACCENT};
}}

/* ── Sidebar ─────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {COLOR_PRIMARY} 0%, #001E40 100%);
    border-right: 1px solid rgba(255,204,0,0.15);
}}

section[data-testid="stSidebar"] > div {{
    padding-top: 1rem;
}}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p {{
    color: {COLOR_WHITE};
}}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stTextInput label {{
    color: rgba(255,255,255,0.8) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px;
}}

section[data-testid="stSidebar"] .stRadio > div {{
    gap: 0.1rem;
}}

section[data-testid="stSidebar"] .stRadio > div > label {{
    background: rgba(255,255,255,0.05);
    border-radius: 6px;
    padding: 0.55rem 0.75rem !important;
    margin-bottom: 0.2rem;
    transition: background 0.15s ease;
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
}}

section[data-testid="stSidebar"] .stRadio > div > label:hover {{
    background: rgba(255,204,0,0.12);
    color: {COLOR_WHITE} !important;
}}

section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.1);
    margin: 1rem 0;
}}

/* ── Streamlit Tabs ──────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {COLOR_CARD_BG};
    border-radius: 8px 8px 0 0;
    border-bottom: 2px solid #E2E8F0;
    gap: 0;
    padding: 0 0.25rem;
}}

.stTabs [data-baseweb="tab"] {{
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.875rem;
    color: #64748B;
    padding: 0.75rem 1.25rem;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}}

.stTabs [aria-selected="true"] {{
    color: {COLOR_PRIMARY} !important;
    border-bottom-color: {COLOR_ACCENT} !important;
    background: transparent !important;
}}

.stTabs [data-baseweb="tab-panel"] {{
    background: {COLOR_CARD_BG};
    border-radius: 0 0 8px 8px;
    padding: 1.25rem;
    border: 1px solid #E2E8F0;
    border-top: none;
}}

/* ── Streamlit Metrics ───────────────────────────────────────── */
[data-testid="metric-container"] {{
    background: {COLOR_CARD_BG};
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}}

[data-testid="metric-container"] [data-testid="stMetricLabel"] {{
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: {COLOR_DARK_TEXT};
}}

/* ── Streamlit Buttons ───────────────────────────────────────── */
.stButton > button[kind="primary"] {{
    background: {COLOR_PRIMARY};
    color: {COLOR_WHITE};
    border: none;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.875rem;
    padding: 0.6rem 1.5rem;
    transition: background 0.2s ease, transform 0.1s ease;
}}

.stButton > button[kind="primary"]:hover {{
    background: #003A72;
    transform: translateY(-1px);
}}

.stButton > button:not([kind="primary"]) {{
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}}

/* ── Download buttons ────────────────────────────────────────── */
.stDownloadButton > button {{
    background: {COLOR_CARD_BG};
    color: {COLOR_PRIMARY};
    border: 1.5px solid {COLOR_PRIMARY};
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    transition: all 0.2s ease;
}}
.stDownloadButton > button:hover {{
    background: {COLOR_PRIMARY};
    color: {COLOR_WHITE};
}}

/* ── Dataframe / Tables ──────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
}}

/* ── Selectbox & Inputs ──────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] > div:first-child {{
    border-radius: 6px;
    border-color: #CBD5E0;
    font-size: 0.875rem;
}}

.stTextInput input {{
    border-radius: 6px;
    border-color: #CBD5E0;
    font-size: 0.875rem;
}}

/* ── Scrollbar ───────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: #F1F5F9; }}
::-webkit-scrollbar-thumb {{ background: #94A3B8; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {COLOR_PRIMARY}; }}

/* ── Info / Warning / Error boxes ───────────────────────────── */
.stAlert {{
    border-radius: 6px;
    font-size: 0.875rem;
}}
</style>
"""


def inject_brand():
    """Inject brand CSS into Streamlit app."""
    import streamlit as st
    st.markdown(BRAND_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str):
    """Render the dashboard header."""
    import streamlit as st
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>📦 {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str):
    """Render a section divider."""
    import streamlit as st
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
