"""
Application configuration and brand constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "inventario.db"
CREDENTIALS_PATH = BASE_DIR / "config" / "credentials.json"

# Ensure db directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Google Sheets ──────────────────────────────────────────────────
GOOGLE_SHEETS_ENABLED = os.getenv("GOOGLE_SHEETS_ENABLED", "false").lower() == "true"
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Inventario_Backup")

# ── Brand Colors ───────────────────────────────────────────────────
COLOR_PRIMARY = "#002D5A"       # Deep Blue
COLOR_SECONDARY = "#007BFF"     # Electric Blue
COLOR_ACCENT = "#FFCC00"        # Energy Yellow
COLOR_NEUTRAL = "#F4F4F4"       # Technical Gray
COLOR_WHITE = "#FFFFFF"
COLOR_DARK_TEXT = "#1A1A2E"
COLOR_SUCCESS = "#28A745"
COLOR_WARNING = "#FFC107"
COLOR_DANGER = "#DC3545"

# ── KPI Thresholds ────────────────────────────────────────────────
THRESHOLDS = {
    "meses_inventario": {"green": 6, "yellow": 12},
    "excess_cost": {"green": 50_000, "yellow": 200_000},
    "zero_sales_pct": {"green": 5, "yellow": 15},
    "excess_ratio": {"green": 0.20, "yellow": 0.50},
    "family_concentration": {"green": 0.15, "yellow": 0.30},
    "aging_days": {"green": 90, "yellow": 180},
}

# ── Risk Score Weights ─────────────────────────────────────────────
RISK_WEIGHTS = {
    "meses_inventario": 0.30,
    "zero_sales": 0.25,
    "excess_ratio": 0.20,
    "excess_cost_rank": 0.15,
    "aging": 0.10,
}

# ── Expected Excel Columns (core, normalized) ─────────────────────
EXPECTED_COLUMNS = [
    "cve_prod", "cse_prod", "existencia", "cosprom",
    "desc_prod", "uni_med", "ventas_periodo",
    "prom_venta_mensual", "meses_inventario",
]

# ── Column Name Mapping (from raw Excel → normalized) ─────────────
COLUMN_MAP_PATTERNS = {
    "cve_prod": "cve_prod",
    "cse_prod": "cse_prod",
    "existencia": "existencia",
    "exceso": "exceso",
    "cosprom": "cosprom",
    "costo_exceso_m.n.": "costo_exceso_mn",
    "costo_exist_m.n.": "costo_exist_mn",
    "desc_prod": "desc_prod",
    "uni_med": "uni_med",
    "prom de venta mensual": "prom_venta_mensual",
    "meses de inventario": "meses_inventario",
    "exceso en meses de inventario": "meses_inventario",
    "caducidad": "caducidad",
    "fecha de ultimo ingreso": "fecha_ultimo_ingreso",
    "comentarios": "comentarios",
}

# Dynamic column patterns (prefix-match)
VENTAS_PREFIX = "ventas"
INV_EXCE_PREFIX = "inv exce al"
COSTO_EXCE_PREFIX = "costo exceso al"

# ── Time Window Options ────────────────────────────────────────────
TIME_WINDOWS = {
    "1 Mes": 1,
    "3 Meses": 3,
    "6 Meses": 6,
    "12 Meses": 12,
}
