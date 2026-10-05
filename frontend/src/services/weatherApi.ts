import type { WeatherRecord, StationOption, AggregationOption } from "../types/weather";

const BASE_URL = import.meta.env.VITE_API_URL || "https://aemet-wind-farm-api.onrender.com";

const STATION_CODE_MAP: Record<StationOption, string> = {
  "Meteo Station Gabriel de Castilla": "89064",
  "Meteo Station Juan Carlos I": "89070",
};

export interface FeasibilityMetrics {
  total_records: number;
  mean_wind_speed_ms: number;
  max_wind_speed_ms: number;
  generation_window_pct: number;
  storm_shutdown_risk_pct: number;
  air_density_kg_m3: number;
  min_temperature_c: number | null;
  icing_risk_detected: boolean;
  cache_source?: string;
}

export async function fetchWeatherData(params: {
  startDate: string;
  endDate: string;
  station: StationOption;
  aggregation: AggregationOption;
  dataTypes: string[];
  location?: string;
}): Promise<WeatherRecord[]> {
  const stationCode = STATION_CODE_MAP[params.station] || params.station;
  const queryParams = new URLSearchParams();

  if (params.aggregation) queryParams.append("aggregation", params.aggregation);
  if (params.location) queryParams.append("location", params.location);
  params.dataTypes.forEach((dt) => queryParams.append("data_types", dt));

  // Endpoint
  const endpoint = `${BASE_URL}/api/antartida/datos/fechaini/${encodeURIComponent(
    params.startDate
  )}/fechafin/${encodeURIComponent(params.endDate)}/estacion/${stationCode}?${queryParams.toString()}`;

  const res = await fetch(endpoint);
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}

export async function fetchFeasibilityMetrics(params: {
  startDate: string;
  endDate: string;
  station: StationOption;
}): Promise<FeasibilityMetrics> {
  const stationCode = STATION_CODE_MAP[params.station] || params.station;
  const endpoint = `${BASE_URL}/api/antartida/feasibility-assessment?fechainiStr=${encodeURIComponent(
    params.startDate
  )}&fechaFinStr=${encodeURIComponent(params.endDate)}&identificacion=${stationCode}`;

  const res = await fetch(endpoint);
  if (!res.ok) {
    throw new Error("Could not retrieve feasibility indicators.");
  }

  return res.json();
}