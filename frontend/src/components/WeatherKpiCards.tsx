import React, { useMemo } from "react";
import type { WeatherRecord } from "../types/weather";

interface Props {
  data: WeatherRecord[];
}

export const WeatherKpiCards: React.FC<Props> = ({ data }) => {
  const stats = useMemo(() => {
    if (!data.length) return null;

    const speeds = data
      .map((d) => d["Speed (m/s)"])
      .filter((v): v is number => v !== undefined && v !== null);

    const temps = data
      .map((d) => d["Temperature (°C)"])
      .filter((v): v is number => v !== undefined && v !== null);

    const pressures = data
      .map((d) => d["Pressure (hpa)"])
      .filter((v): v is number => v !== undefined && v !== null);

    const avgSpeed = speeds.length
      ? (speeds.reduce((a, b) => a + b, 0) / speeds.length).toFixed(2)
      : "--";
    const maxSpeed = speeds.length ? Math.max(...speeds).toFixed(2) : "--";

    const avgTemp = temps.length
      ? (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(2)
      : "--";
    const minTemp = temps.length ? Math.min(...temps).toFixed(2) : "--";

    const avgPressure = pressures.length
      ? (pressures.reduce((a, b) => a + b, 0) / pressures.length).toFixed(1)
      : "--";

    return { avgSpeed, maxSpeed, avgTemp, minTemp, avgPressure };
  }, [data]);

  if (!stats) return null;

  const cardStyle: React.CSSProperties = {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "10px",
    padding: "1rem",
    boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
  };

  const labelStyle: React.CSSProperties = {
    fontSize: "0.8rem",
    color: "#64748b",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    fontWeight: 600,
    marginBottom: "0.3rem",
  };

  const valueStyle: React.CSSProperties = {
    fontSize: "1.5rem",
    fontWeight: 700,
    color: "#0f172a",
    margin: 0,
  };

  const subStyle: React.CSSProperties = {
    fontSize: "0.75rem",
    color: "#94a3b8",
    marginTop: "0.3rem",
  };

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "1rem",
        marginBottom: "1.8rem",
      }}
    >
      <div style={cardStyle}>
        <div style={labelStyle}>Avg Wind Speed</div>
        <p style={valueStyle}>{stats.avgSpeed} <span style={{ fontSize: "0.9rem" }}>m/s</span></p>
        <p style={subStyle}>Operating threshold: &gt; 3.0 m/s</p>
      </div>

      <div style={cardStyle}>
        <div style={labelStyle}>Peak Wind Gust</div>
        <p style={{ ...valueStyle, color: "#2e7d32" }}>{stats.maxSpeed} <span style={{ fontSize: "0.9rem" }}>m/s</span></p>
        <p style={subStyle}>Survival cut-out threshold: 25 m/s</p>
      </div>

      <div style={cardStyle}>
        <div style={labelStyle}>Avg Temperature</div>
        <p style={{ ...valueStyle, color: "#e65100" }}>{stats.avgTemp} <span style={{ fontSize: "0.9rem" }}>°C</span></p>
        <p style={subStyle}>Min recorded: {stats.minTemp} °C</p>
      </div>

      <div style={cardStyle}>
        <div style={labelStyle}>Mean Barometric Pressure</div>
        <p style={{ ...valueStyle, color: "#1565c0" }}>{stats.avgPressure} <span style={{ fontSize: "0.9rem" }}>hPa</span></p>
        <p style={subStyle}>Air density indicator</p>
      </div>
    </div>
  );
};