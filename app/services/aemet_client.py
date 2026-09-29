import httpx
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Mapping user-friendly names to official AEMET station IDs
STATION_CODES = {
    "Meteo Station Juan Carlos I": "89060",
    "Meteo Station Gabriel de Castilla": "89064",
    "89060": "89060",
    "89064": "89064"
}

AEMET_BASE_URL = "https://opendata.aemet.es/opendata/api"


class AEMETClient:
    """
    HTTP Client handling the two-step retrieval workflow required by AEMET OpenData.
    Step 1: Request metadata returning a signed temporary URL in the 'datos' field.
    Step 2: Stream and parse the actual JSON payload from that temporary URL.
    """
    def __init__(self, api_key: str = settings.AEMET_API_KEY):
        self.api_key = api_key
        self.headers = {"api_key": self.api_key}

    async def fetch_antarctica_data(
        self, start_date_str: str, end_date_str: str, station_id: str
    ) -> List[Dict[str, Any]]:
        endpoint = (
            f"{AEMET_BASE_URL}/antartida/datos/fechaini/{start_date_str}"
            f"/fechafin/{end_date_str}/estacion/{station_id}"
        )

        async with httpx.AsyncClient(timeout=20.0) as client:
            logger.info(f"Step 1: Requesting download URL from AEMET: {endpoint}")
            response = await client.get(endpoint, headers=self.headers)

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