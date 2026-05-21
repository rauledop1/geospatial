from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.router import api_router
import os

app = FastAPI(
    title=settings.APP_NAME,
    description="API de procesamiento espacial para el monitoreo comunal en Chile con CBERS-4A",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── JSON API routes (must come BEFORE static mount) ──
app.include_router(api_router, prefix="/api/v1")

# Health endpoint – needed by the frontend connectivity check
@app.get("/api/health")
async def health():
    return {"status": "active", "app": settings.APP_NAME, "version": "1.0.0"}

# ── Static frontend (served last so API routes take priority) ──
frontend_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
