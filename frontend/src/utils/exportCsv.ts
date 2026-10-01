import type { WeatherRecord } from "../types/weather";

export function exportWeatherToCsv(data: WeatherRecord[], filename = "antarctica_observations.csv") {
  if (!data.length) return;

  const headers = ["Station", "Datetime", "Temperature (°C)", "Pressure (hpa)", "Speed (m/s)"];
  
  const csvRows = data.map((row) => [
    `"${row.Station || ""}"`,
    `"${row.Datetime || ""}"`,
    row["Temperature (ºC)"] ?? "",
    row["Pressure (hpa)"] ?? "",
    row["Speed (m/s)"] ?? ""
  ]);

  const csvContent = [headers.join(","), ...csvRows.map((r) => r.join(","))].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}