"""
Brand styling and shared UI helpers for Streamlit.
"""

from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st


BRAND_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@300;400;500;600;700&family=Montserrat:wght@700;800;900&display=swap');

:root {
  --surface:#0d0f12;
  --surface-2:#0f141b;
  --panel:#161b22;
  --panel-soft:#121822;
  --outline:#2b3440;
  --text:#f1f5f9;
  --muted:#93a2b8;
  --cyan:#38bdf8;
  --red:#f87171;
  --amber:#fbbf24;
  --green:#34d399;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.stApp {
  font-family: 'Inter', sans-serif;
  background:
    radial-gradient(1200px 500px at 70% -20%, rgba(56,189,248,0.12), transparent 60%),
    radial-gradient(900px 380px at 20% -10%, rgba(99,102,241,0.08), transparent 60%),
    var(--surface);
  color: var(--text);
}

.main .block-container {
  max-width: 1600px;
  padding-top: 1rem;
  padding-left: 1.2rem;
  padding-right: 1.2rem;
  padding-bottom: 1.5rem;
}

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b111a 0%, #0c131d 100%);
  border-right: 1px solid rgba(48, 63, 79, 0.85);
}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
  display: none;
}

section[data-testid="stSidebar"] > div {
  padding-top: 0.6rem;
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption {
  color: #d5deea !important;
}

section[data-testid="stSidebar"] .stRadio > div > label {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 0.55rem 0.75rem !important;
  margin-bottom: 0.12rem;
  color: #d8e4f2 !important;
  transition: all 0.15s ease;
}

section[data-testid="stSidebar"] .stRadio > div > label:hover {
  background: rgba(56, 189, 248, 0.08);
  border-color: rgba(56, 189, 248, 0.25);
}

section[data-testid="stSidebar"] .stButton > button {
  border-radius: 9px;
  border: 1px solid rgba(248, 113, 113, 0.45);
  color: #fda4a4;
  background: rgba(248, 113, 113, 0.08);
  font-weight: 600;
}

.topbar-shell {
  background: rgba(10, 13, 18, 0.88);
  border: 1px solid rgba(48, 63, 79, 0.8);
  border-radius: 14px;
  padding: 0.55rem 0.85rem;
  margin-bottom: 0.9rem;
  backdrop-filter: blur(6px);
}

.brand-lockup-title {
  margin: 0;
  font-family: 'Montserrat', sans-serif;
  font-size: 0.9rem;
  line-height: 1;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #f5f9ff;
}

.brand-lockup-sub {
  margin-top: 0.18rem;
  font-size: 0.58rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #6f8097;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: #98a7ba;
  white-space: nowrap;
}

.top-nav .active {
  color: #e8f5ff;
  border-bottom: 2px solid var(--cyan);
  padding-bottom: 0.2rem;
}

.top-nav .item {
  padding-bottom: 0.2rem;
}

.sync-meta {
  text-align: right;
  font-size: 0.67rem;
  color: #90a4bd;
}

.sync-meta .value {
  color: #41d89f;
  font-weight: 600;
}

.top-action-btn button {
  width: 100%;
  background: rgba(56, 189, 248, 0.14);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #bdeaff;
  border-radius: 9px;
  font-size: 0.75rem;
}

.dashboard-header {
  background: linear-gradient(120deg, rgba(19,25,33,0.95), rgba(15,21,31,0.95));
  border: 1px solid rgba(48,63,79,0.65);
  border-radius: 14px;
  padding: 1.1rem 1.2rem;
  margin-bottom: 0.9rem;
}

.dashboard-header h1 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.05rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.06;
  letter-spacing: 0.01em;
  color: #f8fbff;
}

.dashboard-header p {
  margin: 0.28rem 0 0 0;
  color: var(--muted);
  font-size: 0.93rem;
  max-width: 980px;
}

.section-header {
  font-family: 'Montserrat', sans-serif;
  font-size: 0.79rem;
  font-weight: 800;
  color: #dce7f6;
  margin: 0.95rem 0 0.62rem 0;
  padding-bottom: 0.45rem;
  border-bottom: 1px solid rgba(48, 63, 79, 0.55);
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.exec-card {
  background: linear-gradient(180deg, rgba(24,31,40,0.55) 0%, rgba(22,27,34,1) 100%);
  border: 1px solid rgba(48,63,79,0.55);
  border-radius: 12px;
  box-shadow: 0 16px 35px rgba(0, 0, 0, 0.28);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.85rem;
  margin-bottom: 1rem;
}

@media (max-width: 1240px) {
  .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 760px) {
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

.kpi-card {
  background: linear-gradient(180deg, rgba(23,30,39,0.95), rgba(16,22,31,0.98));
  border: 1px solid rgba(48,63,79,0.58);
  border-radius: 12px;
  padding: 0.92rem 0.96rem;
  position: relative;
}

.kpi-card::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 100%;
  border-radius: 12px 0 0 12px;
  background: #516175;
}

.kpi-card.green::after { background: var(--green); }
.kpi-card.yellow::after { background: var(--amber); }
.kpi-card.red::after { background: var(--red); }
.kpi-card.gray::after { background: #64748b; }

.kpi-label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #8395ac;
  font-weight: 700;
  margin-bottom: 0.44rem;
}

.kpi-value {
  font-family: 'Montserrat', sans-serif;
  font-size: 1.68rem;
  font-weight: 800;
  color: #f8fbff;
  letter-spacing: -0.02em;
  line-height: 1;
}

.kpi-sub {
  color: #96a8bf;
  font-size: 0.71rem;
  margin-top: 0.36rem;
}

.alert-banner {
  padding: 0.7rem 0.88rem;
  border-radius: 10px;
  margin-bottom: 0.48rem;
  font-size: 0.79rem;
  border: 1px solid transparent;
}

.alert-banner.danger {
  background: rgba(248, 113, 113, 0.1);
  border-color: rgba(248, 113, 113, 0.35);
  color: #fecaca;
}

.alert-banner.warning {
  background: rgba(251, 191, 36, 0.1);
  border-color: rgba(251, 191, 36, 0.32);
  color: #fde68a;
}

.alert-banner.success {
  background: rgba(52, 211, 153, 0.1);
  border-color: rgba(52, 211, 153, 0.3);
  color: #a7f3d0;
}

.upload-zone {
  border: 1px dashed rgba(56, 189, 248, 0.45);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  background: linear-gradient(180deg, rgba(56,189,248,0.08), rgba(18,24,34,0.35));
  margin: 0.8rem 0 1rem 0;
}

[data-testid="stDataFrame"] {
  border-radius: 12px;
  border: 1px solid rgba(48,63,79,0.58);
  overflow: hidden;
}

[data-testid="metric-container"] {
  background: linear-gradient(180deg, rgba(24,31,40,0.8), rgba(18,24,34,0.95));
  border: 1px solid rgba(48,63,79,0.58);
  border-radius: 12px;
  padding: 0.8rem;
}

.stButton > button[kind="primary"] {
  background: #38bdf8;
  color: #07101a;
  border: none;
  border-radius: 10px;
  font-weight: 800;
}

.stButton > button[kind="primary"]:hover {
  filter: brightness(1.05);
}

.stTextInput input,
.stSelectbox [data-baseweb="select"] > div:first-child,
.stMultiSelect [data-baseweb="select"] > div:first-child {
  background: rgba(17,24,34,0.9);
  border-color: rgba(57,70,86,0.9) !important;
  color: #e7eef9;
  border-radius: 9px;
}

.stSlider [data-baseweb="slider"] {
  margin-top: 0.2rem;
}

.login-shell {
  max-width: 560px;
  margin: 7rem auto 0 auto;
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0.5rem 0;
  box-shadow: none;
}

.login-logo-wrap {
  width: 100%;
  min-height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-company-logo {
  max-width: 360px;
  width: 100%;
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 10px 20px rgba(0,0,0,.35));
}

.login-title {
  font-family: 'Montserrat', sans-serif;
  color: #f8fbff;
  font-size: 1.45rem;
  margin: 0;
  letter-spacing: 0.03em;
}

.login-sub {
  color: #9cb0c8;
  margin-top: 0.45rem;
  margin-bottom: 1.15rem;
  font-size: 0.92rem;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(56, 189, 248, 0.12);
  color: #bde9ff;
  border: 1px solid rgba(56, 189, 248, 0.36);
  border-radius: 999px;
  padding: 0.26rem 0.55rem;
  font-size: 0.7rem;
  font-weight: 600;
}

.user-avatar-fallback {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: #0f1f33;
  color: #e2eefc;
  font-size: 0.76rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(71, 85, 105, 0.95);
}

.small-muted {
  color: #8ea1bb;
  font-size: 0.68rem;
}
</style>
"""


def inject_brand() -> None:
    st.markdown(BRAND_CSS, unsafe_allow_html=True)


def _find_login_logo_path() -> Optional[Path]:
    base_dir = Path(__file__).resolve().parents[2]
    candidates = [
        base_dir / "assets" / "Battery_Depot_LogoBlanco.png",
        base_dir / "Battery_Depot_LogoBlanco.png",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _image_to_data_uri(image_path: Path) -> str:
    suffix = image_path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_login_gate(auth_url: Optional[str], auth_error: Optional[str] = None) -> None:
    logo_path = _find_login_logo_path()
    logo_html = ""
    if logo_path is not None:
        logo_src = _image_to_data_uri(logo_path)
        logo_html = f"<img src='{logo_src}' alt='Company logo' class='login-company-logo'/>"
    else:
        logo_html = (
            "<div>"
            "<h1 class='login-title'>SENTINEL INVENTORY</h1>"
            "<p class='login-sub'>Coloca tu logo en <code>assets/Battery_Depot_LogoBlanco.png</code>.</p>"
            "</div>"
        )

    st.markdown(
        f"""
        <div class="login-shell">
            <div class="login-logo-wrap">{logo_html}</div>
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


def render_topbar(user: Dict[str, Any], active_page: str = "Overview") -> bool:
    now_label = datetime.now().strftime("%d %b %Y, %H:%M")

    nav_items = ["Overview", "Risk Analytics", "Optimization", "Reports"]
    nav_html = "".join(
        f"<span class='{'active' if item == active_page else 'item'}'>{item}</span>"
        for item in nav_items
    )

    st.markdown('<div class="topbar-shell">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([2.2, 3.8, 1.7, 1.2, 1.1])

    with col1:
        st.markdown(
            """
            <div style='display:flex; gap:0.55rem; align-items:center;'>
                <div style='width:34px;height:34px;border-radius:9px;border:1px solid rgba(56,189,248,.35);background:rgba(56,189,248,.08);display:flex;align-items:center;justify-content:center;color:#7cd7ff;'>
                    &#128737;
                </div>
                <div>
                    <p class='brand-lockup-title'>Sentinel</p>
                    <p class='brand-lockup-sub'>Executive Command</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(f"<div class='top-nav'>{nav_html}</div>", unsafe_allow_html=True)

    with col3:
        st.markdown(
            f"<div class='sync-meta'>Last Sync<br><span class='value'>{now_label}</span></div>",
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown('<div class="top-action-btn">', unsafe_allow_html=True)
        logout = st.button("Cerrar sesion", key="top_logout", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        avatar = user.get("avatar_url")
        if avatar:
            st.image(avatar, width=34)
        else:
            st.markdown(
                f'<div class="user-avatar-fallback">{_user_initial(user)}</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<div class='small-muted'>{(user.get('name') or user.get('email') or 'Usuario')[:18]}</div>",
            unsafe_allow_html=True,
        )

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
