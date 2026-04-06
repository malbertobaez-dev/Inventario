"""
Streamlit Dashboard main entry point with Supabase Google authentication.
"""

from __future__ import annotations

import os
import sys

import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.components.brand import inject_brand, render_login_gate, render_topbar
from app.components.filters import render_filters
from services.auth import (
    build_google_oauth_url,
    get_auth_error,
    get_auth_user,
    handle_oauth_callback,
    is_supabase_ready,
    logout_user,
)
from services.database import db_exists, get_families, init_db


st.set_page_config(
    page_title="Inventario Slow Movement",
    page_icon="IC",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_brand()
handle_oauth_callback()

if not is_supabase_ready():
    st.error(
        "Supabase no esta configurado. Define SUPABASE_URL y SUPABASE_ANON_KEY en .env para activar el login con Google."
    )
    st.stop()

user = get_auth_user()
auth_url, auth_url_error = build_google_oauth_url()

if not user:
    render_login_gate(auth_url, auth_error=auth_url_error or get_auth_error())
    st.stop()

if render_topbar(user):
    logout_user()
    st.rerun()

# Initialize DB only for authenticated users
init_db()

PAGES = {
    "Overview": "overview",
    "Cargar Datos": "upload",
    "Rankings": "rankings",
    "Tendencias": "trends",
    "Explorador": "data_explorer",
}

st.sidebar.markdown(
    f"""
    <div style='padding:0.5rem 0 1rem 0; border-bottom:1px solid #e5e7eb; margin-bottom:0.75rem;'>
        <div style='font-family:Montserrat, sans-serif; font-size:1.25rem; font-weight:900; color:#001836; line-height:1.1;'>
            Inventory<br/>Control
        </div>
        <div style='font-size:0.63rem; color:#6b7280; margin-top:0.2rem; letter-spacing:0.18em; text-transform:uppercase;'>
            Precision Logistics
        </div>
        <div class='user-chip' style='margin-top:0.6rem;'>
            {user.get("email", "usuario")}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_page = st.sidebar.radio(
    "Navegacion",
    options=list(PAGES.keys()),
    label_visibility="collapsed",
)

if st.sidebar.button("Sign Out", key="sidebar_logout", use_container_width=True):
    logout_user()
    st.rerun()

page_key = PAGES[selected_page]

families = get_families() if db_exists() else []
filters = {}
if page_key in ("overview", "rankings", "data_explorer"):
    filters = render_filters(families)

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
