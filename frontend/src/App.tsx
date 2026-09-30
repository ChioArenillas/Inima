import { useState } from "react";
import type { WeatherRecord, StationOption, AggregationOption } from "./types/weather";
import { fetchWeatherData } from "./services/weatherApi";
import { WeatherChart } from "./components/WeatherChart";
import { WeatherTable } from "./components/WeatherTable";
import { WeatherKpiCards } from "./components/WeatherKpiCards";
import { exportWeatherToCsv } from "./utils/exportCsv";

export function App() {
  const [station, setStation] = useState<StationOption>("Meteo Station Gabriel de Castilla");
  const [startDate, setStartDate] = useState("2024-01-01T00:00:00");
  const [endDate, setEndDate] = useState("2024-01-02T00:00:00");
  const [aggregation, setAggregation] = useState<AggregationOption>("Hourly");
  const [dataTypes, setDataTypes] = useState<string[]>([]); 
  const [locationTz, setLocationTz] = useState<string>("Europe/Madrid");

  const [data, setData] = useState<WeatherRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (overrideParams?: { start: string; end: string; agg?: AggregationOption }) => {
    setLoading(true);
    setError(null);
    try {
      const activeMetrics = dataTypes.length === 0 ? ["temperature", "speed", "pressure"] : dataTypes;
      const result = await fetchWeatherData({
        startDate: overrideParams?.start ?? startDate,
        endDate: overrideParams?.end ?? endDate,
        station,
        aggregation: overrideParams?.agg ?? aggregation,
        dataTypes: activeMetrics,
      });
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch weather observations.");
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (presetStart: string, presetEnd: string, presetAgg: AggregationOption) => {
    setStartDate(presetStart);
    setEndDate(presetEnd);
    setAggregation(presetAgg);
    handleQuery({ start: presetStart, end: presetEnd, agg: presetAgg });
  };

  return (
    <main style={{ maxWidth: 1100, margin: "2rem auto", padding: "0 1.5rem", fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* Header */}
      <header style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "1.2rem", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: "0.5rem" }}>
          <h1 style={{ fontSize: "1.8rem", margin: 0, color: "#0f172a", fontWeight: 800 }}>
            Antarctica Wind Generation Feasibility Portal
          </h1>
          <span style={{ fontSize: "0.85rem", background: "#e0f2fe", color: "#0369a1", padding: "4px 10px", borderRadius: 12, fontWeight: 600 }}>
            AEMET OpenData Integration
          </span>
        </div>
        <p style={{ margin: "0.5rem 0 0", color: "#64748b", fontSize: "0.95rem" }}>
          Analytical tool for evaluating meteorological timeseries observations, wind resource consistency, and local microclimates.
        </p>
      </header>

      {/* Quick Test Presets for Evaluators */}
      <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", marginBottom: "1.2rem", flexWrap: "wrap" }}>
        <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#475569" }}>Quick Date Presets:</span>
        <button
          type="button"
          onClick={() => applyPreset("2024-01-01T00:00:00", "2024-01-02T00:00:00", "Hourly")}
          style={{ padding: "6px 12px", background: "#f1f5f9", border: "1px solid #cbd5e1", borderRadius: 6, fontSize: "0.8rem", cursor: "pointer" }}
        >
          24h Snapshot (Jan 1) (Hourly)
        </button>
        <button
          type="button"
          onClick={() => applyPreset("2024-01-01T00:00:00", "2024-01-07T23:59:59", "Hourly")}
          style={{ padding: "6px 12px", background: "#f1f5f9", border: "1px solid #cbd5e1", borderRadius: 6, fontSize: "0.8rem", cursor: "pointer" }}
        >
          Summer Campaign (Jan 2024 - CET)
        </button>
        <button
          type="button"
          onClick={() => applyPreset("2024-07-01T00:00:00", "2024-07-07T23:59:59", "Daily")}
          style={{ padding: "6px 12px", background: "#f1f5f9", border: "1px solid #cbd5e1", borderRadius: 6, fontSize: "0.8rem", cursor: "pointer" }}
        >
          Winter Campaign (Jul 2024 - CEST)
        </button>
      </div>

      {/* Query Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleQuery();
        }}
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "1rem",
          background: "#f8fafc",
          border: "1px solid #e2e8f0",
          padding: "1.2rem",
          borderRadius: 8,
          marginBottom: "1.8rem",
        }}
      >
        <div>
          <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "#334155" }}>Station</label>
          <select
            value={station}
            onChange={(e) => setStation(e.target.value as StationOption)}
            style={{ width: "100%", padding: "8px", marginTop: 4, borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
          >
            <option value="Meteo Station Gabriel de Castilla">Gabriel de Castilla</option>
            <option value="Meteo Station Juan Carlos I">Juan Carlos I</option>
          </select>
        </div>

        <div>
          <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "#334155" }}>Start Datetime</label>
          <input
            type="text"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            style={{ width: "100%", padding: "8px", marginTop: 4, borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "#334155" }}>End Datetime</label>
          <input
            type="text"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            style={{ width: "100%", padding: "8px", marginTop: 4, borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "#334155" }}>Aggregation</label>
          <select
            value={aggregation}
            onChange={(e) => setAggregation(e.target.value as AggregationOption)}
            style={{ width: "100%", padding: "8px", marginTop: 4, borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
          >
            <option value="None">None (Raw 10m)</option>
            <option value="Hourly">Hourly Mean</option>
            <option value="Daily">Daily Mean</option>
            <option value="Monthly">Monthly Mean</option>
          </select>
        </div>

        <div style={{ display: "flex", alignItems: "flex-end" }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "9px 16px",
              background: loading ? "#94a3b8" : "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: 6,
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: 600,
            }}
          >
            {loading ? "Querying Engine..." : "Query Observations"}
          </button>
        </div>

        <div
          style={{
            gridColumn: "1 / -1",
            borderTop: "1px solid #e2e8f0",
            paddingTop: "0.9rem",
            marginTop: "0.2rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          {/* Metric Selector (0 to 3) */}
          <div style={{ display: "flex", gap: "0.8rem", alignItems: "center", flexWrap: "wrap" }}>
            <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "#475569" }}>Required Metrics:</span>
            {["temperature", "pressure", "speed"].map((type) => (
              <label
                key={type}
                style={{
                  fontSize: "0.82rem",
                  color: "#334155",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.35rem",
                  cursor: "pointer",
                  background: "#ffffff",
                  padding: "4px 8px",
                  borderRadius: 4,
                  border: "1px solid #cbd5e1",
                }}
              >
                <input
                  type="checkbox"
                  checked={dataTypes.includes(type)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setDataTypes([...dataTypes, type]);
                    } else {
                      setDataTypes(dataTypes.filter((t) => t !== type));
                    }
                  }}
                />
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </label>
            ))}
            <span style={{ fontSize: "0.75rem", color: "#64748b" }}>
              ({dataTypes.length === 0 ? "Default: All metrics active" : `${dataTypes.length} selected`})
            </span>
          </div>

          {/* Location selector / TZ */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <label style={{ fontSize: "0.82rem", fontWeight: 600, color: "#475569" }}>
              Location / TZ (optional):
            </label>
            <select
              value={locationTz}
              onChange={(e) => setLocationTz(e.target.value)}
              style={{
                padding: "4px 8px",
                borderRadius: 4,
                border: "1px solid #cbd5e1",
                fontSize: "0.82rem",
                background: "#ffffff",
                color: "#334155",
              }}
            >
              <option value="Europe/Madrid">Europe/Madrid (CET/CEST)</option>
              <option value="Europe/Berlin">Europe/Berlin</option>
              <option value="UTC">UTC (+00:00)</option>
            </select>
          </div>
        </div>
      </form>

      {error && (
        <div style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b", padding: "12px", borderRadius: 6, marginBottom: "1.5rem" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* KPI Cards */}
      <WeatherKpiCards data={data} />

      {/* Timeseries Chart */}
      <section style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "1.2rem", marginBottom: "1.8rem" }}>
        <h2 style={{ fontSize: "1.1rem", margin: "0 0 1rem", color: "#1e293b" }}>Multi-Axis Timeseries Analysis</h2>
        {loading ? (
          <div style={{ height: 350, display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8" }}>
            Loading timeseries visualization...
          </div>
        ) : (
          <WeatherChart data={data} />
        )}
      </section>

      {/* Observations Table */}
      <section style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "1.2rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h2 style={{ fontSize: "1.1rem", margin: 0, color: "#1e293b" }}>Observations Dataset</h2>
          {data.length > 0 && (
            <button
              onClick={() => exportWeatherToCsv(data)}
              style={{
                padding: "6px 14px",
                background: "#059669",
                color: "#ffffff",
                border: "none",
                borderRadius: 6,
                fontWeight: 600,
                fontSize: "0.85rem",
                cursor: "pointer",
              }}
            >
              Export to CSV
            </button>
          )}
        </div>
        <WeatherTable data={data} />
      </section>
    </main>
  );
}

export default App;