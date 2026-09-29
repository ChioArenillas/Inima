# Antarctica Wind Farm Feasibility Service

An end-to-end meteorological data service and exploratory dashboard built to assess the feasibility of wind energy generation in Antarctica (stations Juan Carlos I and Gabriel de Castilla) using historical observations from the AEMET OpenData API.

This solution implements an asynchronous Python backend (FastAPI) paired with local SQLite caching for rate-limit protection, alongside an interactive client-side dashboard (React, TypeScript, Vite, Recharts).

## Architecture Overview

```
                     ┌──────────────────────────────────────────────┐
                     │           Frontend (React + TS)              │
                     │  - Quick Presets (Summer/Winter/DST)         │
                     │  - KPI Summary Cards (Avg & Peak Gusts)      │
                     │  - Dual-Axis Timeseries (Recharts)           │
                     │  - Client-side CSV Export                    │
                     └──────────────────────┬───────────────────────┘
                                            │ HTTP / JSON
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │            Backend (FastAPI)                 │
                     │  - Strict Path & Query Validation (Pydantic) │
                     │  - Pandas Resampling Engine                  │
                     │  - Timezone Conversion (Europe/Madrid + DST) │
                     └──────────────────────┬───────────────────────┘
                                            │
                          ┌─────────────────┴─────────────────┐
             Cache Hit    ▼                                   ▼ Cache Miss
            ┌───────────────────────────────┐       ┌───────────────────────────────┐
            │     SQLite Local Database     │       │       AEMET OpenData API      │
            │  - Compound PK (station, ts)  │       │  - Two-step async HTTP (httpx)│
            │  - Low-latency Trader Reads   │       │  - Upstream rate-limit relief │
            └───────────────────────────────┘       └───────────────────────────────┘

```

## Key Engineering Decisions & Justifications

### 1. High-Frequency Trader Inquiries & Cache-Aside Architecture

* **Problem**: Upstream AEMET OpenData enforces strict rate limits and updates observation sets periodically rather than continuously. Unrestricted concurrent requests from internal algorithmic traders would trigger IP blocks and excessive latency.

* **Solution**: Implemented a cache-aside persistence model backed by SQLite (`weather_observations` table) with a unique compound primary key `(station_id, timestamp_utc)`.

* **Outcome**: The primary request populates local storage; all subsequent intraday queries from traders are served directly from SQLite in single-digit milliseconds without making external HTTP calls.

### 2. Timezone Integrity & Daylight Saving Time (DST)

* **Problem**: The specification mandates returning observations formatted with ISO-8601 timestamps adjusted for Spanish time (`Europe/Madrid`), reflecting winter time (CET: UTC+1) and summer time (CEST: UTC+2). Storing localized timestamps directly causes collision/ambiguity issues during the autumn DST transition (when the 02:00–03:00 window repeats).

* **Solution**: All records are stored normalized in pure UTC. When requests are served, the analytical layer (Pandas) applies `tz_convert("Europe/Madrid")` and formats outputs with explicit ISO offsets (e.g., `+01:00` or `+02:00`), ensuring mathematical consistency across daylight transitions.

### 3. Frontend Architecture & Domain Usability

* **Dual-Axis Dynamic Visualization**: Atmospheric pressure ranges from \~980 to \~1005 hPa, while wind speed and temperature typically range between -15 and +15. Plotting them on a single Cartesian axis flattens wind and temperature curves. A dual-axis layout (`left: Speed/Temp`, `right: Pressure`) with automatic domain scaling ensures both profiles remain clearly readable.

* **KPI Summary Cards**: Provides operational metrics directly in the client (Average Wind Speed, Peak Wind Gust, Mean Barometric Pressure, Minimum Temperature) to allow immediate evaluation of turbine cut-in and cut-out limits without manual data scanning.

* **Client-Side CSV Export**: Avoids redundant backend roundtrips by serializing the active filtered dataset into a `Blob` and initiating an in-browser download.

* **Evaluator Quick Presets**: Integrated one-click scenarios (24-Hour Scan, Antarctic Summer Week, Antarctic Winter DST Week) to allow evaluators to verify temporal edge cases instantly.

## Project Structure

```
aemet-wind-farm/
├── app/
│   ├── services/
│   │   ├── aemet_client.py    # Asynchronous two-step AEMET API client
│   │   └── aggregator.py      # Pandas resampling and timezone logic
│   ├── config.py              # Environment configuration (pydantic-settings)
│   ├── database.py            # SQLAlchemy engine and session lifecycle
│   ├── main.py                # FastAPI application endpoints and routing
│   └── models.py              # SQLite declarative ORM models
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WeatherChart.tsx     # Recharts dual-axis visualization
│   │   │   ├── WeatherKpiCards.tsx  # Executive summary cards
│   │   │   └── WeatherTable.tsx     # Formatted observations tabular view
│   │   ├── services/
│   │   │   └── weatherApi.ts        # Typed API communication layer
│   │   ├── types/
│   │   │   └── weather.ts           # Shared TypeScript interfaces
│   │   ├── utils/
│   │   │   └── exportCsv.ts         # Client-side CSV generator
│   │   ├── App.tsx                  # Main exploratory dashboard layout
│   │   └── main.tsx                 # React entry point
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── __init__.py
│   └── test_aggregator.py     # Pytest unit tests (DST offsets & resampling)
├── .env.example               # Template for required environment variables
├── .gitignore                 # Exclusion rules (secrets, venv, SQLite DB)
├── requirements.txt           # Python dependencies
└── README.md

```

## Getting Started

### Prerequisites

* Python 3.10+

* Node.js 18+ and npm

* An active [AEMET OpenData API Key](https://opendata.aemet.es/centrodedescargas/altaUsuario)

### Backend Setup

1. **Create and activate a virtual environment**:

   ```
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   
   ```

2. **Install Python dependencies**:

   ```
   pip install -r requirements.txt
   
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:

   ```
   cp .env.example .env
   
   ```

   Open `.env` and assign your key:

   ```
   AEMET_API_KEY=your_aemet_api_key_here
   DATABASE_URL=sqlite:///./weather_data.db
   
   ```

4. **Run the Backend Server**:

   ```
   uvicorn app.main:app --reload
   
   ```

   * OpenAPI Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

   * ReDoc: `http://127.0.0.1:8000/redoc`

5. **Run Unit Tests**:

   ```
   pytest
   
   ```

### Frontend Setup

1. **Navigate to the frontend directory**:

   ```
   cd frontend
   
   ```

2. **Install dependencies**:

   ```
   npm install
   
   ```

3. **Start the development server**:

   ```
   npm run dev
   
   ```

   Open your browser at `http://localhost:5173` to access the interactive dashboard.

## API Specification

### `GET /api/antartida/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{estacionId}`

Retrieves and aggregates meteorological timeseries data for the specified station and range.

#### Parameters:

* `fechaIniStr` (path, string, format: `AAAA-MM-DDTHH:MM:SS`): Inclusive start timestamp.

* `fechaFinStr` (path, string, format: `AAAA-MM-DDTHH:MM:SS`): Inclusive end timestamp.

* `estacionId` (path, string): Station identifier or display name (`Meteo Station Gabriel de Castilla` / `89064` or `Meteo Station Juan Carlos I` / `89060`).

* `aggregation` (query, optional): Aggregation method (`None`, `Hourly`, `Daily`, `Monthly`). Defaults to `None`.

* `data_types` (query, optional): Metrics to filter (`temperature`, `speed`, `pressure`).

#### Sample Response:

```
[
  {
    "Station": "JCI Estacion meteorologica",
    "Datetime": "2024-01-01T01:00:00+01:00",
    "Temperature (°C)": 2.35,
    "Pressure (hpa)": 991.0,
    "Speed (m/s)": 1.27
  },
  {
    "Station": "JCI Estacion meteorologica",
    "Datetime": "2024-01-01T02:00:00+01:00",
    "Temperature (°C)": 2.03,
    "Pressure (hpa)": 991.45,
    "Speed (m/s)": 1.25
  }
]

```

## Verification & Automated Testing

Automated verification tests are implemented in `tests/test_aggregator.py` using `pytest`:

* **Time Resampling**: Validates arithmetic mean calculations when grouping raw 10-minute records into hourly, daily, and monthly intervals.

* **DST Offsets**: Verifies correct handling of CET (`+01:00`) during winter observations and CEST (`+02:00`) during summer periods.

* **Selective Metrics**: Verifies payload reduction when specific metric parameters (`data_types`) are provided.