# Antarctica Wind Farm Feasibility & Trading Infrastructure Portal

An end-to-end meteorological data service and exploratory dashboard engineered to evaluate the commercial feasibility of wind energy generation in Antarctica (stations Gabriel de Castilla and Juan Carlos I) using historical observations from the AEMET OpenData API.

This platform bridges two distinct operational stakeholders: **Business Development** (assessing polar aerodynamic turbine viability) and the **Intraday Trading Desk** (protecting upstream rate limits via cache-aside persistence and auditing data freshness).

---

## 1. Business Problem & Domain Context

### Strategic Challenge 1: Wind Farm Feasibility (Business Development)
Evaluating wind energy generation in polar environments requires assessing specific aerodynamic and environmental constraints beyond simple average wind speed:
* **Aerodynamic Power Potential ($P \propto \rho \cdot v^3$):** Available kinetic wind power is proportional to local air density ($\rho$). Polar sub-zero temperatures yield denser air compared to standard ISO conditions ($1.225 \text{ kg/m}^3$), generating higher power output for equivalent swept blade areas.
* **Operational Generation Window:** Commercial polar wind turbines operate within defined aerodynamic cut-in (~$3.5 \text{ m/s}$) and cut-out (~$25.0 \text{ m/s}$) thresholds. Speeds above $25 \text{ m/s}$ trigger automated braking to prevent structural failure during Antarctic blizzards.
* **Blade Icing Risk:** Sub-zero temperatures and polar maritime humidity induce blade icing, requiring de-icing systems to avoid aerodynamic stall and mechanical imbalance.

The application includes an automated **Feasibility Assessment Engine** computing generation window availability (%), storm cut-out shutdown risks, and air density estimations derived from ideal gas calculations ($\rho = \frac{P \cdot 100}{R_{\text{specific}} \cdot T}$).

### Strategic Challenge 2: Intraday Trading Desk Quota & Low-Latency Reads
Traders operating in continuous intraday power markets require frequent meteorological updates to balance short-term commitments. However, upstream AEMET OpenData enforces strict rate limits and updates observation sets periodically. Unregulated requests from algorithmic trading desks risk HTTP 429 quota bans.
* **Cache-Aside Persistence:** All requests query local SQLite storage first before hitting upstream AEMET endpoints, serving subsequent intraday reads in low single-digit milliseconds.
* **Data Provenance Auditing:** The UI surfaces whether the payload originated from `SQLite Local Cache` or `AEMET Live Sync` to guarantee transparency over data freshness.

---

## Architecture Overview

```
                      ┌──────────────────────────────────────────────┐
                      │            Frontend (React + TS)             │
                      │  - Wind Feasibility & Turbine KPI Cards      │
                      │  - Data Source Provenance Indicator (Cache)  │
                      │  - Granular Metric Filter (Temp/Press/Speed) │
                      │  - Dynamic Timezone/Location Selector        │
                      │  - One-Click Presets (24h Snapshot / Weeks)  │
                      │  - Dual-Axis Timeseries (Recharts)           │
                      │  - Client-side CSV Export                    │
                      └──────────────────────┬───────────────────────┘
                                             │ HTTP / JSON
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │             Backend (FastAPI)                │
                      │  - Strict Path & Query Validation (Pydantic) │
                      │  - Aerodynamic Feasibility Calculation Engine│
                      │  - Pandas Resampling Engine                  │
                      │  - Timezone Conversion (Europe/Madrid + DST) │
                      └──────────────────────┬───────────────────────┘
                                             │
                           ┌─────────────────┴─────────────────┐
              Cache Hit    ▼                                   ▼ Cache Miss
            ┌───────────────────────────────┐   ┌───────────────────────────────┐
            │     SQLite Local Database     │   │      AEMET OpenData API       │
            │  - Compound PK (station, ts)  │   │  - Two-step HTTP download     │
            │  - Low-latency Trader Reads   │   │  - Upstream rate-limit relief │
            └───────────────────────────────┘   └───────────────────────────────┘
```

---

## Key Engineering Decisions & Justifications

### 1. High-Frequency Trader Inquiries & Cache-Aside Architecture
* **Problem**: Upstream AEMET OpenData enforces strict rate limits and updates observation sets periodically rather than continuously. Unrestricted concurrent requests from internal algorithmic traders would trigger IP blocks and excessive latency.
* **Solution**: Implemented a cache-aside persistence model backed by SQLite (`weather_observations` table) with a unique compound constraint over `(station_id, timestamp_utc)`.
* **Outcome**: The primary request populates local storage; all subsequent intraday queries from traders are served directly from SQLite in single-digit milliseconds without making external HTTP calls.

### 2. Timezone Integrity & Daylight Saving Time (DST)
* **Problem**: The specification mandates returning observations formatted with ISO-8601 timestamps adjusted for Spanish time (`Europe/Madrid`), reflecting winter time (CET: UTC+1) and summer time (CEST: UTC+2). Storing localized timestamps directly causes ambiguity issues during the autumn DST transition (when the 02:00–03:00 window repeats).
* **Solution**: All records are stored normalized in pure UTC. When requests are served, the analytical layer applies `tz_convert("Europe/Madrid")` and formats outputs with explicit ISO offsets (e.g., `+01:00` or `+02:00`), ensuring mathematical consistency across daylight transitions.

### 3. Frontend Architecture & Domain Usability
* **Wind Feasibility Cards**: Displays turbine generation window percentage (3.5–25 m/s), air density, storm shutdown probability, and blade icing exposure directly in the client.
* **Dual-Axis Dynamic Visualization**: Atmospheric pressure ranges from ~980 to ~1005 hPa, while wind speed and temperature typically range between -15 and +15. Plotting them on a single Cartesian axis flattens wind and temperature curves. A dual-axis layout (`left: Speed/Temp`, `right: Pressure`) with automatic domain scaling ensures both profiles remain clearly readable.
* **Selective Metric Filtering**: Allows analysts to toggle specific parameters (`Temperature`, `Pressure`, `Speed`) dynamically. Defaults to all active metrics when unselected, reducing visual noise and optimizing network payload.
* **Configurable Location / Timezone Selector**: Provides explicit timezone targeting (`Europe/Madrid`, `Europe/Berlin`, `UTC`) directly within the query interface, aligning visual analytics with operational regional desks.
* **Evaluator Quick Presets**: Integrated one-click scenario triggers for rapid assessment:
  * **24h Snapshot (Jan 1)**: Inspects standard hourly granularity over a single diurnal cycle.
  * **Summer Campaign (Jan 2024 - CET)**: Loads a full summer-week profile under Central European Time (UTC+1).
  * **Winter Campaign (Jul 2024 - CEST)**: Evaluates high-severity winter wind regimes aggregated daily under Central European Summer Time (UTC+2).

---

## Project Structure

```
aemet-wind-farm/
├── app/
│   ├── services/
│   │   ├── aemet_client.py     # Two-step AEMET API client & station mappings
│   │   └── aggregator.py       # Resampling, timezone logic & feasibility formulas
│   ├── crud.py                 # SQLite cache-aside operations & deduplication
│   ├── database.py             # SQLAlchemy engine and session lifecycle
│   ├── main.py                 # FastAPI application endpoints and CORS setup
│   └── models.py               # SQLite declarative ORM models
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WeatherChart.tsx        # Recharts dual-axis visualization
│   │   │   ├── WeatherKpiCards.tsx     # Summary KPI cards
│   │   │   ├── WeatherTable.tsx        # Formatted observations tabular view
│   │   │   └── WindFeasibilityCards.tsx# Domain aerodynamic assessment cards
│   │   ├── services/
│   │   │   └── weatherApi.ts           # Typed API communication layer
│   │   ├── types/
│   │   │   └── weather.ts              # Shared TypeScript interfaces
│   │   ├── utils/
│   │   │   └── exportCsv.ts            # Client-side CSV generator
│   │   ├── App.tsx                     # Main exploratory dashboard layout
│   │   └── main.tsx                    # React entry point
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   └── test_api.py             # Pytest unit tests (DST offsets, filtering & feasibility)
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Getting Started

### Prerequisites
* Python 3.10+
* Node.js 18+ and npm
* An active [AEMET OpenData API Key](https://opendata.aemet.es/centrodedescargas/altaUsuario)

### Backend Setup

1. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   ```bash
   # Windows (PowerShell):
   $env:AEMET_API_KEY="your_aemet_api_key_here"

   # Linux / macOS:
   export AEMET_API_KEY="your_aemet_api_key_here"
   ```

4. **Run the Backend Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   * **OpenAPI Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
   * **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

5. **Run Unit Tests**:
   ```bash
   pytest
   ```

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   Open your browser at [http://localhost:5173](http://localhost:5173) to access the interactive dashboard.

---

## API Specification

### 1. `GET /api/antartida/datos/fechaini/{fechalniStr}/fechafin/{fechaFinStr}/estacion/{identificacion}`
Retrieves and aggregates meteorological timeseries data for the specified station and range.

#### Parameters:
* `fechalniStr` (path, string): Inclusive start timestamp (`YYYY-MM-DDTHH:MM:SS`).
* `fechaFinStr` (path, string): Inclusive end timestamp (`YYYY-MM-DDTHH:MM:SS`).
* `identificacion` (path, string): Station identifier or display name (`Meteo Station Gabriel de Castilla` / `89064` or `Meteo Station Juan Carlos I` / `89070`).
* `aggregation` (query, optional): Aggregation method (`None`, `Hourly`, `Daily`, `Monthly`). Defaults to `None`.
* `data_types` (query, optional): Metrics to filter (`temperature`, `speed`, `pressure`).
* `location` (query, optional): Reference timezone for calendar boundaries (default: `Europe/Madrid`).

#### Sample Response:
```json
[
  {
    "Station": "Meteo Station Gabriel de Castilla",
    "Datetime": "2024-01-01T01:00:00+01:00",
    "Temperature (ºC)": 2.35,
    "Pressure (hpa)": 991.0,
    "Speed (m/s)": 12.27
  },
  {
    "Station": "Meteo Station Gabriel de Castilla",
    "Datetime": "2024-01-01T02:00:00+01:00",
    "Temperature (ºC)": 2.03,
    "Pressure (hpa)": 991.45,
    "Speed (m/s)": 14.25
  }
]
```

### 2. `GET /api/antartida/feasibility-assessment`
Computes aerodynamic metrics for polar wind turbine site assessment (cut-in/cut-out ratios, air density, icing probability, and cache source provenance).

---

## Automated Verification & Testing

Automated verification tests are implemented in `tests/test_api.py` using `pytest`:
* **Time Resampling:** Validates arithmetic mean calculations when grouping raw 10-minute records into hourly, daily, and monthly intervals.
* **DST Offsets:** Verifies correct handling of CET (`+01:00`) during winter observations and CEST (`+02:00`) during summer periods.
* **Selective Metrics:** Verifies payload reduction when specific metric parameters (`data_types`) are provided.
* **Feasibility Logic:** Validates aerodynamic window, air density calculations, and icing alerts.

---

## Live Demo & Full-Stack Deployment

* **Live Interactive Platform:** [https://inima-dusky.vercel.app/](https://inima-dusky.vercel.app/)

The application is deployed full-stack (React client on Vercel communicating with an operational backend on Render). You can test the platform directly in your browser:
* Dynamic query execution across both Antarctic stations.
* Real-time calculation of wind generation availability, air density, and icing risk.
* Cache provenance tracking (`SQLite Local Cache` vs. `AEMET Live Sync`).
* Multi-axis timeseries visualization and client-side CSV export.

*(For local execution and inspection of the SQLite persistence layer or automated pytest suites, refer to the Getting Started section above).*