"""
KPI Cards for executive dashboard style.
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import THRESHOLDS


def _get_card_class(value, key: str) -> str:
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
        return "-"
    return f"{v:,.{decimals}f}"


def _card_html(item: dict) -> str:
    return (
        f"<div class='kpi-card {item['cls']}'>"
        f"<div class='kpi-label'>{item['label']}</div>"
        f"<div class='kpi-value'>{item['value']}</div>"
        f"<div class='kpi-sub'>{item['sub']}</div>"
        "</div>"
    )


def render_kpi_cards(kpis: dict):
    items = [
        {
            "label": "Productos Analizados",
            "value": f"{kpis.get('total_products', 0):,}",
            "sub": "Items activos en periodo",
            "cls": "gray",
        },
        {
            "label": "Costo Exceso Total",
            "value": _mxn(kpis.get("total_excess_cost")),
            "sub": "Capital inmovilizado",
            "cls": _get_card_class(kpis.get("total_excess_cost", 0), "excess_cost"),
        },
        {
            "label": "Sin Ventas",
            "value": f"{kpis.get('zero_sales_count', 0):,}",
            "sub": _pct(kpis.get("zero_sales_pct")) + " del portfolio",
            "cls": _get_card_class(kpis.get("zero_sales_pct", 0), "zero_sales_pct"),
        },
        {
            "label": "Mediana Meses Inv",
            "value": _num(kpis.get("avg_months_inventory")),
            "sub": "Cobertura real",
            "cls": _get_card_class(kpis.get("avg_months_inventory", 0), "meses_inventario"),
        },
        {
            "label": "Costo Existencia",
            "value": _mxn(kpis.get("total_exist_cost")),
            "sub": "Valor de stock",
            "cls": "gray",
        },
        {
            "label": "Ratio Exceso / Exist",
            "value": _pct((kpis.get("avg_excess_ratio", 0) or 0) * 100),
            "sub": "Presion de sobreinventario",
            "cls": _get_card_class(kpis.get("avg_excess_ratio", 0), "excess_ratio"),
        },
    ]

    cards_html = "".join(_card_html(item) for item in items)
    st.markdown(f"<div class='kpi-grid'>{cards_html}</div>", unsafe_allow_html=True)


def render_alerts(kpis: dict):
    alerts = []

    excess_cost = kpis.get("total_excess_cost", 0) or 0
    if excess_cost >= 200_000:
        alerts.append(("danger", f"Costo de exceso critico: <strong>{_mxn(excess_cost)}</strong>."))

    zero_pct = kpis.get("zero_sales_pct", 0) or 0
    if zero_pct >= 15:
        alerts.append(("warning", f"{_pct(zero_pct)} del catalogo sin ventas en el periodo."))

    median_months = kpis.get("avg_months_inventory", 0) or 0
    if median_months >= 12:
        alerts.append(("danger", f"Cobertura alta: mediana de {_num(median_months)} meses."))
    elif median_months >= 6:
        alerts.append(("warning", f"Cobertura a monitorear: mediana de {_num(median_months)} meses."))

    excess_ratio = kpis.get("avg_excess_ratio", 0) or 0
    if excess_ratio >= 0.5:
        alerts.append(("danger", f"Ratio exceso/existencia: <strong>{_pct(excess_ratio * 100)}</strong>."))

    if not alerts:
        alerts.append(("success", "KPIs dentro de rangos operativos esperados."))

    html = ""
    for cls, msg in alerts:
        html += f'<div class="alert-banner {cls}">{msg}</div>'

    st.markdown(html, unsafe_allow_html=True)
