"""
Charts — Plotly visualizations for the dashboard.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_DANGER, COLOR_WARNING, COLOR_SUCCESS


CHART_TEMPLATE = "plotly_white"
CHART_COLORS = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, "#FF6B6B",
                "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#F0E68C"]


def chart_family_excess_cost(df: pd.DataFrame):
    """Horizontal bar chart — Excess cost by product family."""
    if df.empty:
        st.info("Sin datos para graficar")
        return

    family_data = df.groupby("cse_prod")["costo_exceso_mn"].sum().reset_index()
    family_data = family_data.sort_values("costo_exceso_mn", ascending=True).tail(15)

    fig = px.bar(
        family_data, x="costo_exceso_mn", y="cse_prod",
        orientation="h",
        labels={"costo_exceso_mn": "Costo Exceso (MXN)", "cse_prod": ""},
        color_discrete_sequence=[COLOR_SECONDARY],
        template=CHART_TEMPLATE,
    )
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter"),
        xaxis_tickformat="$,.0f",
        yaxis=dict(tickfont=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_family_zero_sales(df: pd.DataFrame):
    """Donut chart — Products with zero sales by family."""
    if df.empty or "ventas_periodo" not in df.columns:
        st.info("Sin datos para graficar")
        return

    zero = df[df["ventas_periodo"].fillna(0) == 0]
    if zero.empty:
        st.success("No hay productos con cero ventas 🎉")
        return

    family_zero = zero.groupby("cse_prod").size().reset_index(name="count")
    family_zero = family_zero.sort_values("count", ascending=False)

    fig = px.pie(
        family_zero, values="count", names="cse_prod",
        hole=0.55,
        color_discrete_sequence=CHART_COLORS,
        template=CHART_TEMPLATE,
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter"),
        showlegend=True,
        legend=dict(font=dict(size=10)),
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)


def chart_months_distribution(df: pd.DataFrame):
    """Histogram of months of inventory distribution."""
    if df.empty or "meses_inventario" not in df.columns:
        st.info("Sin datos para graficar")
        return

    valid = df[df["meses_inventario"].notna() & (df["meses_inventario"] < 100)]
    if valid.empty:
        st.info("Sin datos válidos")
        return

    fig = px.histogram(
        valid, x="meses_inventario",
        nbins=30,
        labels={"meses_inventario": "Meses de Inventario"},
        color_discrete_sequence=[COLOR_PRIMARY],
        template=CHART_TEMPLATE,
    )
    # Add threshold lines
    fig.add_vline(x=6, line_dash="dash", line_color=COLOR_SUCCESS,
                  annotation_text="6M (verde)", annotation_position="top right")
    fig.add_vline(x=12, line_dash="dash", line_color=COLOR_WARNING,
                  annotation_text="12M (amarillo)", annotation_position="top right")

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Inter"),
        xaxis_title="Meses de Inventario",
        yaxis_title="Productos",
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_excess_trend(trend_df: pd.DataFrame):
    """Line chart — Weekly excess inventory trend."""
    if trend_df.empty:
        st.info("Sin datos de tendencia semanal")
        return

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=trend_df["snapshot_date"],
        y=trend_df["total_costo_exceso"],
        mode="lines+markers",
        name="Costo Exceso Total",
        line=dict(color=COLOR_DANGER, width=2.5),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(220,53,69,0.1)",
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter"),
        template=CHART_TEMPLATE,
        xaxis_title="Semana",
        yaxis_title="Costo Exceso (MXN)",
        yaxis_tickformat="$,.0f",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_risk_scatter(df: pd.DataFrame):
    """Scatter plot — Risk score vs excess cost, sized by stock."""
    if df.empty or "risk_score" not in df.columns:
        st.info("Sin datos de riesgo")
        return

    fig = px.scatter(
        df, x="costo_exceso_mn", y="risk_score",
        size="existencia",
        color="cse_prod",
        hover_name="cve_prod",
        hover_data=["desc_prod", "meses_inventario", "ventas_periodo"],
        labels={
            "costo_exceso_mn": "Costo Exceso (MXN)",
            "risk_score": "Score de Riesgo",
            "cse_prod": "Familia",
            "existencia": "Existencia",
        },
        color_discrete_sequence=CHART_COLORS,
        template=CHART_TEMPLATE,
    )
    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter"),
        xaxis_tickformat="$,.0f",
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_top_products_bar(df: pd.DataFrame, value_col: str, label: str, n: int = 15):
    """Generic horizontal bar chart for top N products."""
    if df.empty or value_col not in df.columns:
        st.info("Sin datos para graficar")
        return

    top = df.nlargest(n, value_col)
    # Create label
    if "desc_prod" in top.columns:
        top["_label"] = top["cve_prod"].astype(str) + " - " + top["desc_prod"].astype(str).str[:30]
    else:
        top["_label"] = top["cve_prod"].astype(str)

    top = top.sort_values(value_col, ascending=True)

    fig = px.bar(
        top, x=value_col, y="_label",
        orientation="h",
        labels={value_col: label, "_label": ""},
        color_discrete_sequence=[COLOR_DANGER],
        template=CHART_TEMPLATE,
    )
    fig.update_layout(
        height=max(300, n * 28),
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter", size=11),
        xaxis_tickformat="$,.0f" if "costo" in value_col.lower() else ",",
    )
    st.plotly_chart(fig, use_container_width=True)
