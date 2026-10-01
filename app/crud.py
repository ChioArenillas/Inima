from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

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

    # If records exist, treat as cache hit to protect upstream quota
    return result, True


def save_observations(db: Session, records: List[Dict[str, Any]]) -> int:
    """
    Inserts observations ignoring duplicates based on (station_id, timestamp_utc).
    """
    if not records:
        return 0

    inserted_count = 0
    for item in records:
        exists = (
            db.query(WeatherObservation.id)
            .filter(
                and_(
                    WeatherObservation.station_id == item["station_id"],
                    WeatherObservation.timestamp_utc == item["timestamp_utc"]
                )
            )
            .first()
        )
        if not exists:
            obs = WeatherObservation(
                station_id=item["station_id"],
                station_name=item["station_name"],
                timestamp_utc=item["timestamp_utc"],
                temperature=item.get("temperature"),
                pressure=item.get("pressure"),
                wind_speed=item.get("wind_speed"),
            )
            db.add(obs)
            inserted_count += 1

    db.commit()
    return inserted_count