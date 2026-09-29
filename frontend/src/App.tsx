import { useState } from "react";
import type { WeatherRecord, StationOption, AggregationOption } from "./types/weather";
import { fetchWeatherData } from "./services/weatherApi";
import { WeatherChart } from "./components/WeatherChart";
import { WeatherTable } from "./components/WeatherTable";

export function App() {
  const [station, setStation] = useState<StationOption>("Meteo Station Gabriel de Castilla");
  const [startDate, setStartDate] = useState("2024-01-01T00:00:00");
  const [endDate, setEndDate] = useState("2024-01-02T00:00:00");
  const [aggregation, setAggregation] = useState<AggregationOption>("Hourly");

  const [data, setData] = useState<WeatherRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await fetchWeatherData({
        startDate,
        endDate,
        station,
        aggregation,
        dataTypes: ["temperature", "speed", "pressure"],
      });
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch weather observations.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 1000, margin: "2rem auto", padding: "0 1.5rem", fontFamily: "sans-serif" }}>
      <header style={{ borderBottom: "1px solid #e0e0e0", paddingBottom: "1rem", marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.6rem", margin: 0, color: "#111" }}>
          GS Inima - Antarctica Wind Study Portal
        </h1>
        <p style={{ margin: "0.4rem 0 0", color: "#666" }}>
          Exploratory analysis platform for wind generation feasibility.
        </p>
      </header>

      {/* Form */}
      <form
        onSubmit={handleQuery}
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          background: "#f7f9fa",
          padding: "1.2rem",
          borderRadius: 8,
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600 }}>Station</label>
          <select
            value={station}
            onChange={(e) => setStation(e.target.value as StationOption)}
            style={{ width: "100%", padding: "8px", marginTop: 4, borderRadius: 4, border: "1px solid #ccc" }}
          >
            <option value="Meteo Station Gabriel de Castilla">Gabriel de Castilla</option>
            <option value="Meteo Station Juan Carlos I">Juan Carlos I</option>
          </select>
        </div>

        <div>
          <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600 }}>Start Date</label>
          <input
            type="text"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            style={{ width: "100%", padding: "8px", marginTop: 4, borderRadius: 4, border: "1px solid #ccc" }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600 }}>End Date</label>
          <input
            type="text"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            style={{ width: "100%", padding: "8px", marginTop: 4, borderRadius: 4, border: "1px solid #ccc" }}
          />
        </div>

        <div>
          <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600 }}>Aggregation</label>
          <select
            value={aggregation}
            onChange={(e) => setAggregation(e.target.value as AggregationOption)}
            style={{ width: "100%", padding: "8px", marginTop: 4, borderRadius: 4, border: "1px solid #ccc" }}
          >
            <option value="None">None (10 min)</option>
            <option value="Hourly">Hourly</option>
            <option value="Daily">Daily</option>
            <option value="Monthly">Monthly</option>
          </select>
        </div>

        <div style={{ display: "flex", alignItems: "flex-end" }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "10px",
              background: "#0d47a1",
              color: "#fff",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            {loading ? "Querying..." : "Fetch Observations"}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ background: "#ffebee", color: "#c62828", padding: "10px", borderRadius: 4, marginBottom: "1rem" }}>
          {error}
        </div>
      )}

      {/* Gráfico */}
      <section style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.2rem", color: "#222" }}>Timeseries Chart</h2>
        <WeatherChart data={data} />
      </section>

      {/* Tabla */}
      <section>
        <h2 style={{ fontSize: "1.2rem", color: "#222" }}>Observations Table</h2>
        <WeatherTable data={data} />
      </section>
    </main>
  );
}

export default App;