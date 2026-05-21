from fastapi import APIRouter, Query
from typing import Optional
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
    start_date: str = Query("2022-01-01", description="Start date (YYYY-MM-DD)"),
    end_date: str = Query("2026-05-20", description="End date (YYYY-MM-DD)")
):
    """
    Search endpoint that returns matching CBERS-4A scenes based on spatial and temporal parameters.
    """
    # Default bounding box centered on Santiago de Chile
    bbox = [-70.9, -33.65, -70.4, -33.25]
    
    if commune:
        commune_clean = commune.lower().strip()
        if "valparaiso" in commune_clean or "valparaíso" in commune_clean:
            bbox = [-71.7, -33.15, -71.4, -32.9]
        elif "concepcion" in commune_clean or "concepción" in commune_clean:
            bbox = [-73.15, -36.9, -72.9, -36.7]
        elif "santiago" in commune_clean:
            bbox = [-70.9, -33.65, -70.4, -33.25]
            
    scenes = stac_service.search_scenes(
        sensor=sensor,
        bbox=bbox,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "status": "success",
        "count": len(scenes),
        "results": scenes
    }
