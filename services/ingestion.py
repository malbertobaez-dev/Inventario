"""
Excel Ingestion Pipeline — Parse, validate, normalize, and persist.
"""
import re
from datetime import datetime
from typing import Tuple, Optional

import pandas as pd

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import COLUMN_MAP_PATTERNS, VENTAS_PREFIX, INV_EXCE_PREFIX, COSTO_EXCE_PREFIX
from services.database import (
    log_upload, upsert_products, insert_snapshots,
    insert_excess_weekly, get_connection,
)


# ── Sheet Metadata ─────────────────────────────────────────────────

SHEET_CONFIG = {
    "Mar2025 a Feb2026": {"periodo_inicio": "2025-03", "periodo_fin": "2026-02", "meses": 12},
    "12 Meses":          {"periodo_inicio": "2025-03", "periodo_fin": "2026-02", "meses": 12},
    "Sep2025 a Feb2026": {"periodo_inicio": "2025-09", "periodo_fin": "2026-02", "meses": 6},
    "6 Meses":           {"periodo_inicio": "2025-09", "periodo_fin": "2026-02", "meses": 6},
    "Info junta semanal": {"periodo_inicio": "2025-09", "periodo_fin": "2026-02", "meses": 6},
}


def _normalize_column(col: str) -> str:
    """Normalize a column name to lowercase, stripped."""
    return str(col).strip().lower()


def _map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns using the mapping patterns."""
    rename_map = {}
    ventas_col = None
    inv_exce_cols = {}
    costo_exce_cols = {}

    for col in df.columns:
        norm = _normalize_column(col)
        if norm in COLUMN_MAP_PATTERNS:
            rename_map[col] = COLUMN_MAP_PATTERNS[norm]
        elif norm.startswith(VENTAS_PREFIX):
            rename_map[col] = "ventas_periodo"
            ventas_col = col
        elif norm.startswith(INV_EXCE_PREFIX):
            # Extract date: "inv exce al 9mar2026" → "2026-03-09"
            date_str = _parse_snapshot_date(norm)
            if date_str:
                inv_exce_cols[col] = date_str
        elif norm.startswith(COSTO_EXCE_PREFIX):
            date_str = _parse_snapshot_date(norm)
            if date_str:
                costo_exce_cols[col] = date_str

    df = df.rename(columns=rename_map)
    return df, inv_exce_cols, costo_exce_cols


def _parse_snapshot_date(text: str) -> Optional[str]:
    """Parse dates like '9mar2026' or '09mar2026' from column names."""
    MONTH_MAP = {
        "ene": "01", "feb": "02", "mar": "03", "abr": "04",
        "may": "05", "jun": "06", "jul": "07", "ago": "08",
        "sep": "09", "oct": "10", "nov": "11", "dic": "12",
    }
    match = re.search(r"(\d{1,2})\s*(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\s*(\d{4})", text)
    if match:
        day = int(match.group(1))
        month = MONTH_MAP.get(match.group(2))
        year = match.group(3)
        if month:
            return f"{year}-{month}-{day:02d}"
    return None


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Remove empty rows and clean data types."""
    # Drop rows where cve_prod is null (section/empty rows)
    df = df.dropna(subset=["cve_prod"])
    df = df[df["cve_prod"].astype(str).str.strip() != ""]

    # Clean numeric columns
    numeric_cols = [
        "existencia", "exceso", "cosprom", "costo_exceso_mn",
        "costo_exist_mn", "ventas_periodo", "prom_venta_mensual",
        "meses_inventario",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Handle infinite values in meses_inventario
    if "meses_inventario" in df.columns:
        df["meses_inventario"] = df["meses_inventario"].replace(
            [float("inf"), float("-inf")], None
        )

    # Clean date column
    if "fecha_ultimo_ingreso" in df.columns:
        df["fecha_ultimo_ingreso"] = pd.to_datetime(
            df["fecha_ultimo_ingreso"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    # Recalculate prom_venta_mensual if missing
    if "prom_venta_mensual" not in df.columns and "ventas_periodo" in df.columns:
        df["prom_venta_mensual"] = None  # Will be filled by periodo_meses

    return df.reset_index(drop=True)


def _extract_excess_timeseries(
    df_raw: pd.DataFrame,
    inv_exce_cols: dict,
    costo_exce_cols: dict,
) -> pd.DataFrame:
    """Pivot weekly excess columns into a long-format timeseries."""
    rows = []
    for _, product_row in df_raw.iterrows():
        cve = product_row.get("cve_prod")
        if not cve or pd.isna(cve):
            continue
        for orig_col, date_str in inv_exce_cols.items():
            inv_val = product_row.get(orig_col)
            costo_val = None
            # Find matching costo column for this date
            for costo_col, costo_date in costo_exce_cols.items():
                if costo_date == date_str:
                    costo_val = product_row.get(costo_col)
                    break
            rows.append({
                "cve_prod": cve,
                "snapshot_date": date_str,
                "inv_exceso": pd.to_numeric(inv_val, errors="coerce"),
                "costo_exceso": pd.to_numeric(costo_val, errors="coerce"),
            })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def validate_file(file_path: str) -> Tuple[bool, str, list]:
    """
    Validate an Excel file structure.
    Returns: (is_valid, message, list_of_sheet_names)
    """
    try:
        xl = pd.ExcelFile(file_path, engine="openpyxl")
        sheets = xl.sheet_names
        recognized = [s for s in sheets if s in SHEET_CONFIG]
        if not recognized:
            return False, f"No se reconocen las hojas. Esperadas: {list(SHEET_CONFIG.keys())}", []
        return True, f"Archivo válido. {len(recognized)} hojas reconocidas.", recognized
    except Exception as e:
        return False, f"Error al leer archivo: {str(e)}", []


def ingest_sheet(
    file_path: str,
    sheet_name: str,
    filename: str,
) -> Tuple[int, int, str]:
    """
    Ingest a single sheet from an Excel file.
    Returns: (snapshot_rows_inserted, excess_rows_inserted, message)
    """
    config = SHEET_CONFIG.get(sheet_name)
    if not config:
        return 0, 0, f"Hoja '{sheet_name}' no reconocida"

    # Read the sheet
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

    # Map columns
    df, inv_exce_cols, costo_exce_cols = _map_columns(df_raw)

    # Clean
    df = _clean_dataframe(df)

    if df.empty:
        return 0, 0, "No se encontraron datos válidos"

    # Add period metadata
    df["periodo_inicio"] = config["periodo_inicio"]
    df["periodo_fin"] = config["periodo_fin"]
    df["periodo_meses"] = config["meses"]

    # Recalculate monthly average if needed
    if "prom_venta_mensual" in df.columns:
        mask = df["prom_venta_mensual"].isna() & df["ventas_periodo"].notna()
        df.loc[mask, "prom_venta_mensual"] = (
            df.loc[mask, "ventas_periodo"] / config["meses"]
        )

    # Recalculate months of inventory where missing or invalid
    if "meses_inventario" in df.columns:
        mask = df["meses_inventario"].isna() & df["prom_venta_mensual"].notna()
        valid_avg = df.loc[mask, "prom_venta_mensual"] > 0
        df.loc[mask & valid_avg, "meses_inventario"] = (
            df.loc[mask & valid_avg, "existencia"] /
            df.loc[mask & valid_avg, "prom_venta_mensual"]
        )

    # Log upload
    upload_id = log_upload(
        filename=filename,
        sheet_name=sheet_name,
        periodo_meses=config["meses"],
        periodo_inicio=config["periodo_inicio"],
        periodo_fin=config["periodo_fin"],
        row_count=len(df),
    )

    # Upsert products dimension
    upsert_products(df[["cve_prod", "cse_prod", "desc_prod", "uni_med"]].drop_duplicates())

    # Insert snapshots
    snap_count = insert_snapshots(df, upload_id)

    # Extract and insert weekly excess timeseries
    excess_count = 0
    if inv_exce_cols:
        excess_df = _extract_excess_timeseries(df_raw, inv_exce_cols, costo_exce_cols)
        if not excess_df.empty:
            # Need to map cve_prod from raw data
            # df_raw might not have normalized column names
            # Re-read cve_prod from the raw first column
            raw_cve_col = df_raw.columns[0]
            cve_series = df_raw[raw_cve_col].dropna()
            excess_df_clean = excess_df.dropna(subset=["cve_prod"])
            if not excess_df_clean.empty:
                excess_count = insert_excess_weekly(excess_df_clean, upload_id)

    msg = f"✅ {snap_count} productos, {excess_count} registros semanales"
    return snap_count, excess_count, msg


def ingest_file(file_path: str, filename: str, sheets: Optional[list] = None) -> dict:
    """
    Ingest all recognized sheets from an Excel file.
    Returns summary dict.
    """
    is_valid, msg, available = validate_file(file_path)
    if not is_valid:
        return {"success": False, "message": msg}

    target_sheets = sheets if sheets else available
    results = {}
    total_snaps = 0
    total_excess = 0

    for sheet in target_sheets:
        if sheet in SHEET_CONFIG:
            snaps, excess, info = ingest_sheet(file_path, sheet, filename)
            results[sheet] = {"snapshots": snaps, "excess": excess, "info": info}
            total_snaps += snaps
            total_excess += excess

    return {
        "success": True,
        "message": f"Archivo procesado: {total_snaps} productos, {total_excess} registros semanales",
        "sheets": results,
        "total_snapshots": total_snaps,
        "total_excess": total_excess,
    }
