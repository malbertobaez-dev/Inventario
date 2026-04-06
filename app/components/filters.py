"""
Sidebar filters: period, family, search and risk threshold.
"""
import streamlit as st

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import TIME_WINDOWS


def render_filters(families: list) -> dict:
    st.sidebar.markdown(
        "<div style='color:#9FDFFF; font-size:0.74rem; font-weight:800; "
        "letter-spacing:2px; text-transform:uppercase; margin-bottom:0.45rem;'>Filter Parameters</div>",
        unsafe_allow_html=True,
    )

    window_label = st.sidebar.selectbox(
        "Periodo de analisis",
        options=list(TIME_WINDOWS.keys()),
        index=2,
    )
    periodo_meses = TIME_WINDOWS[window_label]

    family_options = ["Todas las familias"] + sorted(families)
    selected_family = st.sidebar.selectbox(
        "Familia de producto",
        options=family_options,
    )
    family = None if selected_family == "Todas las familias" else selected_family

    search = st.sidebar.text_input(
        "Buscar producto",
        placeholder="Codigo o descripcion...",
    )

    min_risk = st.sidebar.slider(
        "Score de riesgo minimo",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div style='font-size:0.68rem; color:rgba(148,163,184,0.85); text-align:center; margin-top:0.45rem;'>"
        "Sentinel Inventory v2</div>",
        unsafe_allow_html=True,
    )

    return {
        "periodo_meses": periodo_meses,
        "family": family,
        "search": search,
        "min_risk": min_risk,
    }


def apply_filters(df, filters: dict):
    import pandas as pd

    if df.empty:
        return df

    result = df.copy()

    if filters.get("family"):
        result = result[result["cse_prod"] == filters["family"]]

    search = filters.get("search", "").strip()
    if search:
        mask = (
            result["cve_prod"].astype(str).str.contains(search, case=False, na=False)
            | result.get("desc_prod", pd.Series(dtype=str)).astype(str).str.contains(search, case=False, na=False)
        )
        result = result[mask]

    min_risk = filters.get("min_risk", 0)
    if min_risk > 0 and "risk_score" in result.columns:
        result = result[result["risk_score"] >= min_risk]

    return result
