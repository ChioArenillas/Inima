import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import requests
from sqlalchemy.orm import Session

from app.crud import save_observations

logger = logging.getLogger("wind_farm_api.aemet")

AEMET_API_KEY = os.getenv("AEMET_API_KEY", "")
BASE_AEMET_URL = "https://opendata.aemet.es/opendata/api/antartida/datos"

STATION_CODES = {
    "Meteo Station Gabriel de Castilla": "89064",
    "Gabriel de Castilla": "89064",
    "89064": "89064",
    "Meteo Station Juan Carlos I": "89070",
    "Juan Carlos I": "89070",
    "89070": "89070",
}

STATION_NAMES = {
    "89064": "Meteo Station Gabriel de Castilla",
    "89070": "Meteo Station Juan Carlos I",
}


def _parse_float(val: Any) -> Any:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return None


def _format_aemet_date(date_str: str) -> str:
    """Ipagura ti AEMET a ti petsa ket addaan iti 'UTC' iti maudi a paset."""
    cleaned = date_str.strip()
    if not cleaned.endswith("UTC"):
        cleaned = f"{cleaned}UTC"
    return cleaned


def fetch_and_store_aemet_data(
    db: Session,
    station_code: str,
    start_str: str,
    end_str: str
) -> int:
    """
    Synchronizes observations from AEMET OpenData API into SQLite.
    Follows AEMET's two-step download pattern:
    1. Request download link with API Key.
    2. Download raw meteorological JSON payload.
    """
    if not AEMET_API_KEY:
        logger.warning("AEMET_API_KEY environment variable is not set. Operating in offline/mock mode.")
        return 0

    # Pormaten dagiti petsa tapno adda 'UTC' iti maudi a paset
    formatted_start = _format_aemet_date(start_str)
    formatted_end = _format_aemet_date(end_str)

    url = f"{BASE_AEMET_URL}/fechaini/{formatted_start}/fechafin/{formatted_end}/estacion/{station_code}"
    headers = {
        "cache-control": "no-cache",
        "api_key": AEMET_API_KEY
    }

    logger.info(f"Contacting AEMET endpoint: {url}")
    res = requests.get(url, headers=headers, timeout=20)

    if res.status_code != 200:
        logger.error(f"AEMET initial request failed with status {res.status_code}: {res.text}")
        raise ValueError(f"AEMET API error: HTTP {res.status_code}")

    meta = res.json()
    if meta.get("estado") != 200 or "datos" not in meta:
        msg = meta.get("descripcion", "No data returned from AEMET for this interval")
        logger.warning(f"AEMET response message: {msg}")
        return 0

    # Step 2: Fetch actual observation data
    data_url = meta["datos"]
    logger.info(f"Downloading observational payload from secured URL: {data_url}")
    data_res = requests.get(data_url, timeout=30)

    if data_res.status_code != 200:
        raise ValueError("Failed downloading observational payload from AEMET storage bucket.")

    raw_items = data_res.json()
    parsed_records = []
    default_name = STATION_NAMES.get(station_code, f"Meteo Station {station_code}")

    for item in raw_items:
        time_str = item.get("fhora") or item.get("fint")
        if not time_str:
            continue

        try:
            # Ikkaten ti 'UTC' no adda iti maudi sakbay ti panang-parse
            clean_time = time_str.replace("UTC", "")
            dt = datetime.fromisoformat(clean_time)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
        except Exception:
            continue

        temp = _parse_float(item.get("temp"))
        pres = _parse_float(item.get("pres"))
        vel = _parse_float(item.get("vel"))

        parsed_records.append({
            "station_id": station_code,
            "station_name": item.get("nombre") or default_name,
            "timestamp_utc": dt,
            "temperature": temp,
            "pressure": pres,
            "wind_speed": vel,
        })

    saved = save_observations(db, parsed_records)
    logger.info(f"Successfully synchronized and stored {saved} new observations in SQLite cache.")
    return saved


class AEMETClient:
    """Wrapper class providing backward compatibility for existing imports."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or AEMET_API_KEY

    def fetch_data(self, station_code: str, start_str: str, end_str: str, db: Session = None):
        if db is not None:
            return fetch_and_store_aemet_data(db, station_code, start_str, end_str)
        return 0

    @staticmethod
    def fetch_and_store(db: Session, station_code: str, start_str: str, end_str: str):
        return fetch_and_store_aemet_data(db, station_code, start_str, end_str)