"""
Google Sheets Sync — Push data to Sheets for backup, restore if needed.
"""
import logging
from typing import Optional

import pandas as pd

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import GOOGLE_SHEETS_ENABLED, GOOGLE_SHEET_NAME, CREDENTIALS_PATH

logger = logging.getLogger(__name__)


def _get_client():
    """Get an authorized gspread client."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(str(CREDENTIALS_PATH), scopes=scopes)
        return gspread.authorize(creds)
    except FileNotFoundError:
        logger.warning("Google credentials file not found at %s", CREDENTIALS_PATH)
        return None
    except Exception as e:
        logger.error("Google Sheets auth error: %s", e)
        return None


def _get_or_create_sheet(client, sheet_name: str, worksheet_name: str):
    """Get or create a Google Sheet."""
    try:
        sh = client.open(sheet_name)
    except Exception:
        sh = client.create(sheet_name)
        sh.share("", perm_type="anyone", role="reader")  # Make accessible

    try:
        ws = sh.worksheet(worksheet_name)
    except Exception:
        ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=30)

    return ws


def push_snapshots(df: pd.DataFrame) -> bool:
    """Push snapshots DataFrame to Google Sheets."""
    if not GOOGLE_SHEETS_ENABLED:
        logger.info("Google Sheets sync disabled")
        return False

    client = _get_client()
    if not client:
        return False

    try:
        ws = _get_or_create_sheet(client, GOOGLE_SHEET_NAME, "Snapshots")
        # Clear and write
        ws.clear()
        # Convert to string to avoid serialization issues
        df_str = df.astype(str)
        data = [df_str.columns.tolist()] + df_str.values.tolist()
        ws.update(data)
        logger.info("Pushed %d rows to Google Sheets", len(df))
        return True
    except Exception as e:
        logger.error("Error pushing to Google Sheets: %s", e)
        return False


def push_excess_weekly(df: pd.DataFrame) -> bool:
    """Push weekly excess data to Google Sheets."""
    if not GOOGLE_SHEETS_ENABLED:
        return False

    client = _get_client()
    if not client:
        return False

    try:
        ws = _get_or_create_sheet(client, GOOGLE_SHEET_NAME, "ExcesoSemanal")
        ws.clear()
        df_str = df.astype(str)
        data = [df_str.columns.tolist()] + df_str.values.tolist()
        ws.update(data)
        logger.info("Pushed %d excess rows to Google Sheets", len(df))
        return True
    except Exception as e:
        logger.error("Error pushing excess to Google Sheets: %s", e)
        return False


def restore_from_sheets() -> Optional[pd.DataFrame]:
    """
    Restore snapshots data from Google Sheets.
    Returns DataFrame or None if unavailable.
    """
    if not GOOGLE_SHEETS_ENABLED:
        return None

    client = _get_client()
    if not client:
        return None

    try:
        sh = client.open(GOOGLE_SHEET_NAME)
        ws = sh.worksheet("Snapshots")
        data = ws.get_all_records()
        if data:
            return pd.DataFrame(data)
        return None
    except Exception as e:
        logger.error("Error restoring from Google Sheets: %s", e)
        return None


def sync_all():
    """
    Full sync: push all current data to Google Sheets.
    Called after successful ingestion.
    """
    if not GOOGLE_SHEETS_ENABLED:
        return

    from services.database import get_all_snapshots_df, get_all_excess_weekly_df

    snap_df = get_all_snapshots_df()
    if not snap_df.empty:
        push_snapshots(snap_df)

    excess_df = get_all_excess_weekly_df()
    if not excess_df.empty:
        push_excess_weekly(excess_df)
