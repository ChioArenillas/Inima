import React from "react";
import type { WeatherRecord } from "../types/weather";

interface Props {
  data: WeatherRecord[];
}

export const WeatherTable: React.FC<Props> = ({ data }) => {
  if (!data || data.length === 0) {
    return <p style={{ color: "#666" }}>No data to display. Please submit a query.</p>;
  }

  return (
    <div style={{ maxHeight: 350, overflowY: "auto", marginTop: "1rem", border: "1px solid #e0e0e0", borderRadius: 4 }}>
      <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.9rem" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #ddd", background: "#fafafa" }}>
            <th style={{ padding: "10px" }}>Station</th>
            <th style={{ padding: "10px" }}>Datetime</th>
            <th style={{ padding: "10px" }}>Temp (°C)</th>
            <th style={{ padding: "10px" }}>Pressure (hpa)</th>
            <th style={{ padding: "10px" }}>Speed (m/s)</th>
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 100).map((row, idx) => (
            <tr key={idx} style={{ borderBottom: "1px solid #eee" }}>
              <td style={{ padding: "8px 10px" }}>{row.Station}</td>
              <td style={{ padding: "8px 10px" }}>{row.Datetime}</td>
              <td style={{ padding: "8px 10px" }}>{row["Temperature (°C)"] ?? "-"}</td>
              <td style={{ padding: "8px 10px" }}>{row["Pressure (hpa)"] ?? "-"}</td>
              <td style={{ padding: "8px 10px" }}>{row["Speed (m/s)"] ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > 100 && (
        <p style={{ fontSize: "0.8rem", color: "#888", textAlign: "center", margin: "8px 0" }}>
          Showing first 100 rows of {data.length} records.
        </p>
      )}
    </div>
  );
};