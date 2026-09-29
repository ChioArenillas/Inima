import pandas as pd
from typing import List, Dict, Any, Optional


def aggregate_weather_data(
    records: List[Dict[str, Any]],
    aggregation: Optional[str] = "None",
    data_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Processes time-series observations:
    1. Normalizes timestamps to Europe/Madrid timezone, preserving DST offsets.
    2. Performs time aggregation (None, Hourly, Daily, Monthly) using arithmetic means.
    3. Filters metrics and outputs formatted JSON compliant with the specification.
    """
    if not records:
        return []

    df = pd.DataFrame(records)

    # Standardize to UTC then convert to Europe/Madrid (CET/CEST)
    df["timestamp"] = pd.to_datetime(df["timestamp_utc"])
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")

    df["timestamp"] = df["timestamp"].dt.tz_convert("Europe/Madrid")

    # If no aggregation requested, retain original 10-minute resolution
    if not aggregation or aggregation.lower() == "none":
        return _format_output(df, data_types)

    frequency_mapping = {
        "hourly": "1h",
        "daily": "1D",
        "monthly": "1ME"
    }
    freq = frequency_mapping.get(aggregation.lower())
    if not freq:
        return _format_output(df, data_types)

    # Prepare numeric values for aggregation
    numeric_columns = ["temperature", "pressure", "wind_speed"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Resample by time window and compute mean values
    df = df.set_index("timestamp")
    aggregated_df = (
        df.groupby(["station_id", "station_name"])[numeric_columns]
        .resample(freq)
        .mean()
        .reset_index()
    )
    aggregated_df = aggregated_df.dropna(subset=numeric_columns, how="all")

    return _format_output(aggregated_df, data_types)


def _format_output(
    df: pd.DataFrame, data_types: Optional[List[str]]
) -> List[Dict[str, Any]]:
    """
    Maps internal dataframe columns to required API response keys with explicit ISO-8601 offsets.
    """
    # If no data_types are passed or list is empty, default to all three metrics
    active_types = (
        [t.lower() for t in data_types]
        if data_types
        else ["temperature", "pressure", "speed"]
    )

    results = []
    for _, row in df.iterrows():
        # Generates ISO format including timezone offset (e.g., +01:00 or +02:00)
        formatted_datetime = row["timestamp"].isoformat()

        item = {
            "Station": row.get("station_name"),
            "Datetime": formatted_datetime
        }
        if "temperature" in active_types:
            item["Temperature (°C)"] = (
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