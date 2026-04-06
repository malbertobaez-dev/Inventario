"""
Streamlit Dashboard — Main Entry Point with Multi-Page Navigation.
"""
import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.components.brand import inject_brand, render_header
from app.components.filters import render_filters
from services.database import init_db, db_exists, get_families

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inventario Slow Movement",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize DB
init_db()

# Inject brand CSS
inject_brand()

# ── Navigation ─────────────────────────────────────────────────────
PAGES = {
    "📊 Resumen Ejecutivo": "overview",
    "📤 Cargar Datos": "upload",
    "🏆 Rankings": "rankings",
    "📈 Tendencias": "trends",
    "📋 Explorador de Datos": "data_explorer",
}

st.sidebar.markdown(
    "<h2 style='color:#FFCC00; font-weight:800; margin-bottom:0.5rem;'>⚡ Inventario</h2>",
    unsafe_allow_html=True,
)

selected_page = st.sidebar.radio(
    "Navegación",
    options=list(PAGES.keys()),
    label_visibility="collapsed",
)

page_key = PAGES[selected_page]

# ── Filters (only on analytics pages) ─────────────────────────────
families = get_families() if db_exists() else []
filters = {}
if page_key in ("overview", "rankings", "data_explorer"):
    filters = render_filters(families)

# ── Route to Page ──────────────────────────────────────────────────
if page_key == "overview":
    from app.pages.overview import render_overview
    render_overview(filters)

elif page_key == "upload":
    from app.pages.upload import render_upload

    render_upload()

elif page_key == "rankings":
    from app.pages.rankings import render_rankings
    render_rankings(filters)

elif page_key == "trends":
    from app.pages.trends import render_trends
    render_trends()

elif page_key == "data_explorer":
    from app.pages.data_explorer import render_data_explorer
    render_data_explorer(filters)
