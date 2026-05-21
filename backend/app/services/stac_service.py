import requests
from typing import List, Dict, Any
from app.config import settings

STAC_API_URL = "https://stac.scitekno.com.br/v100"

# Map frontend sensor names → STAC collection IDs
SENSOR_TO_COLLECTION = {
    "MUX": "CBERS4A-MUX",
    "WPM": "CBERS4A-WPM",
    "WFI": "CBERS4A-WFI",
}

class STACService:

    def search_scenes(
        self,
        sensor: str,
        bbox: List[float],
        start_date: str,
        end_date: str,
        limit: int = 50,
        sortby: str = "-datetime",
    ) -> List[Dict[str, Any]]:
        """
        Searches the CBERS-4A STAC catalog for scenes intersecting the bbox.

        :param sensor:     MUX | WPM | WFI
        :param bbox:       [min_lng, min_lat, max_lng, max_lat]
        :param start_date: YYYY-MM-DD
        :param end_date:   YYYY-MM-DD
        :param limit:      Max number of scenes to return (default 50)
        :param sortby:     STAC sort field (default: newest first)
        """
        collection = SENSOR_TO_COLLECTION.get(sensor.upper(), "CBERS4A-MUX")

        payload: Dict[str, Any] = {
            "bbox": bbox,
            "collections": [collection],
            "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
            "limit": limit,
            "sortby": [sortby],
        }

        try:
            response = requests.post(
                f"{STAC_API_URL}/search", json=payload, timeout=20
            )
            if response.status_code != 200:
                print(
                    f"[stac] Search returned HTTP {response.status_code}: "
                    f"{response.text[:200]}"
                )
                return []

            features = response.json().get("features", [])
            return [
                {
                    "id":         feat["id"],
                    "datetime":   feat["properties"].get("datetime"),
                    "collection": feat.get("collection"),
                    "bbox":       feat.get("bbox"),
                    "assets": {
                        k: {"href": v.get("href"), "title": v.get("title")}
                        for k, v in feat.get("assets", {}).items()
                    },
                }
                for feat in features
            ]

        except Exception as exc:
            print(f"[stac] Error querying catalog: {exc}")
            return []


stac_service = STACService()
