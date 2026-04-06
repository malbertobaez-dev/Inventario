"""
SQLite Database Layer — Schema, CRUD, and Query Operations.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    -- Upload history / audit log
    CREATE TABLE IF NOT EXISTS upload_log (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        filename        TEXT    NOT NULL,
        uploaded_at     TEXT    NOT NULL,
        sheet_name      TEXT,
        periodo_meses   INTEGER,
        periodo_inicio  TEXT,
        periodo_fin     TEXT,
        row_count       INTEGER DEFAULT 0,
        status          TEXT    DEFAULT 'success',
        notes           TEXT
    );

    -- Product dimension (deduplicated master)
    CREATE TABLE IF NOT EXISTS products (
        cve_prod        TEXT    PRIMARY KEY,
        cse_prod        TEXT,
        desc_prod       TEXT,
        uni_med         TEXT,
        last_updated    TEXT
    );

    -- Main fact table — one row per product per upload period
    CREATE TABLE IF NOT EXISTS inventory_snapshots (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id           INTEGER REFERENCES upload_log(id),
        cve_prod            TEXT    NOT NULL,
        cse_prod            TEXT,
        desc_prod           TEXT,
        uni_med             TEXT,
        existencia          REAL,
        exceso              REAL,
        cosprom             REAL,
        costo_exceso_mn     REAL,
        costo_exist_mn      REAL,
        ventas_periodo      REAL,
        prom_venta_mensual  REAL,
        meses_inventario    REAL,
        caducidad           TEXT,
        fecha_ultimo_ingreso TEXT,
        comentarios         TEXT,
        periodo_inicio      TEXT,
        periodo_fin         TEXT,
        periodo_meses       INTEGER,
        UNIQUE(cve_prod, periodo_inicio, periodo_fin)
    );

    -- Weekly excess tracking (time-series from "6 Meses" sheet columns)
    CREATE TABLE IF NOT EXISTS excess_weekly (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id       INTEGER REFERENCES upload_log(id),
        cve_prod        TEXT    NOT NULL,
        snapshot_date   TEXT    NOT NULL,
        inv_exceso      REAL,
        costo_exceso    REAL,
        UNIQUE(cve_prod, snapshot_date)
    );

    -- Performance indexes
    CREATE INDEX IF NOT EXISTS idx_snap_cve ON inventory_snapshots(cve_prod);
    CREATE INDEX IF NOT EXISTS idx_snap_cse ON inventory_snapshots(cse_prod);
    CREATE INDEX IF NOT EXISTS idx_snap_periodo ON inventory_snapshots(periodo_inicio, periodo_fin);
    CREATE INDEX IF NOT EXISTS idx_excess_cve ON excess_weekly(cve_prod);
    CREATE INDEX IF NOT EXISTS idx_excess_date ON excess_weekly(snapshot_date);
    """)

    conn.commit()
    conn.close()


# ── Insert Operations ──────────────────────────────────────────────

def log_upload(filename: str, sheet_name: str, periodo_meses: int,
               periodo_inicio: str, periodo_fin: str,
               row_count: int, status: str = "success",
               notes: str = "") -> int:
    """Insert an upload log entry and return its ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO upload_log
            (filename, uploaded_at, sheet_name, periodo_meses,
             periodo_inicio, periodo_fin, row_count, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename, datetime.now().isoformat(), sheet_name,
        periodo_meses, periodo_inicio, periodo_fin,
        row_count, status, notes,
    ))
    upload_id = cur.lastrowid
    conn.commit()
    conn.close()
    return upload_id


def upsert_products(df: pd.DataFrame):
    """Upsert product dimension from a DataFrame."""
    conn = get_connection()
    now = datetime.now().isoformat()
    for _, row in df.iterrows():
        conn.execute("""
            INSERT INTO products (cve_prod, cse_prod, desc_prod, uni_med, last_updated)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(cve_prod) DO UPDATE SET
                cse_prod = excluded.cse_prod,
                desc_prod = excluded.desc_prod,
                uni_med = excluded.uni_med,
                last_updated = excluded.last_updated
        """, (
            row.get("cve_prod"), row.get("cse_prod"),
            row.get("desc_prod"), row.get("uni_med"), now,
        ))
    conn.commit()
    conn.close()


def insert_snapshots(df: pd.DataFrame, upload_id: int) -> int:
    """Insert inventory snapshots, skip duplicates. Returns inserted count."""
    conn = get_connection()
    inserted = 0
    for _, row in df.iterrows():
        try:
            conn.execute("""
                INSERT INTO inventory_snapshots
                    (upload_id, cve_prod, cse_prod, desc_prod, uni_med,
                     existencia, exceso, cosprom, costo_exceso_mn, costo_exist_mn,
                     ventas_periodo, prom_venta_mensual, meses_inventario,
                     caducidad, fecha_ultimo_ingreso, comentarios,
                     periodo_inicio, periodo_fin, periodo_meses)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                upload_id,
                row.get("cve_prod"), row.get("cse_prod"),
                row.get("desc_prod"), row.get("uni_med"),
                row.get("existencia"), row.get("exceso"),
                row.get("cosprom"), row.get("costo_exceso_mn"),
                row.get("costo_exist_mn"),
                row.get("ventas_periodo"), row.get("prom_venta_mensual"),
                row.get("meses_inventario"),
                row.get("caducidad"), row.get("fecha_ultimo_ingreso"),
                row.get("comentarios"),
                row.get("periodo_inicio"), row.get("periodo_fin"),
                row.get("periodo_meses"),
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # Duplicate — skip
    conn.commit()
    conn.close()
    return inserted


def insert_excess_weekly(df: pd.DataFrame, upload_id: int) -> int:
    """Insert weekly excess snapshots. Returns inserted count."""
    conn = get_connection()
    inserted = 0
    for _, row in df.iterrows():
        try:
            conn.execute("""
                INSERT INTO excess_weekly
                    (upload_id, cve_prod, snapshot_date, inv_exceso, costo_exceso)
                VALUES (?, ?, ?, ?, ?)
            """, (
                upload_id,
                row.get("cve_prod"), row.get("snapshot_date"),
                row.get("inv_exceso"), row.get("costo_exceso"),
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return inserted


# ── Query Operations ───────────────────────────────────────────────

def get_snapshots(periodo_meses: Optional[int] = None,
                  cse_prod: Optional[str] = None) -> pd.DataFrame:
    """Retrieve inventory snapshots with optional filters."""
    conn = get_connection()
    query = "SELECT * FROM inventory_snapshots WHERE 1=1"
    params = []
    if periodo_meses:
        query += " AND periodo_meses = ?"
        params.append(periodo_meses)
    if cse_prod:
        query += " AND cse_prod = ?"
        params.append(cse_prod)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_latest_snapshots(periodo_meses: Optional[int] = None) -> pd.DataFrame:
    """Get the latest snapshot per product (most recent periodo_fin)."""
    conn = get_connection()
    query = """
        SELECT s.* FROM inventory_snapshots s
        INNER JOIN (
            SELECT cve_prod, MAX(periodo_fin) as max_fin
            FROM inventory_snapshots
            {where}
            GROUP BY cve_prod
        ) latest ON s.cve_prod = latest.cve_prod
                 AND s.periodo_fin = latest.max_fin
    """
    params = []
    where = ""
    if periodo_meses:
        where = "WHERE periodo_meses = ?"
        params.append(periodo_meses)
    query = query.format(where=where)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_excess_weekly() -> pd.DataFrame:
    """Retrieve all weekly excess tracking data."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM excess_weekly ORDER BY snapshot_date", conn
    )
    conn.close()
    return df


def get_upload_history() -> pd.DataFrame:
    """Retrieve upload log history."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM upload_log ORDER BY uploaded_at DESC", conn
    )
    conn.close()
    return df


def get_families() -> list:
    """Return distinct product families."""
    conn = get_connection()
    cur = conn.execute(
        "SELECT DISTINCT cse_prod FROM products WHERE cse_prod IS NOT NULL ORDER BY cse_prod"
    )
    families = [row[0] for row in cur.fetchall()]
    conn.close()
    return families


def get_total_records() -> int:
    """Return total records in inventory_snapshots."""
    conn = get_connection()
    cur = conn.execute("SELECT COUNT(*) FROM inventory_snapshots")
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_all_snapshots_df() -> pd.DataFrame:
    """Export entire snapshots table as DataFrame (for Google Sheets sync)."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM inventory_snapshots", conn)
    conn.close()
    return df


def get_all_excess_weekly_df() -> pd.DataFrame:
    """Export entire excess_weekly table as DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM excess_weekly", conn)
    conn.close()
    return df


def db_exists() -> bool:
    """Check if the database file exists and has tables."""
    if not DB_PATH.exists():
        return False
    try:
        conn = get_connection()
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_snapshots'"
        )
        result = cur.fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False


# Auto-initialize on import
init_db()
