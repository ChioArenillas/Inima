// frontend/src/components/WindFeasibilityCards.tsx
import type { FeasibilityMetrics } from "../services/weatherApi";

interface Props {
  metrics: FeasibilityMetrics | null;
  loading: boolean;
}

export function WindFeasibilityCards({ metrics, loading }: Props) {
  if (loading) {
    return (
      <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: 8, border: "1px dashed #cbd5e1", marginBottom: "1.5rem", textAlign: "center", color: "#64748b" }}>
        Calculating aerodynamic feasibility & resource availability...
      </div>
    );
  }

  if (!metrics || metrics.total_records === 0) return null;

  return (
    <section style={{ marginBottom: "1.8rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.8rem" }}>
        <h2 style={{ fontSize: "1.1rem", margin: 0, color: "#0f172a", fontWeight: 700 }}>
          Wind Farm Feasibility & Aerodynamic Assessment
        </h2>
        {metrics.cache_source && (
          <span
            style={{
              fontSize: "0.75rem",
              fontWeight: 600,
              padding: "3px 8px",
              borderRadius: 6,
              background: metrics.cache_source.includes("Cache") ? "#ecfdf5" : "#eff6ff",
              color: metrics.cache_source.includes("Cache") ? "#047857" : "#1d4ed8",
              border: `1px solid ${metrics.cache_source.includes("Cache") ? "#a7f3d0" : "#bfdbfe"}`,
            }}
          >
            ⚡ Data Source: {metrics.cache_source}
          </span>
        )}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "1rem",
        }}
      >
        {/* Potencial de Generación */}
        <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "1rem", borderLeft: "4px solid #0284c7" }}>
          <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase" }}>
            Turbine Generation Window
          </span>
          <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#0f172a", margin: "0.3rem 0" }}>
            {metrics.generation_window_pct}%
          </div>
          <span style={{ fontSize: "0.75rem", color: "#475569" }}>
            Hours within cut-in (3.5 m/s) and cut-out (25 m/s) limits.
          </span>
        </div>

        {/* Densidad del aire */}
        <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "1rem", borderLeft: "4px solid #10b981" }}>
          <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase" }}>
            Estimated Air Density (ρ)
          </span>
          <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#0f172a", margin: "0.3rem 0" }}>
            {metrics.air_density_kg_m3} <span style={{ fontSize: "0.9rem", fontWeight: 500 }}>kg/m³</span>
          </div>
          <span style={{ fontSize: "0.75rem", color: "#475569" }}>
            vs. 1.225 standard. Denser polar air increases wind power output.
          </span>
        </div>

        {/* Riesgo de tempestad */}
        <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "1rem", borderLeft: "4px solid #f59e0b" }}>
          <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase" }}>
            Storm Cut-Out Risk
          </span>
          <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#0f172a", margin: "0.3rem 0" }}>
            {metrics.storm_shutdown_risk_pct}%
          </div>
          <span style={{ fontSize: "0.75rem", color: "#475569" }}>
            Peak gust: {metrics.max_wind_speed_ms} m/s (&gt;25 m/s forces shutdown).
          </span>
        </div>

        {/* Riesgo de Icing / Congelación */}
        <div
          style={{
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: 8,
            padding: "1rem",
            borderLeft: `4px solid ${metrics.icing_risk_detected ? "#ef4444" : "#10b981"}`,
          }}
        >
          <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, textTransform: "uppercase" }}>
            Blade Icing Risk
          </span>
          <div
            style={{
              fontSize: "1.2rem",
              fontWeight: 800,
              color: metrics.icing_risk_detected ? "#b91c1c" : "#047857",
              margin: "0.5rem 0",
            }}
          >
            {metrics.icing_risk_detected ? "⚠️ High Risk Detected" : "✓ Low Risk"}
          </div>
          <span style={{ fontSize: "0.75rem", color: "#475569" }}>
            Min temp: {metrics.min_temperature_c ?? "N/A"} ºC (Heated blades required).
          </span>
        </div>
      </div>
    </section>
  );
}