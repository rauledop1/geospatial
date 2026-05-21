from fastapi import APIRouter, Query
from typing import Optional
from datetime import date
from app.services.stac_service import stac_service

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "catalog",
        "message": "STAC Catalog Service active."
    }

@router.get("/search")
async def search_scenes(
    sensor: str = Query("MUX", description="Sensor name (MUX, WPM, WFI)"),
    commune: Optional[str] = Query(None, description="Commune name"),
    start_date: str = Query("2020-01-01", description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(default=None, description="End date (YYYY-MM-DD), defaults to today")
):
    """
    Search endpoint that returns matching CBERS-4A scenes based on spatial and temporal parameters.
    """
    # Default end_date to today so we always include the latest scenes
    if not end_date:
        end_date = date.today().isoformat()

    # Expanded bboxes give better chance of catching scenes
    # (CBERS-4A scenes are large but Chile is narrow, need some margin)
    bbox = [-73.0, -34.5, -69.5, -32.0]  # Default: Greater Santiago region
    
    if commune:
        commune_clean = commune.lower().strip()
        if "valparaiso" in commune_clean or "valparaíso" in commune_clean:
            bbox = [-72.5, -33.5, -70.5, -32.5]
        elif "concepcion" in commune_clean or "concepción" in commune_clean:
            bbox = [-74.5, -37.5, -72.0, -36.0]
        elif "santiago" in commune_clean:
            bbox = [-71.5, -34.0, -70.0, -33.0]
            
    scenes = stac_service.search_scenes(
        sensor=sensor,
        bbox=bbox,
        start_date=start_date,
        end_date=end_date,
        limit=50,
        sortby="-datetime"
    )
    
    return {
        "status": "success",
        "count": len(scenes),
        "results": scenes
    }
