import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import type { WeatherRecord } from "../types/weather";

interface Props {
  data: WeatherRecord[];
}

export const WeatherChart: React.FC<Props> = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div style={{ width: "100%", height: 350, marginTop: "1rem" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="Datetime"
            tickFormatter={(val) => val.split("T")[1]?.substring(0, 5) || val.split("T")[0]}
            stroke="#666"
          />
          <YAxis stroke="#666" />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="Temperature (°C)"
            stroke="#e65100"
            dot={false}
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="Speed (m/s)"
            stroke="#2e7d32"
            dot={false}
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="Pressure (hpa)"
            stroke="#1565c0"
            dot={false}
            strokeWidth={1.5}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};