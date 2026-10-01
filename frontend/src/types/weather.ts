export interface WeatherRecord {
  Station: string;
  Datetime: string;
  "Temperature (ºC)"?: number;
  "Pressure (hpa)"?: number;
  "Speed (m/s)"?: number;
}

export type StationOption =
  | "Meteo Station Gabriel de Castilla"
  | "Meteo Station Juan Carlos I";

export type AggregationOption = "None" | "Hourly" | "Daily" | "Monthly";