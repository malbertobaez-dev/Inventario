"""
Page: Trends — Weekly excess evolution and period-over-period comparison.
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.components.brand import render_header, render_section_header
from app.components.charts import chart_excess_trend
from services.database import get_excess_weekly, get_snapshots, db_exists
from services.kpi_engine import excess_trend


def render_trends():
    render_header(
        "Tendencias",
        "Evolución semanal del exceso y comparación entre períodos"
    )

    if not db_exists():
        st.warning("⚠️ No hay datos cargados.")
        return

    # ── Weekly Excess Trend ────────────────────────────────────────
    render_section_header("Evolución Semanal del Exceso")

    excess_df = get_excess_weekly()
    if excess_df.empty:
        st.info(
            "No hay datos de tendencia semanal. "
            "Carga un archivo con la hoja '6 Meses' que contenga columnas 'Inv Exce al...' "
            "para ver esta visualización."
        )
    else:
        trend = excess_trend(excess_df)

        if not trend.empty:
            chart_excess_trend(trend)

            # Summary metrics
            if len(trend) >= 2:
                latest = trend.iloc[-1]
                prev = trend.iloc[-2]

                col1, col2, col3 = st.columns(3)
                with col1:
                    cost_change = latest["cambio_costo"]
                    delta_color = "inverse" if cost_change and cost_change > 0 else "normal"
                    st.metric(
                        "Costo Exceso Último Corte",
                        f"${latest['total_costo_exceso']:,.0f}",
                        delta=f"{cost_change:+.1f}%" if cost_change and cost_change == cost_change else None,
                        delta_color=delta_color,
                    )
                with col2:
                    inv_change = latest["cambio_inv"]
                    delta_color = "inverse" if inv_change and inv_change > 0 else "normal"
                    st.metric(
                        "Inventario Exceso Último Corte",
                        f"{latest['total_inv_exceso']:,.0f}",
                        delta=f"{inv_change:+.1f}%" if inv_change and inv_change == inv_change else None,
                        delta_color=delta_color,
                    )
                with col3:
                    st.metric(
                        "Productos con Exceso",
                        f"{int(latest['product_count']):,}"
                    )

            # Table
            render_section_header("Detalle Semanal")
            display = trend[["snapshot_date", "total_inv_exceso", "total_costo_exceso",
                             "product_count", "cambio_costo"]].copy()
            display.columns = ["Fecha", "Inv Exceso", "Costo Exceso", "Productos", "Cambio %"]
            st.dataframe(display, use_container_width=True, hide_index=True)

    # ── Period Comparison ──────────────────────────────────────────
    render_section_header("Comparación 6 Meses vs 12 Meses")

    df_6m = get_snapshots(periodo_meses=6)
    df_12m = get_snapshots(periodo_meses=12)

    if df_6m.empty and df_12m.empty:
        st.info("Carga datos de ambos períodos (6 y 12 meses) para ver la comparación.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Período 6 Meses**")
            if not df_6m.empty:
                _period_metrics(df_6m)
            else:
                st.info("Sin datos de 6 meses")

        with col2:
            st.markdown("**Período 12 Meses**")
            if not df_12m.empty:
                _period_metrics(df_12m)
            else:
                st.info("Sin datos de 12 meses")


def _period_metrics(df):
    """Render quick metrics for a period."""
    total_products = len(df)
    total_excess = df["costo_exceso_mn"].sum() if "costo_exceso_mn" in df.columns else 0
    zero_sales = len(df[df["ventas_periodo"].fillna(0) == 0]) if "ventas_periodo" in df.columns else 0
    median_months = df["meses_inventario"].median() if "meses_inventario" in df.columns else 0

    st.metric("Productos", f"{total_products:,}")
    st.metric("Costo Exceso Total", f"${total_excess:,.0f}")
    st.metric("Sin Ventas", f"{zero_sales} ({zero_sales/total_products*100:.0f}%)" if total_products > 0 else "0")
    st.metric("Mediana Meses Inv", f"{median_months:.1f}" if median_months else "N/D")
