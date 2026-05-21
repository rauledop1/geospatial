from fastapi import APIRouter, Query, Response, HTTPException
from typing import Optional
from app.services.tiler_service import tiler_service

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "tiler",
        "message": "Tile Server active."
    }

@router.get("/tiles/{z}/{x}/{y}")
async def get_tile(
    z: int,
    x: int,
    y: int,
    scene_id: str = Query(..., description="The STAC Scene ID"),
    index: str = Query("raw", description="Spectral index (raw, ndvi, ndwi)"),
    colormap: Optional[str] = Query(None, description="Colormap name (e.g. rdylgn, coolwarm)")
):
    """
    Returns an XYZ web tile for a specific CBERS-4A scene, band rendering, or spectral index.
    """
    try:
        tile_bytes = tiler_service.render_tile(
            scene_id=scene_id,
            index=index,
            colormap=colormap,
            x=x,
            y=y,
            z=z
        )
        # Return raw image bytes with PNG headers
        return Response(content=tile_bytes, media_type="image/png")
    except Exception as e:
        print(f"Error serving tile {z}/{x}/{y} for scene {scene_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to render tile: {str(e)}"
        )
