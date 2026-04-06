"""
Page: Executive Overview with strategic blocks and KPI analytics.
"""
import html
import pandas as pd
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.components.brand import render_header, render_section_header
from app.components.kpi_cards import render_kpi_cards, render_alerts
from app.components.charts import (
    chart_family_excess_cost,
    chart_family_zero_sales,
    chart_months_distribution,
    chart_risk_scatter,
)
from app.components.filters import apply_filters
from services.database import get_latest_snapshots, db_exists
from services.kpi_engine import calc_kpi_summary, add_risk_scores


def _num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")


def _risk_state(score: float):
    if score >= 80:
        return "Critical", "#F87171"
    if score >= 60:
        return "Moderate", "#FBBF24"
    return "Controlled", "#34D399"


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    for col in ["risk_score", "costo_exceso_mn", "costo_exist_mn", "exceso", "cosprom", "meses_inventario", "ventas_periodo"]:
        if col in data.columns:
            data[col] = _num(data[col])
    if "costo_exceso_mn" not in data.columns and "exceso" in data.columns and "cosprom" in data.columns:
        data["costo_exceso_mn"] = data["exceso"].fillna(0) * data["cosprom"].fillna(0)
    data["costo_exceso_mn"] = data.get("costo_exceso_mn", pd.Series(index=data.index, dtype=float)).fillna(0)
    data["costo_exist_mn"] = data.get("costo_exist_mn", pd.Series(index=data.index, dtype=float)).fillna(0)
    data["cse_prod"] = data.get("cse_prod", pd.Series(index=data.index, dtype=str)).fillna("Sin familia")
    return data


def _render_strategic_portfolio(df_filtered, kpis: dict):
    if df_filtered.empty:
        return

    data = _prepare(df_filtered)

    agg_risk = round(float(data["risk_score"].fillna(0).mean()) if "risk_score" in data.columns else 0.0, 1)
    risk_label, risk_color = _risk_state(agg_risk)
    ring_deg = max(8, min(360, int((agg_risk / 100) * 360)))

    delta = round(float(data["risk_score"].fillna(0).std()) if "risk_score" in data.columns else 0.0, 1)

    top_risk = data.sort_values(["risk_score", "costo_exceso_mn"], ascending=[False, False]).head(3)
    interventions = []
    for _, row in top_risk.iterrows():
        score = float(row.get("risk_score") or 0)
        _, dot = _risk_state(score)
        title = f"{row.get('cve_prod', 'SKU')} - {row.get('cse_prod', 'Familia')}"
        desc = (
            f"Score {score:.1f}/100 | Exceso ${float(row.get('costo_exceso_mn') or 0):,.0f} "
            f"| Cobertura {float(row.get('meses_inventario') or 0):.1f} meses"
        )
        interventions.append((html.escape(str(title)), html.escape(str(desc)), dot))

    if not interventions:
        interventions.append(("Sin alertas", "No se detectaron intervenciones en el corte actual.", "#34D399"))

    fam = (
        data.groupby("cse_prod", dropna=False)
        .agg(risk=("risk_score", "mean"), costo=("costo_exceso_mn", "sum"), count=("cse_prod", "count"))
        .reset_index()
        .sort_values("risk", ascending=False)
        .head(3)
    )

    family_rows = []
    for _, row in fam.iterrows():
        fam_name = row["cse_prod"] if row["cse_prod"] else "Sin familia"
        fam_risk = float(row["risk"] or 0)
        status, color = _risk_state(fam_risk)
        width = int(max(15, min(95, fam_risk)))
        family_rows.append((html.escape(str(fam_name)), status, color, width, float(row["costo"] or 0)))

    if not family_rows:
        family_rows = [("Sin datos", "Stable", "#34D399", 20, 0.0)]

    family_cost = data.groupby("cse_prod", dropna=False)["costo_exceso_mn"].sum().sort_values(ascending=False)
    total_cost = float(family_cost.sum())
    if len(family_cost) > 0 and total_cost > 0:
        top_family = str(family_cost.index[0])
        conc = float((family_cost.iloc[0] / total_cost) * 100)
    else:
        top_family = "Sin familia"
        conc = 0.0

    zero_sales = float(kpis.get("zero_sales_pct") or 0)
    excess_cost = float(kpis.get("total_excess_cost") or 0)
    exist_cost = float(kpis.get("total_exist_cost") or 0)
    potential = max(excess_cost * 0.05, exist_cost * (zero_sales / 100) * 0.01)

    left_col, right_col = st.columns([7, 5], gap="large")

    with left_col:
        st.markdown(
            f"""
            <div class='exec-card' style='padding:1.1rem 1.2rem; margin-bottom:0.95rem;'>
                <div style='display:flex; justify-content:space-between; gap:1rem; align-items:center;'>
                    <div style='max-width:68%;'>
                        <div style='font-size:0.72rem; letter-spacing:.16em; text-transform:uppercase; color:#8FA1B9; font-weight:700;'>Aggregate Risk Score</div>
                        <div style='display:flex; align-items:baseline; gap:.5rem; margin-top:.35rem;'>
                            <div style='font-family:Montserrat,sans-serif; font-weight:900; font-size:3.2rem; line-height:1; color:#F8FBFF;'>{agg_risk:.0f}</div>
                            <div style='color:{risk_color}; font-weight:700; font-size:1.02rem; margin-top:.5rem;'>{risk_label}</div>
                        </div>
                        <p style='color:#9CB0C8; font-size:.84rem; margin-top:.55rem; line-height:1.45;'>
                            El riesgo agregado muestra una dispersion interna de <span style='color:{risk_color}; font-weight:700;'>{delta}%</span>,
                            con mayor presion en familias de alta cobertura y baja rotacion.
                        </p>
                    </div>
                    <div style='position:relative; width:170px; height:170px;'>
                        <div style='position:absolute; inset:0; border-radius:50%; background:conic-gradient({risk_color} {ring_deg}deg, #273547 {ring_deg}deg 360deg);'></div>
                        <div style='position:absolute; inset:18px; border-radius:50%; background:#0F151F; border:1px solid rgba(80,97,121,.6); display:flex; align-items:center; justify-content:center; flex-direction:column;'>
                            <div style='font-size:1.5rem; color:{risk_color};'>R</div>
                            <div style='font-size:.74rem; color:#AFC2DA;'>Risk</div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class='exec-card' style='padding:1rem 1.15rem;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:.75rem;'>
                    <div style='font-family:Cormorant Garamond,serif; font-size:1.28rem; color:#EAF3FF;'>Family Risk Performance</div>
                    <div style='font-size:.72rem; color:#68D5FF; font-weight:700;'>View All</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        for fam_name, status, color, width, cost in family_rows:
            st.markdown(
                f"""
                <div style='margin-bottom:.65rem;'>
                    <div style='display:flex; justify-content:space-between; align-items:end;'>
                        <span style='font-size:.68rem; text-transform:uppercase; letter-spacing:.12em; color:#96A9C1; font-weight:700;'>{fam_name}</span>
                        <span style='font-size:.68rem; color:{color}; font-weight:700;'>{status}</span>
                    </div>
                    <div style='height:8px; background:rgba(61,80,104,.35); border-radius:999px; overflow:hidden; margin-top:.28rem;'>
                        <div style='height:100%; width:{width}%; background:{color};'></div>
                    </div>
                    <div style='font-size:.66rem; color:#8498B2; margin-top:.26rem;'>Costo exceso: ${cost:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown(
            """
            <div class='exec-card' style='padding:0; overflow:hidden; margin-bottom:0.95rem;'>
                <div style='padding:.78rem 1rem; border-bottom:1px solid rgba(54,69,87,.62); background:linear-gradient(90deg, rgba(248,113,113,.10), rgba(248,113,113,.03));'>
                    <div style='font-size:.9rem; font-weight:800; color:#FCA5A5;'>Critical Interventions</div>
                </div>
                <div style='padding:.92rem 1rem;'>
            """,
            unsafe_allow_html=True,
        )

        for title, desc, dot_color in interventions:
            st.markdown(
                f"""
                <div style='display:flex; gap:.52rem; margin-bottom:.68rem;'>
                    <div style='width:8px; height:8px; border-radius:999px; background:{dot_color}; margin-top:.4rem;'></div>
                    <div>
                        <div style='font-size:.79rem; color:#EAF3FF; font-weight:700;'>{title}</div>
                        <div style='font-size:.71rem; color:#9CB0C8; line-height:1.35;'>{desc}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class='exec-card' style='padding:.95rem 1rem; margin-bottom:.95rem;'>
                <div style='font-family:Cormorant Garamond,serif; font-size:1.24rem; color:#EAF3FF; margin-bottom:.65rem;'>Executive Insights</div>
                <div style='padding:.72rem; border-radius:9px; background:rgba(56,189,248,.09); border:1px solid rgba(56,189,248,.22); margin-bottom:.55rem;'>
                    <div style='font-size:.62rem; text-transform:uppercase; letter-spacing:.1em; color:#6fd8ff; font-weight:800;'>Concentracion de riesgo</div>
                    <div style='font-size:.78rem; color:#EAF3FF; margin-top:.3rem;'>
                        La familia <strong>{html.escape(top_family)}</strong> concentra <strong>{conc:.1f}%</strong> del costo de exceso.
                    </div>
                </div>
                <div style='padding:.72rem; border-radius:9px; background:rgba(26,33,44,.65); border:1px solid rgba(56,189,248,.14);'>
                    <div style='font-size:.62rem; text-transform:uppercase; letter-spacing:.1em; color:#9db1ca; font-weight:800;'>Oportunidad prioritaria</div>
                    <div style='font-size:.78rem; color:#EAF3FF; margin-top:.3rem;'>
                        Con {zero_sales:.1f}% sin ventas, una reduccion tactica del 5% podria liberar ~<strong>${potential:,.0f}</strong>.
                    </div>
                </div>
            </div>
            <div class='exec-card' style='padding:.6rem .85rem; display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-size:.68rem; color:#9fb2c9;'>Systems Operational</span>
                <span style='font-size:.64rem; color:#7f96b3;'>LAST_VERIFIED: INVENTARIO-Q4</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_overview(filters: dict):
    render_header(
        "Strategic Risk Portfolio",
        "Resumen ejecutivo de exposicion operacional, exceso de inventario y oportunidades de optimizacion.",
    )

    if not db_exists():
        st.warning("No hay datos cargados. Ve a Cargar Datos para importar un archivo Excel.")
        return

    periodo = filters.get("periodo_meses", 6)
    df = get_latest_snapshots(periodo_meses=periodo)

    if df.empty:
        st.info(f"No hay datos para el periodo de {periodo} meses. Prueba con otro rango.")
        return

    df = add_risk_scores(df)
    df_filtered = apply_filters(df, filters)
    kpis = calc_kpi_summary(df_filtered)

    render_alerts(kpis)
    _render_strategic_portfolio(df_filtered, kpis)

    render_section_header("Core KPI Command Grid")
    render_kpi_cards(kpis)

    st.markdown("<div style='height:0.7rem;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_section_header("Costo de Exceso por Familia")
        chart_family_excess_cost(df_filtered)
    with col2:
        render_section_header("Distribucion de Meses de Inventario")
        chart_months_distribution(df_filtered)

    st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="large")
    with col3:
        render_section_header("Productos sin Ventas por Familia")
        chart_family_zero_sales(df_filtered)
    with col4:
        render_section_header("Mapa de Riesgo")
        chart_risk_scatter(df_filtered)
