import pytest
from datetime import datetime, timezone
from app.services.aggregator import aggregate_weather_data, calculate_feasibility_metrics


@pytest.fixture
def sample_raw_data():
    """Generates synthetic observations across winter and summer for DST and aggregation testing."""
    return [
        {
            "station_id": "89064",
            "station_name": "Meteo Station Gabriel de Castilla",
            "timestamp_utc": datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),  # CET (Winter -> UTC+1)
            "temperature": -2.5,
            "pressure": 995.0,
            "wind_speed": 12.0
        },
        {
            "station_id": "89064",
            "station_name": "Meteo Station Gabriel de Castilla",
            "timestamp_utc": datetime(2024, 1, 15, 12, 10, 0, tzinfo=timezone.utc),
            "temperature": -2.1,
            "pressure": 995.2,
            "wind_speed": 14.5
        },
        {
            "station_id": "89064",
            "station_name": "Meteo Station Gabriel de Castilla",
            "timestamp_utc": datetime(2024, 7, 15, 12, 0, 0, tzinfo=timezone.utc),  # CEST (Summer -> UTC+2)
            "temperature": -18.0,
            "pressure": 980.0,
            "wind_speed": 28.0  # Above cut-out (storm threshold)
        }
    ]


def test_dst_offset_winter_cet(sample_raw_data):
    """Verifies that January dates output explicit CET offset (+01:00)."""
    winter_record = [sample_raw_data[0]]
    result = aggregate_weather_data(winter_record, aggregation="None")
    assert len(result) == 1
    assert result[0]["Datetime"].endswith("+01:00")


def test_dst_offset_summer_cest(sample_raw_data):
    """Verifies that July dates output explicit CEST offset (+02:00)."""
    summer_record = [sample_raw_data[2]]
    result = aggregate_weather_data(summer_record, aggregation="None")
    assert len(result) == 1
    assert result[0]["Datetime"].endswith("+02:00")


def test_data_types_filtering(sample_raw_data):
    """Verifies that selecting only 'speed' excludes temperature and pressure."""
    result = aggregate_weather_data(sample_raw_data, aggregation="None", data_types=["speed"])
    assert "Speed (m/s)" in result[0]
    assert "Temperature (ºC)" not in result[0]
    assert "Pressure (hpa)" not in result[0]


def test_feasibility_metrics_calculation(sample_raw_data):
    """Verifies wind power potential, air density and icing risk calculations."""
    metrics = calculate_feasibility_metrics(sample_raw_data)
    assert metrics["total_records"] == 3
    assert metrics["mean_wind_speed_ms"] > 0
    assert metrics["air_density_kg_m3"] > 1.2
    assert metrics["icing_risk_detected"] is True  # Because min temp was -18.0°C