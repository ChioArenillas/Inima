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
    <div style={{ width: "100%", height: 380, marginTop: "1rem" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 30, left: 10, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="Datetime"
            tickFormatter={(val) => {
              if (!val) return "";
              const timePart = val.split("T")[1];
              return timePart ? timePart.substring(0, 5) : val;
            }}
            stroke="#666"
          />
          {/* Left axis: Temperature (°C) and Speed (m/s) */}
          <YAxis
            yAxisId="left"
            stroke="#e65100"
            domain={["auto", "auto"]}
            unit=""
          />
          {/* Right axis: Pressure (hPa) with auto-scaling to avoid flattening the rest */}
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#1565c0"
            domain={["auto", "auto"]}
            unit=" hPa"
          />
          <Tooltip />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="Temperature (ºC)"
            stroke="#e65100"
            dot={false}
            strokeWidth={2}
          />{" "}
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="Speed (m/s)"
            stroke="#2e7d32"
            dot={false}
            strokeWidth={2}
          />
          <Line
            yAxisId="right"
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
