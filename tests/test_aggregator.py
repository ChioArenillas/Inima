import pytest
from app.services.aggregator import aggregate_weather_data


def test_time_aggregation_hourly():
    """
    Verifies that 10-minute interval observations are grouped 
    into a single hourly record using arithmetic means.
    """
    records = [
        {
            "station_id": "89064",
            "station_name": "Meteo Station Gabriel de Castilla",
            "timestamp_utc": "2024-01-01T10:00:00Z",
            "temperature": 1.0,
            "pressure": 990.0,
            "wind_speed": 10.0,
        },
        {
            "station_id": "89064",
            "station_name": "Meteo Station Gabriel de Castilla",
            "timestamp_utc": "2024-01-01T10:10:00Z",
            "temperature": 3.0,
            "pressure": 992.0,
            "wind_speed": 12.0,
        },
    ]

    result = aggregate_weather_data(records, aggregation="Hourly")

    assert len(result) == 1
    # Average of 1.0 and 3.0
    assert result[0]["Temperature (°C)"] == 2.0
    # Average of 990.0 and 992.0
    assert result[0]["Pressure (hpa)"] == 991.0
    # Average of 10.0 and 12.0
    assert result[0]["Speed (m/s)"] == 11.0


def test_dst_transition_offsets():
    """
    Verifies that the API properly applies Europe/Madrid timezone offsets:
    - Summer time (CEST): UTC+2
    - Winter time (CET): UTC+1
    """
    records = [
        # Summer date (July) -> Expecting +02:00
        {
            "station_id": "89064",
            "station_name": "Meteo Station Gabriel de Castilla",
            "timestamp_utc": "2024-07-15T12:00:00Z",
            "temperature": -2.0,
            "pressure": 985.0,
            "wind_speed": 15.0,
        },
        # Winter date (January) -> Expecting +01:00
        {
            "station_id": "89064",
            "station_name": "Meteo Station Gabriel de Castilla",
            "timestamp_utc": "2024-01-15T12:00:00Z",
            "temperature": -5.0,
            "pressure": 980.0,
            "wind_speed": 8.0,
        },
    ]

    result = aggregate_weather_data(records, aggregation="None")

    assert len(result) == 2

    # Summer record check (+02:00)
    summer_dt = result[0]["Datetime"]
    assert "+02:00" in summer_dt

    # Winter record check (+01:00)
    winter_dt = result[1]["Datetime"]
    assert "+01:00" in winter_dt


def test_selective_data_types():
    """
    Verifies that passing specific metrics returns only requested fields.
    """
    records = [
        {
            "station_id": "89060",
            "station_name": "Meteo Station Juan Carlos I",
            "timestamp_utc": "2024-01-01T08:00:00Z",
            "temperature": 0.5,
            "pressure": 995.0,
            "wind_speed": 6.2,
        }
    ]

    result = aggregate_weather_data(
        records, aggregation="None", data_types=["temperature"]
    )

    assert len(result) == 1
    assert "Temperature (°C)" in result[0]
    assert "Pressure (hpa)" not in result[0]
    assert "Speed (m/s)" not in result[0]