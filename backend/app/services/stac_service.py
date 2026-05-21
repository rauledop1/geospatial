import requests
from typing import List, Dict, Any
from app.config import settings

class STACService:
    def __init__(self):
        # Fallback to SciTekno STAC if no BDC URL or Token is active/working
        self.api_url = "https://stac.scitekno.com.br/v100"
        
    def search_scenes(
        self,
        sensor: str,
        bbox: List[float],
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Searches STAC catalog for CBERS-4A scenes.
        :param sensor: MUX, WPM, or WFI
        :param bbox: [min_lng, min_lat, max_lng, max_lat]
        :param start_date: YYYY-MM-DD
        :param end_date: YYYY-MM-DD
        """
        # Map sensor selections to STAC collections
        sensor_map = {
            "MUX": "CBERS4A-MUX",
            "WPM": "CBERS4A-WPM",
            "WFI": "CBERS4A-WFI"
        }
        collection = sensor_map.get(sensor.upper(), "CBERS4A-MUX")
        
        # Build search payload
        payload = {
            "bbox": bbox,
            "collections": [collection],
            "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
            "limit": 10
        }
        
        try:
            response = requests.post(f"{self.api_url}/search", json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                
                results = []
                for feat in features:
                    results.append({
                        "id": feat.get("id"),
                        "datetime": feat.get("properties", {}).get("datetime"),
                        "bbox": feat.get("bbox"),
                        "collection": feat.get("collection"),
                        "assets": {
                            k: {
                                "href": v.get("href"),
                                "title": v.get("title")
                            } for k, v in feat.get("assets", {}).items()
                        }
                    })
                return results
            else:
                print(f"STAC search returned status {response.status_code}: {response.text[:200]}")
                return []
        except Exception as e:
            print(f"Error querying STAC API: {e}")
            return []

stac_service = STACService()
