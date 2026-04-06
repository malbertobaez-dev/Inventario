"""
KPI Calculation Engine - Metrics, risk scores, rankings, and alerts.
"""
import numpy as np
import pandas as pd

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import THRESHOLDS, RISK_WEIGHTS


def _to_numeric(series: pd.Series) -> pd.Series:
    """Robust numeric conversion handling commas/currency symbols."""
    return pd.to_numeric(
        series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True),
        errors="coerce",
    )


def traffic_light(value, metric_key: str, higher_is_worse: bool = True) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "white"
    t = THRESHOLDS.get(metric_key)
    if not t:
        return "white"
    if higher_is_worse:
        if value <= t["green"]:
            return "green"
        if value <= t["yellow"]:
            return "yellow"
        return "red"
    if value >= t["green"]:
        return "green"
    if value >= t["yellow"]:
        return "yellow"
    return "red"


def traffic_color(value, metric_key: str, higher_is_worse: bool = True) -> str:
    tl = traffic_light(value, metric_key, higher_is_worse)
    return {"green": "#28A745", "yellow": "#FFC107", "red": "#DC3545"}.get(tl, "#6c757d")


def calc_kpi_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return _empty_kpis()

    data = df.copy()

    # Normalize numeric fields used in calculations
    for col in ["meses_inventario", "costo_exceso_mn", "costo_exist_mn", "ventas_periodo", "exceso", "existencia"]:
        if col in data.columns:
            data[col] = _to_numeric(data[col])

    valid_mi = data["meses_inventario"].dropna() if "meses_inventario" in data.columns else pd.Series(dtype=float)
    avg_months = valid_mi.median() if len(valid_mi) > 0 else None

    total_excess_cost = data["costo_exceso_mn"].sum() if "costo_exceso_mn" in data.columns else 0
    total_excess_cost = 0 if pd.isna(total_excess_cost) else float(total_excess_cost)

    total_exist_cost = data["costo_exist_mn"].sum() if "costo_exist_mn" in data.columns else 0
    total_exist_cost = 0 if pd.isna(total_exist_cost) else float(total_exist_cost)

    total_products = len(data)
    if "ventas_periodo" in data.columns:
        zero_sales = int((data["ventas_periodo"].fillna(0) == 0).sum())
    else:
        zero_sales = 0
    zero_sales_pct = (zero_sales / total_products * 100) if total_products > 0 else 0

    if "exceso" in data.columns and "existencia" in data.columns:
        mask = data["existencia"] > 0
        if mask.any():
            avg_excess_ratio = (data.loc[mask, "exceso"].fillna(0) / data.loc[mask, "existencia"]).median()
            avg_excess_ratio = 0 if pd.isna(avg_excess_ratio) else float(avg_excess_ratio)
        else:
            avg_excess_ratio = 0
    else:
        avg_excess_ratio = 0

    if "costo_exceso_mn" in data.columns and total_excess_cost > 0 and "cse_prod" in data.columns:
        family_excess = data.groupby("cse_prod", dropna=False)["costo_exceso_mn"].sum()
        family_excess = family_excess[family_excess.notna()]
        if len(family_excess) > 0:
            max_family_share = float(family_excess.max() / total_excess_cost) if total_excess_cost > 0 else 0
            top_family_raw = family_excess.idxmax()
            top_family = "Sin familia" if pd.isna(top_family_raw) else str(top_family_raw)
        else:
            max_family_share = 0
            top_family = "N/A"
    else:
        max_family_share = 0
        top_family = "N/A"

    if "fecha_ultimo_ingreso" in data.columns:
        dates = pd.to_datetime(data["fecha_ultimo_ingreso"], errors="coerce")
        valid_dates = dates.dropna()
        if len(valid_dates) > 0:
            today = pd.Timestamp.now()
            aging_days = (today - valid_dates).dt.days.median()
        else:
            aging_days = None
    else:
        aging_days = None

    return {
        "total_products": int(total_products),
        "total_excess_units": int(data["exceso"].fillna(0).sum()) if "exceso" in data.columns else 0,
        "total_stock_units": int(data["existencia"].fillna(0).sum()) if "existencia" in data.columns else 0,
        "total_exist_cost": round(total_exist_cost, 2),
        "avg_months_inventory": round(float(avg_months), 1) if avg_months is not None and not pd.isna(avg_months) else None,
        "avg_months_tl": traffic_light(avg_months, "meses_inventario"),
        "avg_months_color": traffic_color(avg_months, "meses_inventario"),
        "total_excess_cost": round(total_excess_cost, 2),
        "excess_cost_tl": traffic_light(total_excess_cost, "excess_cost"),
        "excess_cost_color": traffic_color(total_excess_cost, "excess_cost"),
        "zero_sales_count": int(zero_sales),
        "zero_sales_pct": round(float(zero_sales_pct), 1),
        "zero_sales_tl": traffic_light(zero_sales_pct, "zero_sales_pct"),
        "zero_sales_color": traffic_color(zero_sales_pct, "zero_sales_pct"),
        "avg_excess_ratio": round(float(avg_excess_ratio), 3) if avg_excess_ratio else 0,
        "excess_ratio_tl": traffic_light(avg_excess_ratio, "excess_ratio"),
        "excess_ratio_color": traffic_color(avg_excess_ratio, "excess_ratio"),
        "family_concentration": round(float(max_family_share), 3),
        "top_family": top_family,
        "family_conc_tl": traffic_light(max_family_share, "family_concentration"),
        "family_conc_color": traffic_color(max_family_share, "family_concentration"),
        "aging_days": int(aging_days) if aging_days is not None and not pd.isna(aging_days) else None,
        "aging_tl": traffic_light(aging_days, "aging_days") if aging_days is not None else "white",
        "aging_color": traffic_color(aging_days, "aging_days") if aging_days is not None else "#6c757d",
    }


def _empty_kpis() -> dict:
    return {
        "total_products": 0,
        "total_excess_units": 0,
        "total_stock_units": 0,
        "total_exist_cost": 0,
        "avg_months_inventory": None,
        "avg_months_tl": "white",
        "avg_months_color": "#6c757d",
        "total_excess_cost": 0,
        "excess_cost_tl": "white",
        "excess_cost_color": "#6c757d",
        "zero_sales_count": 0,
        "zero_sales_pct": 0,
        "zero_sales_tl": "white",
        "zero_sales_color": "#6c757d",
        "avg_excess_ratio": 0,
        "excess_ratio_tl": "white",
        "excess_ratio_color": "#6c757d",
        "family_concentration": 0,
        "top_family": "N/A",
        "family_conc_tl": "white",
        "family_conc_color": "#6c757d",
        "aging_days": None,
        "aging_tl": "white",
        "aging_color": "#6c757d",
    }


def calc_risk_score(row: pd.Series, percentile_rank_cost: float) -> float:
    scores = {}

    mi = row.get("meses_inventario")
    if mi is not None and not (isinstance(mi, float) and np.isnan(mi)):
        scores["meses_inventario"] = min(float(mi) / 24 * 100, 100)
    else:
        scores["meses_inventario"] = 100

    ventas = row.get("ventas_periodo", 0)
    scores["zero_sales"] = 100 if (ventas is None or ventas == 0 or (isinstance(ventas, float) and np.isnan(ventas))) else 0

    existencia = row.get("existencia", 0)
    exceso = row.get("exceso", 0)
    if existencia and existencia > 0 and exceso:
        ratio = float(exceso) / float(existencia)
        scores["excess_ratio"] = min(ratio * 200, 100)
    else:
        scores["excess_ratio"] = 0

    scores["excess_cost_rank"] = percentile_rank_cost * 100

    fecha = row.get("fecha_ultimo_ingreso")
    if fecha and not pd.isna(fecha):
        try:
            date_val = pd.to_datetime(fecha, errors="coerce")
            if date_val and not pd.isna(date_val):
                days = (pd.Timestamp.now() - date_val).days
                scores["aging"] = min(days / 365 * 100, 100)
            else:
                scores["aging"] = 50
        except Exception:
            scores["aging"] = 50
    else:
        scores["aging"] = 50

    total = 0
    for key, weight in RISK_WEIGHTS.items():
        total += scores.get(key, 0) * weight

    return round(min(total, 100), 1)


def add_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        df["risk_score"] = []
        return df

    data = df.copy()
    for col in ["costo_exceso_mn", "meses_inventario", "ventas_periodo", "existencia", "exceso"]:
        if col in data.columns:
            data[col] = _to_numeric(data[col])

    if "costo_exceso_mn" in data.columns:
        data["_cost_rank"] = data["costo_exceso_mn"].fillna(0).rank(pct=True)
    else:
        data["_cost_rank"] = 0

    data["risk_score"] = data.apply(lambda row: calc_risk_score(row, row.get("_cost_rank", 0)), axis=1)
    data = data.drop(columns=["_cost_rank"], errors="ignore")
    return data


def top_products_by_risk(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    data = add_risk_scores(df)
    cols = [
        "cve_prod",
        "cse_prod",
        "desc_prod",
        "existencia",
        "exceso",
        "cosprom",
        "costo_exceso_mn",
        "meses_inventario",
        "ventas_periodo",
        "risk_score",
    ]
    available = [c for c in cols if c in data.columns]
    if "risk_score" not in data.columns:
        return data.head(0)
    data["risk_score"] = _to_numeric(data["risk_score"]).fillna(0)
    return data.nlargest(n, "risk_score")[available].reset_index(drop=True)


def top_products_by_excess_cost(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    if "costo_exceso_mn" not in df.columns:
        return df.head(0)

    data = df.copy()
    data["costo_exceso_mn"] = _to_numeric(data["costo_exceso_mn"])
    data = data.dropna(subset=["costo_exceso_mn"])

    cols = ["cve_prod", "cse_prod", "desc_prod", "existencia", "exceso", "cosprom", "costo_exceso_mn", "meses_inventario"]
    available = [c for c in cols if c in data.columns]

    if data.empty:
        return data.head(0)

    return data.nlargest(n, "costo_exceso_mn")[available].reset_index(drop=True)


def top_products_by_months(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    if "meses_inventario" not in df.columns:
        return df.head(0)

    data = df.copy()
    data["meses_inventario"] = _to_numeric(data["meses_inventario"])
    valid = data[data["meses_inventario"].notna() & (data["meses_inventario"] > 0)]

    cols = ["cve_prod", "cse_prod", "desc_prod", "existencia", "cosprom", "meses_inventario", "ventas_periodo"]
    available = [c for c in cols if c in valid.columns]

    if valid.empty:
        return valid.head(0)

    return valid.nlargest(n, "meses_inventario")[available].reset_index(drop=True)


def family_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    data = df.copy()
    for col in ["existencia", "exceso", "costo_exceso_mn", "meses_inventario", "ventas_periodo"]:
        if col in data.columns:
            data[col] = _to_numeric(data[col])

    if "cse_prod" not in data.columns:
        return data.head(0)

    agg = data.groupby("cse_prod", dropna=False).agg(
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


def excess_trend(excess_df: pd.DataFrame) -> pd.DataFrame:
    if excess_df.empty:
        return excess_df

    trend = excess_df.groupby("snapshot_date").agg(
        total_inv_exceso=("inv_exceso", "sum"),
        total_costo_exceso=("costo_exceso", "sum"),
        product_count=("cve_prod", "nunique"),
    ).reset_index()

    trend = trend.sort_values("snapshot_date")
    trend["cambio_inv"] = trend["total_inv_exceso"].pct_change() * 100
    trend["cambio_costo"] = trend["total_costo_exceso"].pct_change() * 100
    return trend


def product_excess_trend(excess_df: pd.DataFrame, cve_prod: str) -> pd.DataFrame:
    if excess_df.empty:
        return excess_df
    return excess_df[excess_df["cve_prod"] == cve_prod].sort_values("snapshot_date")
