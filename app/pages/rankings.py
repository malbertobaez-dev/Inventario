"""
Page: Rankings — Top products by risk, excess cost, and months of inventory.
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.components.brand import render_header, render_section_header
from app.components.charts import chart_top_products_bar
from app.components.filters import apply_filters
from services.database import get_latest_snapshots, db_exists
from services.kpi_engine import (
    add_risk_scores, top_products_by_risk,
    top_products_by_excess_cost, top_products_by_months,
    family_summary,
)


def _format_currency_col(df, col):
    """Format a column as currency for display."""
    if col in df.columns:
        df[col] = df[col].apply(lambda x: f"${x:,.0f}" if x and not (isinstance(x, float) and x != x) else "$0")
    return df


def render_rankings(filters: dict):
    render_header(
        "Rankings de Productos",
        "Productos prioritarios para acción de inventario"
    )

    if not db_exists():
        st.warning("⚠️ No hay datos cargados.")
        return

    periodo = filters.get("periodo_meses", 6)
    df = get_latest_snapshots(periodo_meses=periodo)

    if df.empty:
        st.info("No hay datos para este período.")
        return

    df = add_risk_scores(df)
    df = apply_filters(df, filters)

    # Tab layout
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Mayor Riesgo",
        "💰 Mayor Costo Exceso",
        "📅 Mayor Cobertura",
        "👨‍👩‍👧‍👦 Por Familia",
    ])

    n = st.sidebar.number_input("Top N productos", min_value=5, max_value=50, value=20, step=5)

    with tab1:
        render_section_header(f"Top {n} Productos por Score de Riesgo")
        top_risk = top_products_by_risk(df, n=n)
        if not top_risk.empty:
            chart_top_products_bar(top_risk, "risk_score", "Score de Riesgo", n=n)
            st.dataframe(
                top_risk,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "risk_score": st.column_config.ProgressColumn(
                        "Riesgo", min_value=0, max_value=100, format="%.0f",
                    ),
                },
            )
        else:
            st.info("Sin datos")

    with tab2:
        render_section_header(f"Top {n} Productos por Costo de Exceso")
        top_cost = top_products_by_excess_cost(df, n=n)
        if not top_cost.empty:
            chart_top_products_bar(top_cost, "costo_exceso_mn", "Costo Exceso (MXN)", n=n)
            st.dataframe(top_cost, use_container_width=True, hide_index=True)
        else:
            st.info("Sin datos")

    with tab3:
        render_section_header(f"Top {n} Productos por Meses de Inventario")
        top_months = top_products_by_months(df, n=n)
        if not top_months.empty:
            chart_top_products_bar(top_months, "meses_inventario", "Meses de Inventario", n=n)
            st.dataframe(top_months, use_container_width=True, hide_index=True)
        else:
            st.info("Sin datos")

    with tab4:
        render_section_header("Resumen por Familia")
        fam = family_summary(df)
        if not fam.empty:
            st.dataframe(
                fam,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "cse_prod": st.column_config.TextColumn("Familia"),
                    "productos": st.column_config.NumberColumn("Productos"),
                    "total_existencia": st.column_config.NumberColumn("Existencia Total"),
                    "total_exceso": st.column_config.NumberColumn("Exceso Total"),
                    "costo_exceso_total": st.column_config.NumberColumn("Costo Exceso", format="$%,.0f"),
                    "mediana_meses_inv": st.column_config.NumberColumn("Mediana Meses Inv", format="%.1f"),
                    "pct_zero_sales": st.column_config.ProgressColumn(
                        "% Sin Ventas", min_value=0, max_value=100, format="%.0f%%",
                    ),
                },
            )
        else:
            st.info("Sin datos")
