from sqlalchemy import Column, String, Float, DateTime, UniqueConstraint
from app.database import Base


class WeatherObservation(Base):
    """
    SQLAlchemy ORM model storing observations locally in SQLite.
    Prevents source API throttling and accelerates queries for internal consumers.
    """
    __tablename__ = "weather_observations"

    # Unique identifier composed of station_id and UTC timestamp
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    station_id = Column(String, index=True, nullable=False)
    station_name = Column(String, nullable=True)
    timestamp_utc = Column(DateTime, index=True, nullable=False)

    # Core meteorological metrics requested
    temperature = Column(Float, nullable=True)  # 'temp' from AEMET response
    pressure = Column(Float, nullable=True)     # 'pres' from AEMET response
    wind_speed = Column(Float, nullable=True)   # 'vel' from AEMET response

    __table_args__ = (
        UniqueConstraint('station_id', 'timestamp_utc', name='uq_station_timestamp'),
    )