from fastapi import APIRouter
from app.config import geoportal_config

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "indices",
        "message": "Spectral Index Processing Service active."
    }

@router.get("/list")
async def list_indices():
    """
    Returns the list of available spectral indices and their configuration metadata.
    """
    indices = geoportal_config.get("spectral_indices", {})
    return {
        "status": "success",
        "indices": indices
    }
