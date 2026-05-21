from fastapi import APIRouter
from app.api.endpoints import catalog, tiler, indices

api_router = APIRouter()

api_router.include_router(catalog.router, prefix="/catalog", tags=["Catalog & Search"])
api_router.include_router(tiler.router, prefix="/tiler", tags=["Tile Server"])
api_router.include_router(indices.router, prefix="/indices", tags=["Spectral Indices"])
