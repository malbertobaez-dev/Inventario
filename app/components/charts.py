"""
Charts: Plotly visualizations for the dashboard.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import COLOR_DANGER, COLOR_SUCCESS, COLOR_WARNING


CHART_TEMPLATE = "plotly_dark"
CHART_COLORS = [
    "#38BDF8", "#60A5FA", "#A78BFA", "#F472B6", "#FBBF24",
    "#34D399", "#F87171", "#22D3EE", "#94A3B8", "#E879F9",
]

_LAYOUT_BASE = dict(
    font=dict(family="Inter", size=12, color="#DDE7F4"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=22, b=14),
    hoverlabel=dict(font_family="Inter"),
)


def _num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")


def _apply_layout(fig, height: int = 330):
    fig.update_layout(template=CHART_TEMPLATE, height=height, **_LAYOUT_BASE)
    fig.update_xaxes(gridcolor="rgba(120,140,165,0.16)", zerolinecolor="rgba(120,140,165,0.2)")
    fig.update_yaxes(gridcolor="rgba(120,140,165,0.16)", zerolinecolor="rgba(120,140,165,0.2)")


def chart_family_excess_cost(df: pd.DataFrame):
    if df.empty or "cse_prod" not in df.columns:
        st.info("Sin datos para graficar")
        return

    data = df.copy()
    if "costo_exceso_mn" in data.columns:
        data["costo_exceso_mn"] = _num(data["costo_exceso_mn"])
    elif "exceso" in data.columns and "cosprom" in data.columns:
        data["costo_exceso_mn"] = _num(data["exceso"]) * _num(data["cosprom"])
    else:
        st.info("No hay columna de costo de exceso para graficar")
        return

    data["costo_exceso_mn"] = data["costo_exceso_mn"].fillna(0)
    family_data = data.groupby("cse_prod", dropna=False)["costo_exceso_mn"].sum().reset_index()
    family_data["cse_prod"] = family_data["cse_prod"].fillna("Sin familia")
    family_data = family_data.sort_values("costo_exceso_mn", ascending=True).tail(12)

    if family_data["costo_exceso_mn"].sum() <= 0:
        st.info("No hay costo de exceso mayor a cero para mostrar.")
        return

    fig = px.bar(
        family_data,
        x="costo_exceso_mn",
        y="cse_prod",
        orientation="h",
        labels={"costo_exceso_mn": "Costo Exceso (MXN)", "cse_prod": ""},
        color_discrete_sequence=["#38BDF8"],
        template=CHART_TEMPLATE,
    )
    _apply_layout(fig, height=340)
    fig.update_layout(xaxis_tickformat="$,.0f", yaxis=dict(tickfont=dict(size=11)))
    st.plotly_chart(fig, use_container_width=True)


def chart_family_zero_sales(df: pd.DataFrame):
    if df.empty or "ventas_periodo" not in df.columns:
        st.info("Sin datos para graficar")
        return

    data = df.copy()
    data["ventas_periodo"] = _num(data["ventas_periodo"]).fillna(0)
    data["cse_prod"] = data.get("cse_prod", pd.Series(index=data.index, dtype=str)).fillna("Sin familia")

    zero = data[data["ventas_periodo"] == 0]
    if zero.empty:
        st.success("No hay productos con cero ventas")
        return

    family_zero = zero.groupby("cse_prod", dropna=False).size().reset_index(name="count")
    family_zero = family_zero.sort_values("count", ascending=False)

    fig = px.pie(
        family_zero,
        values="count",
        names="cse_prod",
        hole=0.62,
        color_discrete_sequence=CHART_COLORS,
        template=CHART_TEMPLATE,
    )
    _apply_layout(fig, height=320)
    fig.update_layout(showlegend=True, legend=dict(font=dict(size=10)))
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)


def chart_months_distribution(df: pd.DataFrame):
    if df.empty or "meses_inventario" not in df.columns:
        st.info("Sin datos para graficar")
        return

    data = df.copy()
    data["meses_inventario"] = _num(data["meses_inventario"])
    valid = data[data["meses_inventario"].notna() & (data["meses_inventario"] < 100)]
    if valid.empty:
        st.info("Sin datos validos")
        return

    fig = px.histogram(
        valid,
        x="meses_inventario",
        nbins=26,
        labels={"meses_inventario": "Meses de Inventario"},
        color_discrete_sequence=["#60A5FA"],
        template=CHART_TEMPLATE,
    )
    fig.add_vline(x=6, line_dash="dash", line_color=COLOR_SUCCESS)
    fig.add_vline(x=12, line_dash="dash", line_color=COLOR_WARNING)
    _apply_layout(fig, height=320)
    fig.update_layout(xaxis_title="Meses de Inventario", yaxis_title="Productos")
    st.plotly_chart(fig, use_container_width=True)


def chart_excess_trend(trend_df: pd.DataFrame):
    if trend_df.empty:
        st.info("Sin datos de tendencia semanal")
        return

    data = trend_df.copy()
    data["total_costo_exceso"] = _num(data["total_costo_exceso"]).fillna(0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["snapshot_date"],
            y=data["total_costo_exceso"],
            mode="lines+markers",
            name="Costo Exceso Total",
            line=dict(color=COLOR_DANGER, width=2.3),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(248,113,113,0.12)",
        )
    )

    _apply_layout(fig, height=320)
    fig.update_layout(xaxis_title="Semana", yaxis_title="Costo Exceso (MXN)", yaxis_tickformat="$,.0f", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


def chart_risk_scatter(df: pd.DataFrame):
    if df.empty or "risk_score" not in df.columns:
        st.info("Sin datos de riesgo")
        return

    data = df.copy()
    for col in ["risk_score", "costo_exceso_mn", "existencia", "meses_inventario", "ventas_periodo"]:
        if col in data.columns:
            data[col] = _num(data[col])

    if "costo_exceso_mn" not in data.columns:
        if "exceso" in data.columns and "cosprom" in data.columns:
            data["costo_exceso_mn"] = _num(data["exceso"]) * _num(data["cosprom"])
        else:
            st.info("No hay datos de costo de exceso para el mapa.")
            return

    data = data.dropna(subset=["risk_score", "costo_exceso_mn"]) 
    if data.empty:
        st.info("No hay puntos validos para el mapa de riesgo.")
        return

    data["cse_prod"] = data.get("cse_prod", pd.Series(index=data.index, dtype=str)).fillna("Sin familia")
    data["existencia"] = data.get("existencia", pd.Series(index=data.index, dtype=float)).fillna(1).clip(lower=1)

    fig = px.scatter(
        data,
        x="costo_exceso_mn",
        y="risk_score",
        size="existencia",
        color="cse_prod",
        hover_name="cve_prod" if "cve_prod" in data.columns else None,
        hover_data=[c for c in ["desc_prod", "meses_inventario", "ventas_periodo"] if c in data.columns],
        labels={
            "costo_exceso_mn": "Costo Exceso (MXN)",
            "risk_score": "Score de Riesgo",
            "cse_prod": "Familia",
            "existencia": "Existencia",
        },
        color_discrete_sequence=CHART_COLORS,
        template=CHART_TEMPLATE,
    )
    _apply_layout(fig, height=360)
    fig.update_layout(xaxis_tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True)


def chart_top_products_bar(df: pd.DataFrame, value_col: str, label: str, n: int = 15):
    if df.empty or value_col not in df.columns:
        st.info("Sin datos para graficar")
        return

    data = df.copy()
    data[value_col] = _num(data[value_col])
    data = data.dropna(subset=[value_col])
    if data.empty:
        st.info("Sin datos para graficar")
        return

    top = data.nlargest(n, value_col)
    if "desc_prod" in top.columns:
        top["_label"] = top["cve_prod"].astype(str) + " - " + top["desc_prod"].astype(str).str[:30]
    else:
        top["_label"] = top["cve_prod"].astype(str) if "cve_prod" in top.columns else top.index.astype(str)

    top = top.sort_values(value_col, ascending=True)

    fig = px.bar(
        top,
        x=value_col,
        y="_label",
        orientation="h",
        labels={value_col: label, "_label": ""},
        color_discrete_sequence=["#F87171" if "risk" in value_col else "#38BDF8"],
        template=CHART_TEMPLATE,
    )
    _apply_layout(fig, height=max(300, n * 24))
    fig.update_layout(font=dict(family="Inter", size=11, color="#DDE7F4"))
    fig.update_layout(xaxis_tickformat="$,.0f" if "costo" in value_col.lower() else ",")
    st.plotly_chart(fig, use_container_width=True)
