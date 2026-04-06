"""
KPI Calculation Engine — Metrics, risk scores, rankings, and alerts.
"""
import numpy as np
import pandas as pd

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import THRESHOLDS, RISK_WEIGHTS


# ── Traffic Light Helper ───────────────────────────────────────────

def traffic_light(value, metric_key: str, higher_is_worse: bool = True) -> str:
    """Return '🟢', '🟡', or '🔴' based on threshold config."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "⚪"
    t = THRESHOLDS.get(metric_key)
    if not t:
        return "⚪"
    if higher_is_worse:
        if value <= t["green"]:
            return "🟢"
        elif value <= t["yellow"]:
            return "🟡"
        else:
            return "🔴"
    else:
        if value >= t["green"]:
            return "🟢"
        elif value >= t["yellow"]:
            return "🟡"
        else:
            return "🔴"


def traffic_color(value, metric_key: str, higher_is_worse: bool = True) -> str:
    """Return hex color string for the traffic light."""
    tl = traffic_light(value, metric_key, higher_is_worse)
    return {"🟢": "#28A745", "🟡": "#FFC107", "🔴": "#DC3545"}.get(tl, "#6c757d")


# ── Core KPI Calculations ─────────────────────────────────────────

def calc_kpi_summary(df: pd.DataFrame) -> dict:
    """
    Calculate all dashboard-level KPIs from a snapshots DataFrame.
    Returns a dict of KPI values and their traffic lights.
    """
    if df.empty:
        return _empty_kpis()

    # K1: Average Months of Inventory
    valid_mi = df["meses_inventario"].dropna()
    avg_months = valid_mi.median() if len(valid_mi) > 0 else None

    # K2: Total Excess Inventory Value
    total_excess_cost = df["costo_exceso_mn"].sum() if "costo_exceso_mn" in df.columns else 0
    if pd.isna(total_excess_cost):
        total_excess_cost = 0

    # K3: Zero-Sales Products percentage
    total_products = len(df)
    zero_sales = len(df[df["ventas_periodo"].fillna(0) == 0]) if "ventas_periodo" in df.columns else 0
    zero_sales_pct = (zero_sales / total_products * 100) if total_products > 0 else 0

    # K4: Average Excess Ratio
    if "exceso" in df.columns and "existencia" in df.columns:
        mask = df["existencia"] > 0
        if mask.any():
            avg_excess_ratio = (df.loc[mask, "exceso"].fillna(0) / df.loc[mask, "existencia"]).median()
        else:
            avg_excess_ratio = 0
    else:
        avg_excess_ratio = 0

    # K5: Family Concentration (max family share of excess cost)
    if "costo_exceso_mn" in df.columns and total_excess_cost > 0:
        family_excess = df.groupby("cse_prod")["costo_exceso_mn"].sum()
        max_family_share = family_excess.max() / total_excess_cost if total_excess_cost > 0 else 0
        top_family = family_excess.idxmax() if len(family_excess) > 0 else "N/A"
    else:
        max_family_share = 0
        top_family = "N/A"

    # K6: Inventory Aging (median days since last receipt)
    if "fecha_ultimo_ingreso" in df.columns:
        dates = pd.to_datetime(df["fecha_ultimo_ingreso"], errors="coerce")
        valid_dates = dates.dropna()
        if len(valid_dates) > 0:
            today = pd.Timestamp.now()
            aging_days = (today - valid_dates).dt.days.median()
        else:
            aging_days = None
    else:
        aging_days = None

    return {
        "total_products": total_products,
        "total_excess_units": int(df["exceso"].sum()) if "exceso" in df.columns else 0,
        "total_stock_units": int(df["existencia"].sum()) if "existencia" in df.columns else 0,
        # K1
        "avg_months_inventory": round(avg_months, 1) if avg_months else None,
        "avg_months_tl": traffic_light(avg_months, "meses_inventario"),
        "avg_months_color": traffic_color(avg_months, "meses_inventario"),
        # K2
        "total_excess_cost": round(total_excess_cost, 2),
        "excess_cost_tl": traffic_light(total_excess_cost, "excess_cost"),
        "excess_cost_color": traffic_color(total_excess_cost, "excess_cost"),
        # K3
        "zero_sales_count": zero_sales,
        "zero_sales_pct": round(zero_sales_pct, 1),
        "zero_sales_tl": traffic_light(zero_sales_pct, "zero_sales_pct"),
        "zero_sales_color": traffic_color(zero_sales_pct, "zero_sales_pct"),
        # K4
        "avg_excess_ratio": round(avg_excess_ratio, 3) if avg_excess_ratio else 0,
        "excess_ratio_tl": traffic_light(avg_excess_ratio, "excess_ratio"),
        "excess_ratio_color": traffic_color(avg_excess_ratio, "excess_ratio"),
        # K5
        "family_concentration": round(max_family_share, 3),
        "top_family": top_family,
        "family_conc_tl": traffic_light(max_family_share, "family_concentration"),
        "family_conc_color": traffic_color(max_family_share, "family_concentration"),
        # K6
        "aging_days": int(aging_days) if aging_days and not np.isnan(aging_days) else None,
        "aging_tl": traffic_light(aging_days, "aging_days") if aging_days else "⚪",
        "aging_color": traffic_color(aging_days, "aging_days") if aging_days else "#6c757d",
    }


def _empty_kpis() -> dict:
    return {
        "total_products": 0, "total_excess_units": 0, "total_stock_units": 0,
        "avg_months_inventory": None, "avg_months_tl": "⚪", "avg_months_color": "#6c757d",
        "total_excess_cost": 0, "excess_cost_tl": "⚪", "excess_cost_color": "#6c757d",
        "zero_sales_count": 0, "zero_sales_pct": 0, "zero_sales_tl": "⚪", "zero_sales_color": "#6c757d",
        "avg_excess_ratio": 0, "excess_ratio_tl": "⚪", "excess_ratio_color": "#6c757d",
        "family_concentration": 0, "top_family": "N/A", "family_conc_tl": "⚪", "family_conc_color": "#6c757d",
        "aging_days": None, "aging_tl": "⚪", "aging_color": "#6c757d",
    }


# ── Risk Score ─────────────────────────────────────────────────────

def calc_risk_score(row: pd.Series, percentile_rank_cost: float) -> float:
    """
    Calculate Low Rotation Risk Score (0–100) for a single product.
    """
    scores = {}

    # Months of Inventory component
    mi = row.get("meses_inventario")
    if mi is not None and not (isinstance(mi, float) and np.isnan(mi)):
        scores["meses_inventario"] = min(float(mi) / 24 * 100, 100)
    else:
        scores["meses_inventario"] = 100  # Assume worst if unknown

    # Zero Sales component
    ventas = row.get("ventas_periodo", 0)
    scores["zero_sales"] = 100 if (ventas is None or ventas == 0 or (isinstance(ventas, float) and np.isnan(ventas))) else 0

    # Excess Ratio component
    existencia = row.get("existencia", 0)
    exceso = row.get("exceso", 0)
    if existencia and existencia > 0 and exceso:
        ratio = float(exceso) / float(existencia)
        scores["excess_ratio"] = min(ratio * 200, 100)
    else:
        scores["excess_ratio"] = 0

    # Excess Cost Rank component
    scores["excess_cost_rank"] = percentile_rank_cost * 100

    # Aging component
    fecha = row.get("fecha_ultimo_ingreso")
    if fecha and not pd.isna(fecha):
        try:
            date_val = pd.to_datetime(fecha, errors="coerce")
            if date_val and not pd.isna(date_val):
                days = (pd.Timestamp.now() - date_val).days
                scores["aging"] = min(days / 365 * 100, 100)
            else:
                scores["aging"] = 50  # Unknown
        except Exception:
            scores["aging"] = 50
    else:
        scores["aging"] = 50  # Unknown → neutral

    # Weighted composite
    total = 0
    for key, weight in RISK_WEIGHTS.items():
        total += scores.get(key, 0) * weight

    return round(min(total, 100), 1)


def add_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add risk_score column to the DataFrame."""
    if df.empty:
        df["risk_score"] = []
        return df

    # Calculate percentile ranks for excess cost
    if "costo_exceso_mn" in df.columns:
        df["_cost_rank"] = df["costo_exceso_mn"].fillna(0).rank(pct=True)
    else:
        df["_cost_rank"] = 0

    df["risk_score"] = df.apply(
        lambda row: calc_risk_score(row, row.get("_cost_rank", 0)), axis=1
    )
    df = df.drop(columns=["_cost_rank"], errors="ignore")
    return df


# ── Rankings ───────────────────────────────────────────────────────

def top_products_by_risk(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Top N products by risk score (highest risk first)."""
    df = add_risk_scores(df)
    cols = ["cve_prod", "cse_prod", "desc_prod", "existencia", "exceso",
            "cosprom", "costo_exceso_mn", "meses_inventario", "ventas_periodo",
            "risk_score"]
    available = [c for c in cols if c in df.columns]
    return df.nlargest(n, "risk_score")[available].reset_index(drop=True)


def top_products_by_excess_cost(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Top N products by excess cost (highest cost first)."""
    if "costo_exceso_mn" not in df.columns:
        return df.head(0)
    cols = ["cve_prod", "cse_prod", "desc_prod", "existencia", "exceso",
            "cosprom", "costo_exceso_mn", "meses_inventario"]
    available = [c for c in cols if c in df.columns]
    return df.nlargest(n, "costo_exceso_mn")[available].reset_index(drop=True)


def top_products_by_months(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Top N products by months of inventory (highest first)."""
    if "meses_inventario" not in df.columns:
        return df.head(0)
    valid = df[df["meses_inventario"].notna() & (df["meses_inventario"] > 0)]
    cols = ["cve_prod", "cse_prod", "desc_prod", "existencia",
            "cosprom", "meses_inventario", "ventas_periodo"]
    available = [c for c in cols if c in valid.columns]
    return valid.nlargest(n, "meses_inventario")[available].reset_index(drop=True)


def family_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate KPIs per product family."""
    if df.empty:
        return df

    agg = df.groupby("cse_prod").agg(
        productos=("cve_prod", "count"),
        total_existencia=("existencia", "sum"),
        total_exceso=("exceso", "sum"),
        costo_exceso_total=("costo_exceso_mn", "sum"),
        mediana_meses_inv=("meses_inventario", "median"),
        zero_sales=("ventas_periodo", lambda x: (x.fillna(0) == 0).sum()),
    ).reset_index()

    agg["pct_zero_sales"] = (agg["zero_sales"] / agg["productos"] * 100).round(1)
    agg = agg.sort_values("costo_exceso_total", ascending=False)
    return agg


# ── Trend Analysis ─────────────────────────────────────────────────

def excess_trend(excess_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate weekly trend summary from excess_weekly data.
    Returns aggregated totals per snapshot_date.
    """
    if excess_df.empty:
        return excess_df

    trend = excess_df.groupby("snapshot_date").agg(
        total_inv_exceso=("inv_exceso", "sum"),
        total_costo_exceso=("costo_exceso", "sum"),
        product_count=("cve_prod", "nunique"),
    ).reset_index()

    trend = trend.sort_values("snapshot_date")

    # Add week-over-week change
    trend["cambio_inv"] = trend["total_inv_exceso"].pct_change() * 100
    trend["cambio_costo"] = trend["total_costo_exceso"].pct_change() * 100

    return trend


def product_excess_trend(excess_df: pd.DataFrame, cve_prod: str) -> pd.DataFrame:
    """Get excess trend for a specific product."""
    if excess_df.empty:
        return excess_df
    return excess_df[excess_df["cve_prod"] == cve_prod].sort_values("snapshot_date")
