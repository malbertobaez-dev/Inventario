"""
Page: Data Explorer — Full data table with filters and CSV export.
"""
import streamlit as st
import io
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.components.brand import render_header, render_section_header
from app.components.filters import apply_filters
from services.database import get_latest_snapshots, db_exists
from services.kpi_engine import add_risk_scores


def render_data_explorer(filters: dict):
    render_header(
        "Explorador de Datos",
        "Consulta y exporta datos detallados de inventario"
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

    # Summary bar
    col1, col2, col3 = st.columns(3)
    col1.metric("Registros", f"{len(df):,}")
    col2.metric("Familias", f"{df['cse_prod'].nunique():,}" if "cse_prod" in df.columns else "N/D")
    col3.metric("Costo Exceso Filtrado", f"${df['costo_exceso_mn'].sum():,.0f}" if "costo_exceso_mn" in df.columns else "$0")

    # Column selector
    render_section_header("Datos")

    default_cols = [
        "cve_prod", "cse_prod", "desc_prod", "existencia", "exceso",
        "cosprom", "costo_exceso_mn", "meses_inventario",
        "ventas_periodo", "prom_venta_mensual", "risk_score",
    ]
    available_cols = [c for c in default_cols if c in df.columns]
    all_cols = df.columns.tolist()

    selected_cols = st.multiselect(
        "Columnas visibles",
        options=all_cols,
        default=available_cols,
    )

    if not selected_cols:
        selected_cols = available_cols

    # Sort controls
    sort_col = st.selectbox("Ordenar por", options=selected_cols, index=len(selected_cols) - 1)
    sort_asc = st.checkbox("Ascendente", value=False)

    df_display = df[selected_cols].sort_values(sort_col, ascending=sort_asc)

    # Data table
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "risk_score": st.column_config.ProgressColumn(
                "Riesgo", min_value=0, max_value=100, format="%.0f",
            ),
            "costo_exceso_mn": st.column_config.NumberColumn(
                "Costo Exceso", format="$%,.0f",
            ),
            "cosprom": st.column_config.NumberColumn(
                "Costo Prom", format="$%,.2f",
            ),
            "meses_inventario": st.column_config.NumberColumn(
                "Meses Inv", format="%.1f",
            ),
        },
    )

    # Export
    render_section_header("Exportar")
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        csv_buffer = io.BytesIO()
        df_display.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 Descargar CSV",
            data=csv_buffer.getvalue(),
            file_name="inventario_slow_movement.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_exp2:
        excel_buffer = io.BytesIO()
        with __import__("pandas").ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df_display.to_excel(writer, index=False, sheet_name="Datos")
        st.download_button(
            "📥 Descargar Excel",
            data=excel_buffer.getvalue(),
            file_name="inventario_slow_movement.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
