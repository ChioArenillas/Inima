import type { WeatherRecord, StationOption, AggregationOption } from "../types/weather";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

interface FetchParams {
  startDate: string;
  endDate: string;
  station: StationOption;
  aggregation: AggregationOption;
  dataTypes: string[];
}

export async function fetchWeatherData(params: FetchParams): Promise<WeatherRecord[]> {
  const queryParams = new URLSearchParams();
  if (params.aggregation && params.aggregation !== "None") {
    queryParams.append("aggregation", params.aggregation);
  }
  params.dataTypes.forEach((dt) => queryParams.append("data_types", dt));

  const endpoint = `${API_BASE_URL}/api/antartida/datos/fechaini/${params.startDate}/fechafin/${params.endDate}/estacion/${encodeURIComponent(
    params.station
  )}?${queryParams.toString()}`;

  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  return response.json();
}