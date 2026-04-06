"""
Sidebar Filters — Time window, family, and product search.
"""
import streamlit as st

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import TIME_WINDOWS


def render_filters(families: list) -> dict:
    """
    Render sidebar filters and return selected values.
    """
    st.sidebar.markdown("### 🔍 Filtros")

    # Time window
    window_label = st.sidebar.selectbox(
        "Período de análisis",
        options=list(TIME_WINDOWS.keys()),
        index=2,  # Default: 6 Meses
    )
    periodo_meses = TIME_WINDOWS[window_label]

    # Family filter
    family_options = ["Todas las familias"] + sorted(families)
    selected_family = st.sidebar.selectbox(
        "Familia de producto",
        options=family_options,
    )
    family = None if selected_family == "Todas las familias" else selected_family

    # Product search
    search = st.sidebar.text_input(
        "Buscar producto",
        placeholder="Código o descripción...",
    )

    # Risk filter
    min_risk = st.sidebar.slider(
        "Score de riesgo mínimo",
        min_value=0, max_value=100, value=0, step=5,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='font-size:0.75rem; opacity:0.6; text-align:center;'>"
        f"Inventario Slow Movement v1.0</div>",
        unsafe_allow_html=True,
    )

    return {
        "periodo_meses": periodo_meses,
        "family": family,
        "search": search,
        "min_risk": min_risk,
    }


def apply_filters(df, filters: dict):
    """Apply filters to a DataFrame."""
    import pandas as pd

    if df.empty:
        return df

    result = df.copy()

    # Family filter
    if filters.get("family"):
        result = result[result["cse_prod"] == filters["family"]]

    # Search filter
    search = filters.get("search", "").strip()
    if search:
        mask = (
            result["cve_prod"].astype(str).str.contains(search, case=False, na=False) |
            result.get("desc_prod", pd.Series(dtype=str)).astype(str).str.contains(search, case=False, na=False)
        )
        result = result[mask]

    # Risk score filter
    min_risk = filters.get("min_risk", 0)
    if min_risk > 0 and "risk_score" in result.columns:
        result = result[result["risk_score"] >= min_risk]

    return result
