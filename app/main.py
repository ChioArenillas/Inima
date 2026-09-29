from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import logging

from app.database import Base, engine, get_db
from app.models import WeatherObservation
from app.services.aemet_client import AEMETClient, STATION_CODES
from app.services.aggregator import aggregate_weather_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GS Inima Antarctica Wind Study API",
    description="High-availability API for historical meteorological data in Antarctica.",
    version="1.0.0"
)

# Enable CORS for the React/TypeScript frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aemet_client = AEMETClient()


@app.get(
    "/api/antartida/datos/fechaini/{fechalniStr}/fechafin/{fechaFinStr}/estacion/{identificacion}",
    summary="Retrieve Antarctica time-series observations"
)
async def get_antarctica_data(
    fechalniStr: str,
    fechaFinStr: str,
    identificacion: str,
    aggregation: Optional[str] = Query(
        "None", description="Aggregation level: None, Hourly, Daily, Monthly"
    ),
    data_types: Optional[List[str]] = Query(
        None, description="Select metrics: temperature, pressure, speed"
    ),
    db: Session = Depends(get_db)
):
    """
    Retrieves time-series data using a local cache-aside strategy (SQLite)
    to minimize redundant upstream requests to AEMET.
    """
    station_id = STATION_CODES.get(identificacion, identificacion)

    # 1. Query local cache first
    cached_records = (
        db.query(WeatherObservation)
        .filter(WeatherObservation.station_id == station_id)
        .all()
    )

    # 2. If data is missing locally, fetch from AEMET and persist
    if not cached_records:
        logger.info(f"Cache miss for station {station_id}. Requesting upstream AEMET API...")
        raw_data = await aemet_client.fetch_antarctica_data(
            fechalniStr, fechaFinStr, station_id
        )

        station_names = {
            "89064": "Meteo Station Gabriel de Castilla",
            "89060": "Meteo Station Juan Carlos I"
        }

        for item in raw_data:
            fhora_str = item.get("fhora")
            if not fhora_str:
                continue

            dt = datetime.fromisoformat(fhora_str.replace("Z", "+00:00"))
            obs_id = f"{station_id}_{dt.isoformat()}"

            if not db.query(WeatherObservation).filter_by(id=obs_id).first():
                new_observation = WeatherObservation(
                    id=obs_id,
                    station_id=station_id,
                    station_name=item.get("nombre", station_names.get(station_id, "Unknown Station")),
                    timestamp_utc=dt,
                    temperature=float(item["temp"]) if item.get("temp") is not None else None,
                    pressure=float(item["pres"]) if item.get("pres") is not None else None,
                    wind_speed=float(item["vel"]) if item.get("vel") is not None else None,
                )
                db.add(new_observation)

        db.commit()

        # Reload persisted data from SQLite
        cached_records = (
            db.query(WeatherObservation)
            .filter(WeatherObservation.station_id == station_id)
            .all()
        )

    # 3. Serialize records for processing
    formatted_records = [
        {
            "station_id": r.station_id,
            "station_name": r.station_name,
            "timestamp_utc": r.timestamp_utc,
            "temperature": r.temperature,
            "pressure": r.pressure,
            "wind_speed": r.wind_speed,
        }
        for r in cached_records
    ]

    # 4. Apply time aggregation and Europe/Madrid timezone conversion
    return aggregate_weather_data(formatted_records, aggregation, data_types)