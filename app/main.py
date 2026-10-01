import logging
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.crud import get_cached_observations
from app.services.aemet_client import fetch_and_store_aemet_data, STATION_CODES
from app.services.aggregator import aggregate_weather_data, calculate_feasibility_metrics

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("wind_farm_api")

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GS Inima Antarctica Wind Study API",
    description="High-availability operational API for Antarctica Wind Generation Analysis & Intraday Trading Desk.",
    version="2.0.0"
)

# Enable CORS for the React/TypeScript frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATION_MAP = {
    "Meteo Station Gabriel de Castilla": "89064",
    "Gabriel de Castilla": "89064",
    "89064": "89064",
    "Meteo Station Juan Carlos I": "89070",
    "Juan Carlos I": "89070",
    "89070": "89070",
}


@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok", "service": "antarctica-wind-api"}


@app.get(
    "/api/antartida/datos/fechaini/{fechalniStr}/fechafin/{fechaFinStr}/estacion/{identificacion}",
    summary="Retrieve Antarctica time-series observations"
)
def get_antarctica_data(
    fechalniStr: str,
    fechaFinStr: str,
    identificacion: str,
    location: Optional[str] = Query("Europe/Madrid", description="Input location timezone or shift"),
    aggregation: Optional[str] = Query("None", description="Aggregation level: None, Hourly, Daily, Monthly"),
    data_types: Optional[List[str]] = Query(None, description="Select metrics: temperature, pressure, speed"),
    db: Session = Depends(get_db)
):
    """
    Core challenge endpoint: Retrieves timeseries from SQLite cache or AEMET upstream,
    respecting DST, location boundaries, and selected metrics.
    """
    station_code = STATION_MAP.get(identificacion, identificacion)

    logger.info(
        f"Incoming request: Station={identificacion} ({station_code}), "
        f"Range=[{fechalniStr} -> {fechaFinStr}], Aggregation={aggregation}, Location={location}"
    )

    # 1. Cache-aside check in SQLite (Protecting AEMET quota for intraday traders)
    cached_records, cache_hit = get_cached_observations(db, station_code, fechalniStr, fechaFinStr)

    if not cache_hit:
        logger.info(f"Cache miss for {station_code}. Synchronizing with upstream AEMET API...")
        try:
            fetch_and_store_aemet_data(db, station_code, fechalniStr, fechaFinStr)
            cached_records, _ = get_cached_observations(db, station_code, fechalniStr, fechaFinStr)
        except Exception as e:
            logger.error(f"Upstream synchronization error: {str(e)}")
            if not cached_records:
                raise HTTPException(status_code=502, detail=f"AEMET upstream error: {str(e)}")

    # 2. Process timezone conversions, calendar boundaries, and aggregations
    return aggregate_weather_data(
        records=cached_records,
        aggregation=aggregation,
        data_types=data_types,
        location=location
    )


@app.get(
    "/api/antartida/feasibility-assessment",
    summary="Wind Farm Feasibility & Aerodynamic Assessment"
)
def get_feasibility_assessment(
    fechainiStr: str,
    fechaFinStr: str,
    identificacion: str,
    db: Session = Depends(get_db)
):
    """
    Answers the Business Development team's feasibility question:
    Evaluates wind generation window, air density, storm risk, and blade icing.
    """
    station_code = STATION_MAP.get(identificacion, identificacion)
    cached_records, cache_hit = get_cached_observations(db, station_code, fechainiStr, fechaFinStr)

    if not cache_hit:
        try:
            fetch_and_store_aemet_data(db, station_code, fechainiStr, fechaFinStr)
            cached_records, _ = get_cached_observations(db, station_code, fechainiStr, fechaFinStr)
        except Exception as e:
            logger.error(f"Error fetching data for assessment: {e}")

    metrics = calculate_feasibility_metrics(cached_records)
    metrics["cache_source"] = "SQLite Local Cache" if cache_hit else "AEMET Live Sync"
    return metrics