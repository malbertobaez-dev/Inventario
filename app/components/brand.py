"""
Brand styling and shared UI helpers for Streamlit.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import (
    COLOR_ACCENT,
    COLOR_BG_MAIN,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_DARK_TEXT,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_WHITE,
)


BRAND_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

.stApp {{
    font-family: 'Inter', sans-serif;
    background: {COLOR_BG_MAIN};
    color: {COLOR_DARK_TEXT};
}}

.main .block-container {{
    max-width: 1500px;
    padding-top: 1rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}}

section[data-testid="stSidebar"] {{
    background: #f6f7f9;
    border-right: 1px solid #d9dde3;
}}

section[data-testid="stSidebar"] > div {{
    padding-top: 0.6rem;
}}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p {{
    color: #1f2937;
}}

section[data-testid="stSidebar"] .stRadio > div > label {{
    background: transparent;
    border-radius: 6px;
    padding: 0.55rem 0.75rem !important;
    margin-bottom: 0.1rem;
    color: #111827 !important;
    transition: all 0.15s ease;
}}

section[data-testid="stSidebar"] .stRadio > div > label:hover {{
    background: #ffffff;
    border: 1px solid #e5e7eb;
}}

section[data-testid="stSidebar"] .stButton > button {{
    border-radius: 8px;
    border: 1px solid #ef4444;
    color: #ef4444;
    background: #fff;
    font-weight: 600;
}}

.topbar-shell {{
    background: #ffffff;
    border: 1px solid #dce2ea;
    border-radius: 14px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}}

.topbar-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    color: #001836;
    margin: 0;
}}

.topbar-sub {{
    font-size: 0.72rem;
    color: #6b7280;
    margin-top: 0.15rem;
}}

.dashboard-header {{
    background: #ffffff;
    border: 1px solid #dce2ea;
    border-left: 4px solid {COLOR_PRIMARY};
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}}

.dashboard-header h1 {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    margin: 0;
    color: #0b1f42;
}}

.dashboard-header p {{
    font-size: 0.8rem;
    color: #64748b;
    margin: 0.3rem 0 0 0;
}}

.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0.9rem;
    margin-bottom: 1.25rem;
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
    padding: 1rem;
    border: 1px solid #e6e9ee;
    border-left: 3px solid #cbd5e1;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}}

.kpi-card.green {{ border-left-color: {COLOR_SUCCESS}; }}
.kpi-card.yellow {{ border-left-color: {COLOR_WARNING}; }}
.kpi-card.red {{ border-left-color: {COLOR_DANGER}; }}
.kpi-card.gray {{ border-left-color: #9ca3af; }}

.kpi-dot {{
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 999px;
    margin-right: 0.35rem;
}}

.kpi-dot.green {{ background: {COLOR_SUCCESS}; }}
.kpi-dot.yellow {{ background: {COLOR_WARNING}; }}
.kpi-dot.red {{ background: {COLOR_DANGER}; }}
.kpi-dot.gray {{ background: #9ca3af; }}

.kpi-label {{
    font-size: 0.63rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}}

.kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #0b1f42;
    line-height: 1.1;
}}

.kpi-sub {{
    font-size: 0.7rem;
    color: #64748b;
    margin-top: 0.3rem;
}}

.section-header {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.95rem;
    font-weight: 800;
    color: #07234a;
    margin: 1rem 0 0.7rem 0;
    padding-bottom: 0.45rem;
    border-bottom: 2px solid #e5e7eb;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}

.alert-banner {{
    padding: 0.65rem 0.9rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
    font-weight: 500;
    border-left: 4px solid transparent;
}}

.alert-banner.danger {{
    background: #fff5f5;
    border-left-color: {COLOR_DANGER};
    color: #991b1b;
}}

.alert-banner.warning {{
    background: #fffbeb;
    border-left-color: {COLOR_WARNING};
    color: #78350f;
}}

.alert-banner.success {{
    background: #f0fdf4;
    border-left-color: {COLOR_SUCCESS};
    color: #14532d;
}}

.upload-zone {{
    border: 1px dashed #93c5fd;
    border-radius: 10px;
    padding: 1.8rem;
    text-align: center;
    background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 100%);
    margin: 0.8rem 0 1rem 0;
}}

[data-testid="stDataFrame"] {{
    border-radius: 10px;
    border: 1px solid #e5e7eb;
}}

.stButton > button[kind="primary"] {{
    background: {COLOR_SECONDARY};
    color: {COLOR_WHITE};
    border: none;
    border-radius: 8px;
    font-weight: 700;
}}

.stButton > button[kind="primary"]:hover {{
    background: #005ad0;
}}

.login-shell {{
    max-width: 520px;
    margin: 6rem auto 0 auto;
    background: #ffffff;
    border: 1px solid #dce2ea;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 12px 36px rgba(0, 24, 54, 0.08);
}}

.login-title {{
    font-family: 'Montserrat', sans-serif;
    color: #001836;
    font-size: 1.6rem;
    margin: 0;
}}

.login-sub {{
    color: #6b7280;
    margin-top: 0.45rem;
    margin-bottom: 1.1rem;
    font-size: 0.92rem;
}}

.user-chip {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: #eef4ff;
    color: #0b1f42;
    border: 1px solid #dbeafe;
    border-radius: 999px;
    padding: 0.25rem 0.55rem;
    font-size: 0.72rem;
    font-weight: 600;
}}

.user-avatar-fallback {{
    width: 32px;
    height: 32px;
    border-radius: 999px;
    background: #002d5a;
    color: #fff;
    font-size: 0.74rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #e5e7eb;
}}
</style>
"""


def inject_brand() -> None:
    st.markdown(BRAND_CSS, unsafe_allow_html=True)


def render_login_gate(auth_url: Optional[str], auth_error: Optional[str] = None) -> None:
    st.markdown(
        """
        <div class="login-shell">
            <h1 class="login-title">Inventory Control</h1>
            <p class="login-sub">Inicia sesion con Google para acceder al dashboard de inventario.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if auth_error:
        st.error(auth_error)

    if auth_url:
        st.link_button("Entrar con Google", auth_url, use_container_width=True)
    else:
        st.error("No se pudo construir la URL de autenticacion de Supabase.")


def _user_initial(user: Dict[str, Any]) -> str:
    name = (user.get("name") or user.get("email") or "U").strip()
    return name[:1].upper() if name else "U"


def render_topbar(user: Dict[str, Any]) -> bool:
    now_label = datetime.now().strftime("%d %b %Y, %H:%M")

    st.markdown('<div class="topbar-shell">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([6.5, 1.8, 1.7])

    with col1:
        st.markdown('<p class="topbar-title">Sentinel Risk Advisor</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="topbar-sub">Ultima sincronizacion: {now_label}</p>', unsafe_allow_html=True)

    with col2:
        logout = st.button("Cerrar sesion", key="top_logout", use_container_width=True)

    with col3:
        avatar = user.get("avatar_url")
        if avatar:
            st.image(avatar, width=34)
        else:
            st.markdown(
                f'<div class="user-avatar-fallback">{_user_initial(user)}</div>',
                unsafe_allow_html=True,
            )
        label = user.get("name") or user.get("email") or "Usuario"
        st.caption(label)

    st.markdown('</div>', unsafe_allow_html=True)
    return logout


def render_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="dashboard-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
