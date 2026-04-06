"""
KPI Cards — Premium styled cards with traffic-light borders and monospace values.
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import THRESHOLDS


def _get_card_class(value, key: str) -> str:
    """Return CSS class based on KPI threshold."""
    if value is None:
        return "gray"
    t = THRESHOLDS.get(key, {})
    green = t.get("green")
    yellow = t.get("yellow")
    if green is None:
        return "gray"
    if value <= green:
        return "green"
    if value <= yellow:
        return "yellow"
    return "red"


def _mxn(v) -> str:
    if v is None:
        return "$0"
    return f"${v:,.0f}"


def _pct(v) -> str:
    if v is None:
        return "0%"
    return f"{v:.1f}%"


def _num(v, decimals=1) -> str:
    if v is None:
        return "—"
    return f"{v:,.{decimals}f}"


def render_kpi_cards(kpis: dict):
    """Render KPI cards using custom HTML grid."""
    items = [
        {
            "label": "Productos Analizados",
            "value": f"{kpis.get('total_products', 0):,}",
            "sub": "Items en período",
            "cls": "gray",
        },
        {
            "label": "Costo Exceso Total",
            "value": _mxn(kpis.get("total_excess_cost")),
            "sub": "Inventario inmovilizado en MXN",
            "cls": _get_card_class(kpis.get("total_excess_cost", 0), "excess_cost"),
        },
        {
            "label": "Sin Ventas en Período",
            "value": f"{kpis.get('zero_sales_count', 0):,}",
            "sub": _pct(kpis.get("zero_sales_pct")) + " del total",
            "cls": _get_card_class(kpis.get("zero_sales_pct", 0), "zero_sales_pct"),
        },
        {
            "label": "Mediana Meses de Inv",
            "value": _num(kpis.get("median_months_inventory")),
            "sub": "meses de cobertura",
            "cls": _get_card_class(kpis.get("median_months_inventory", 0), "meses_inventario"),
        },
        {
            "label": "Costo Existencia Total",
            "value": _mxn(kpis.get("total_exist_cost")),
            "sub": "Valor de inventario activo",
            "cls": "gray",
        },
        {
            "label": "Ratio Exceso / Exist",
            "value": _pct(kpis.get("excess_ratio", 0) * 100),
            "sub": "Proporción de exceso",
            "cls": _get_card_class(kpis.get("excess_ratio", 0), "excess_ratio"),
        },
    ]

    cards_html = '<div class="kpi-grid">'
    for item in items:
        cls = item["cls"]
        cards_html += f"""
        <div class="kpi-card {cls}">
            <div class="kpi-label">
                <span class="kpi-dot {cls}"></span>
                {item["label"]}
            </div>
            <div class="kpi-value">{item["value"]}</div>
            <div class="kpi-sub">{item["sub"]}</div>
        </div>
        """
    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)
    # spacer so Streamlit doesn't clip
    st.write("")


def render_alerts(kpis: dict):
    """Render alert banners for critical KPI conditions."""
    alerts = []

    excess_cost = kpis.get("total_excess_cost", 0) or 0
    if excess_cost >= 200_000:
        alerts.append(("danger", f"⚠️ Costo de exceso crítico: <strong>{_mxn(excess_cost)}</strong> — Requiere acción inmediata."))

    zero_pct = kpis.get("zero_sales_pct", 0) or 0
    if zero_pct >= 15:
        alerts.append(("warning", f"⚠️ {_pct(zero_pct)} de productos sin ventas en el período — Evaluar liquidación."))

    median_months = kpis.get("median_months_inventory", 0) or 0
    if median_months >= 12:
        alerts.append(("danger", f"📅 Mediana de {_num(median_months)} meses de inventario — Cobertura excesiva detectada."))
    elif median_months >= 6:
        alerts.append(("warning", f"📅 Mediana de {_num(median_months)} meses de inventario — Monitorear tendencia."))

    excess_ratio = kpis.get("excess_ratio", 0) or 0
    if excess_ratio >= 0.5:
        alerts.append(("danger", f"📦 Ratio exceso/existencia: <strong>{_pct(excess_ratio * 100)}</strong> — Más de la mitad del inventario en exceso."))

    if not alerts:
        alerts.append(("success", "✅ KPIs dentro de rangos normales — Sin alertas críticas."))

    html = ""
    for cls, msg in alerts:
        html += f'<div class="alert-banner {cls}">{msg}</div>'

    st.markdown(html, unsafe_allow_html=True)
