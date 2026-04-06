"""
KPI Cards — Render dashboard metric cards with traffic-light indicators.
"""
import streamlit as st


def render_kpi_cards(kpis: dict):
    """Render the main KPI card grid."""

    def _tl_class(tl: str) -> str:
        return {"🟢": "green", "🟡": "yellow", "🔴": "red"}.get(tl, "gray")

    def _card(label: str, value, sub: str = "", tl: str = "⚪"):
        cls = _tl_class(tl)
        return f"""
        <div class="kpi-card {cls}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{tl} {value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """

    # Format values
    excess_cost = kpis.get("total_excess_cost", 0)
    if excess_cost >= 1_000_000:
        excess_str = f"${excess_cost / 1_000_000:,.1f}M"
    elif excess_cost >= 1_000:
        excess_str = f"${excess_cost / 1_000:,.0f}K"
    else:
        excess_str = f"${excess_cost:,.0f}"

    months = kpis.get("avg_months_inventory")
    months_str = f"{months} meses" if months else "N/D"

    zero_pct = kpis.get("zero_sales_pct", 0)
    excess_ratio = kpis.get("avg_excess_ratio", 0)
    family_conc = kpis.get("family_concentration", 0)
    aging = kpis.get("aging_days")

    cards_html = f"""
    <div class="kpi-grid">
        {_card("Productos Analizados", f'{kpis.get("total_products", 0):,}',
               f'{kpis.get("total_stock_units", 0):,} unidades en stock')}

        {_card("Mediana Meses Inventario", months_str,
               "Cobertura de inventario",
               kpis.get("avg_months_tl", "⚪"))}

        {_card("Costo Exceso Total", excess_str,
               f'{kpis.get("total_excess_units", 0):,} unidades exceso',
               kpis.get("excess_cost_tl", "⚪"))}

        {_card("Productos Sin Ventas", f'{zero_pct}%',
               f'{kpis.get("zero_sales_count", 0)} de {kpis.get("total_products", 0)}',
               kpis.get("zero_sales_tl", "⚪"))}

        {_card("Ratio de Exceso", f'{excess_ratio:.1%}',
               "Mediana exceso/existencia",
               kpis.get("excess_ratio_tl", "⚪"))}

        {_card("Concentración por Familia", f'{family_conc:.0%}',
               f'Mayor: {kpis.get("top_family", "N/A")}',
               kpis.get("family_conc_tl", "⚪"))}
    </div>
    """

    st.markdown(cards_html, unsafe_allow_html=True)


def render_alerts(kpis: dict):
    """Render alert banners based on KPI traffic lights."""
    alerts = []

    if kpis.get("excess_cost_tl") == "🔴":
        cost = kpis.get("total_excess_cost", 0)
        alerts.append(("danger", f"🚨 Costo de exceso crítico: ${cost:,.0f} MXN — requiere acción inmediata"))

    if kpis.get("zero_sales_tl") == "🔴":
        pct = kpis.get("zero_sales_pct", 0)
        alerts.append(("danger", f"🚨 {pct}% de productos sin ventas — revisar obsolescencia"))

    if kpis.get("avg_months_tl") == "🔴":
        months = kpis.get("avg_months_inventory", 0)
        alerts.append(("warning", f"⚠️ Mediana de {months} meses de inventario — riesgo de lento movimiento"))

    if kpis.get("family_conc_tl") == "🔴":
        family = kpis.get("top_family", "")
        pct = kpis.get("family_concentration", 0)
        alerts.append(("warning", f"⚠️ Familia '{family}' concentra {pct:.0%} del exceso — diversificar acciones"))

    if not alerts:
        alerts.append(("success", "✅ Indicadores dentro de parámetros aceptables"))

    for level, msg in alerts:
        st.markdown(f'<div class="alert-banner {level}">{msg}</div>', unsafe_allow_html=True)
