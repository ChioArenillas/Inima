import httpx
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

STATION_CODES = {
    "Meteo Station Juan Carlos I": "89060",
    "Meteo Station Gabriel de Castilla": "89064",
    "89060": "89060",
    "89064": "89064"
}

AEMET_BASE_URL = "https://opendata.aemet.es/opendata/api"


class AEMETClient:
    def __init__(self, api_key: str = settings.AEMET_API_KEY):
        self.api_key = api_key.strip()
        self.headers = {
            "api_key": self.api_key,
            "cache-control": "no-cache"
        }

    async def fetch_antarctica_data(
        self, start_date_str: str, end_date_str: str, station_id: str
    ) -> List[Dict[str, Any]]:
        # AEMET requires datetime strings to terminate explicitly with 'UTC'
        formatted_start = start_date_str if start_date_str.endswith("UTC") else f"{start_date_str}UTC"
        formatted_end = end_date_str if end_date_str.endswith("UTC") else f"{end_date_str}UTC"

        endpoint = (
            f"{AEMET_BASE_URL}/antartida/datos/fechaini/{formatted_start}"
            f"/fechafin/{formatted_end}/estacion/{station_id}"
        )
        params = {"api_key": self.api_key}

        async with httpx.AsyncClient(timeout=25.0) as client:
            logger.info(f"Step 1: Requesting download URL from AEMET: {endpoint}")
            response = await client.get(endpoint, headers=self.headers, params=params)

            if response.status_code != 200:
                logger.error(
                    f"AEMET Step 1 failed: HTTP {response.status_code} - {response.text}"
                )
                return []

            meta_data = response.json()
            data_url = meta_data.get("datos")

            if not data_url:
                logger.warning(
                    f"AEMET did not provide a data URL: {meta_data.get('descripcion')}"
                )
                return []

            logger.info(f"Step 2: Fetching raw measurements from: {data_url}")
            data_response = await client.get(data_url)

            if data_response.status_code != 200:
                logger.error(
                    f"AEMET Step 2 failed: HTTP {data_response.status_code}"
                )
                return []

            return data_response.json()