"""
Page: Executive Overview — KPI cards, charts, and alerts.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.components.brand import render_header, render_section_header
from app.components.kpi_cards import render_kpi_cards, render_alerts
from app.components.charts import (
    chart_family_excess_cost, chart_family_zero_sales,
    chart_months_distribution, chart_risk_scatter,
)
from app.components.filters import apply_filters
from services.database import get_latest_snapshots, db_exists
from services.kpi_engine import calc_kpi_summary, add_risk_scores


def render_overview(filters: dict):
    render_header(
        "Resumen Ejecutivo",
        "Panel de control de inventario de lento movimiento y exceso"
    )

    if not db_exists():
        st.warning("⚠️ No hay datos cargados. Ve a **📤 Cargar Datos** para importar un archivo Excel.")
        return

    # Load data
    periodo = filters.get("periodo_meses", 6)
    df = get_latest_snapshots(periodo_meses=periodo)

    if df.empty:
        st.info(f"No hay datos para el período de {periodo} meses. Prueba con otro período.")
        return

    # Apply filters
    df = add_risk_scores(df)
    df_filtered = apply_filters(df, filters)

    # KPIs
    kpis = calc_kpi_summary(df_filtered)

    # Alerts
    render_alerts(kpis)

    # KPI Cards
    render_kpi_cards(kpis)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("Costo de Exceso por Familia")
        chart_family_excess_cost(df_filtered)

    with col2:
        render_section_header("Distribución Meses de Inventario")
        chart_months_distribution(df_filtered)

    col3, col4 = st.columns(2)

    with col3:
        render_section_header("Productos Sin Ventas por Familia")
        chart_family_zero_sales(df_filtered)

    with col4:
        render_section_header("Mapa de Riesgo")
        chart_risk_scatter(df_filtered)
