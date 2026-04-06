"""
Brand styling — CSS injection and theme constants for Streamlit.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT,
    COLOR_NEUTRAL, COLOR_WHITE, COLOR_DARK_TEXT,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
)


BRAND_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ─────────────────────────────────────────────────── */
.stApp {{
    font-family: 'Inter', sans-serif;
}}

.main .block-container {{
    max-width: 1280px;
    padding-top: 1rem;
}}

/* ── Header ─────────────────────────────────────────────────── */
.dashboard-header {{
    background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, #004B8D 100%);
    color: {COLOR_WHITE};
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,45,90,0.3);
}}

.dashboard-header h1 {{
    font-size: 1.8rem;
    font-weight: 800;
    margin: 0 0 0.25rem 0;
    letter-spacing: -0.5px;
}}

.dashboard-header p {{
    font-size: 0.95rem;
    opacity: 0.85;
    margin: 0;
    font-weight: 300;
}}

/* ── KPI Cards ──────────────────────────────────────────────── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}}

.kpi-card {{
    background: {COLOR_WHITE};
    border-radius: 12px;
    padding: 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 4px solid transparent;
    transition: all 0.2s ease;
}}

.kpi-card:hover {{
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}}

.kpi-card .kpi-label {{
    font-size: 0.78rem;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.4rem;
}}

.kpi-card .kpi-value {{
    font-size: 1.6rem;
    font-weight: 700;
    color: {COLOR_DARK_TEXT};
    line-height: 1.1;
}}

.kpi-card .kpi-sub {{
    font-size: 0.75rem;
    color: #999;
    margin-top: 0.3rem;
}}

.kpi-card.green  {{ border-left-color: {COLOR_SUCCESS}; }}
.kpi-card.yellow {{ border-left-color: {COLOR_WARNING}; }}
.kpi-card.red    {{ border-left-color: {COLOR_DANGER}; }}
.kpi-card.gray   {{ border-left-color: #ccc; }}

/* ── Section Headers ────────────────────────────────────────── */
.section-header {{
    font-size: 1.15rem;
    font-weight: 700;
    color: {COLOR_PRIMARY};
    margin: 1.5rem 0 0.75rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid {COLOR_ACCENT};
}}

/* ── Tables ─────────────────────────────────────────────────── */
.ranking-table {{
    font-size: 0.85rem;
}}

/* ── Upload area ────────────────────────────────────────────── */
.upload-zone {{
    border: 2px dashed {COLOR_SECONDARY};
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    background: #f8faff;
    margin: 1rem 0;
}}

/* ── Alerts ─────────────────────────────────────────────────── */
.alert-banner {{
    padding: 0.8rem 1.2rem;
    border-radius: 8px;
    margin-bottom: 0.8rem;
    font-size: 0.9rem;
    font-weight: 500;
}}

.alert-banner.danger {{
    background: #fff5f5;
    border: 1px solid #DC3545;
    color: #DC3545;
}}

.alert-banner.warning {{
    background: #fffdf0;
    border: 1px solid #FFC107;
    color: #856404;
}}

.alert-banner.success {{
    background: #f0fff4;
    border: 1px solid #28A745;
    color: #28A745;
}}

/* ── Sidebar ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {COLOR_PRIMARY} 0%, #001F3F 100%);
}}

section[data-testid="stSidebar"] .stMarkdown {{
    color: {COLOR_WHITE};
}}

section[data-testid="stSidebar"] label {{
    color: rgba(255,255,255,0.8) !important;
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
        <h1>⚡ {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str):
    """Render a section divider."""
    import streamlit as st
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
