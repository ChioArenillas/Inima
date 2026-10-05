from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.models import WeatherObservation


def get_cached_observations(
    db: Session,
    station_code: str,
    start_str: str,
    end_str: str
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Retrieves observations from the local SQLite cache.
    Returns (records, is_cache_hit).
    Evaluates cache hit if data exists across the queried interval.
    """
    # Parse input strings to UTC datetime objects
    dt_start = datetime.fromisoformat(start_str)
    if dt_start.tzinfo is None:
        dt_start = dt_start.replace(tzinfo=timezone.utc)
    else:
        dt_start = dt_start.astimezone(timezone.utc)

    dt_end = datetime.fromisoformat(end_str)
    if dt_end.tzinfo is None:
        dt_end = dt_end.replace(tzinfo=timezone.utc)
    else:
        dt_end = dt_end.astimezone(timezone.utc)

    records = (
        db.query(WeatherObservation)
        .filter(
            and_(
                WeatherObservation.station_id == station_code,
                WeatherObservation.timestamp_utc >= dt_start,
                WeatherObservation.timestamp_utc <= dt_end
            )
        )
        .order_by(WeatherObservation.timestamp_utc.asc())
        .all()
    )

    if not records:
        return [], False

    # Convert SQLAlchemy instances to dictionaries
    result = [
        {
            "station_id": r.station_id,
            "station_name": r.station_name,
            "timestamp_utc": r.timestamp_utc,
            "temperature": r.temperature,
            "pressure": r.pressure,
            "wind_speed": r.wind_speed,
        }
        for r in records
    ]

    return result, True


def save_observations(db: Session, records: List[Dict[str, Any]]) -> int:
    """
    Inserts observations ignoring duplicates natively via SQLite ON CONFLICT DO NOTHING.
    Guarantees idempotency and avoids unique constraint violations.
    """
    if not records:
        return 0

    # 1. Deduplicar en memoria por si el payload de AEMET trae elementos repetidos
    unique_records_dict = {}
    for item in records:
        key = (item["station_id"], item["timestamp_utc"])
        if key not in unique_records_dict:
            unique_records_dict[key] = {
                "station_id": item["station_id"],
                "station_name": item.get("station_name"),
                "timestamp_utc": item["timestamp_utc"],
                "temperature": item.get("temperature"),
                "pressure": item.get("pressure"),
                "wind_speed": item.get("wind_speed"),
            }

    unique_records = list(unique_records_dict.values())
    if not unique_records:
        return 0

    # 2. Insert nativo atómico con ON CONFLICT DO NOTHING en SQLite
    stmt = sqlite_insert(WeatherObservation).values(unique_records)
    stmt = stmt.on_conflict_do_nothing(
        index_elements=["station_id", "timestamp_utc"]
    )

    result = db.execute(stmt)
    db.commit()
    return result.rowcount