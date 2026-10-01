from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


def aggregate_weather_data(
    records: List[Dict[str, Any]],
    aggregation: Optional[str] = "None",
    data_types: Optional[List[str]] = None,
    location: Optional[str] = "Europe/Madrid"
) -> List[Dict[str, Any]]:
    """
    Processes time-series observations:
    1. Localizes timestamps according to the station/input location for accurate daily/monthly grouping.
    2. Performs time aggregation (None, Hourly, Daily, Monthly) using arithmetic means.
    3. Converts final output Datetime to Europe/Madrid (CET/CEST) with explicit ISO-8601 offsets.
    4. Filters metric keys according to user selection (0 to 3 types; default all).
    """
    if not records:
        return []

    df = pd.DataFrame(records)

    # 1. Parse timestamps stored in UTC
    df["timestamp"] = pd.to_datetime(df["timestamp_utc"])
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")

    # 2. Localize to target location for proper calendar day/month boundaries
    target_tz = location if location else "Europe/Madrid"
    try:
        df["timestamp_local"] = df["timestamp"].dt.tz_convert(target_tz)
    except Exception:
        df["timestamp_local"] = df["timestamp"].dt.tz_convert("Europe/Madrid")

    # 3. Handle raw resolution (no aggregation)
    if not aggregation or aggregation.lower() == "none":
        # Always output in Europe/Madrid as specified in requirements
        df["timestamp_final"] = df["timestamp"].dt.tz_convert("Europe/Madrid")
        return _format_output(df, data_types)

    frequency_mapping = {
        "hourly": "1h",
        "daily": "1D",
        "monthly": "1ME"
    }
    freq = frequency_mapping.get(aggregation.lower())
    if not freq:
        df["timestamp_final"] = df["timestamp"].dt.tz_convert("Europe/Madrid")
        return _format_output(df, data_types)

    numeric_columns = ["temperature", "pressure", "wind_speed"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Resample based on local time boundaries (ensuring midnight-to-midnight reflects station days)
    df = df.set_index("timestamp_local")
    aggregated_df = (
        df.groupby(["station_id", "station_name"])[numeric_columns]
        .resample(freq)
        .mean()
        .reset_index()
    )
    aggregated_df = aggregated_df.dropna(subset=numeric_columns, how="all")

    # Final presentation requirement: Output Datetime in Europe/Madrid (CET/CEST)
    aggregated_df["timestamp_final"] = (
        aggregated_df["timestamp_local"].dt.tz_convert("Europe/Madrid")
    )

    return _format_output(aggregated_df, data_types)


def calculate_feasibility_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Business Domain calculation for the Antarctica Wind Farm project:
    Evaluates wind resource availability, turbine cut-in/cut-out thresholds,
    and air density for GS Inima Business Development analysts.
    """
    if not records:
        return {
            "total_hours_analyzed": 0,
            "mean_wind_speed_ms": 0.0,
            "max_wind_gust_ms": 0.0,
            "turbine_generation_potential_pct": 0.0,
            "high_wind_shutdown_risk_pct": 0.0,
            "estimated_air_density_kg_m3": 0.0,
            "min_temperature_c": 0.0,
            "icing_risk_detected": False
        }

    df = pd.DataFrame(records)
    for col in ["temperature", "pressure", "wind_speed"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    speeds = df["wind_speed"].dropna()
    temps = df["temperature"].dropna()
    pressures = df["pressure"].dropna()

    total_pts = len(speeds)
    if total_pts == 0:
        return {}

    # Typical commercial wind turbine operational range
    cut_in = 3.5    # Minimum operational wind speed (m/s)
    cut_out = 25.0  # Storm safety shutdown (m/s)

    generation_hours = ((speeds >= cut_in) & (speeds <= cut_out)).sum()
    shutdown_hours = (speeds > cut_out).sum()

    mean_temp = temps.mean() if not temps.empty else -5.0
    mean_pres = pressures.mean() if not pressures.empty else 990.0

    # Ideal Gas Law for air density: rho = (P * 100) / (R_specific * T_kelvin)
    # R_specific for dry air = 287.05 J/(kg·K)
    t_kelvin = mean_temp + 273.15
    air_density = (mean_pres * 100.0) / (287.05 * t_kelvin) if t_kelvin > 0 else 1.225

    return {
        "total_records": total_pts,
        "mean_wind_speed_ms": round(float(speeds.mean()), 2),
        "max_wind_speed_ms": round(float(speeds.max()), 2),
        "generation_window_pct": round(float((generation_hours / total_pts) * 100), 1),
        "storm_shutdown_risk_pct": round(float((shutdown_hours / total_pts) * 100), 1),
        "air_density_kg_m3": round(float(air_density), 3),
        "min_temperature_c": round(float(temps.min()), 2) if not temps.empty else None,
        "icing_risk_detected": bool(temps.min() < -15.0) if not temps.empty else False,
    }


def _format_output(
    df: pd.DataFrame, data_types: Optional[List[str]]
) -> List[Dict[str, Any]]:
    """
    Formats the DataFrame columns to match the PDF specification.
    """
    active_types = (
        [t.lower() for t in data_types]
        if data_types
        else ["temperature", "pressure", "speed"]
    )

    results = []
    for _, row in df.iterrows():
        # Generates ISO format with timezone offset (e.g. +01:00 or +02:00)
        formatted_datetime = row["timestamp_final"].isoformat()

        item = {
            "Station": row.get("station_name"),
            "Datetime": formatted_datetime
        }
        if "temperature" in active_types:
            item["Temperature (ºC)"] = (
                round(row["temperature"], 2)
                if pd.notnull(row.get("temperature"))
                else None
            )
        if "pressure" in active_types:
            item["Pressure (hpa)"] = (
                round(row["pressure"], 2)
                if pd.notnull(row.get("pressure"))
                else None
            )
        if "speed" in active_types:
            item["Speed (m/s)"] = (
                round(row["wind_speed"], 2)
                if pd.notnull(row.get("wind_speed"))
                else None
            )

        results.append(item)

    return results