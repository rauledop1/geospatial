"""
Tile service — reads COG files and renders PNG XYZ tiles on the fly.

Performance optimisations applied:
  - HTTPS access to public S3 (no SDK overhead, no auth round-trips)
  - GDAL VSI cache (VSI_CACHE=TRUE) set in config.py
  - Per-process in-memory LRU cache on STAC asset resolution
  - Percentile auto-stretch per tile (avoids full-scene stats download)
  - Each band COG read independently so only the needed HTTP ranges are fetched
"""
import numpy as np
import requests
from functools import lru_cache
from rio_tiler.io import Reader
from rio_tiler.models import ImageData
from rio_tiler.colormap import cmap
from app.services.index_service import index_service
from app.services.datasource import resolve_asset_url

STAC_SEARCH_URL = "https://stac.scitekno.com.br/v100/search"


@lru_cache(maxsize=512)
def _get_scene_assets_cached(scene_id: str) -> dict:
    """
    Cached STAC asset resolver — the cache survives the process lifetime so
    repeated tile requests for the same scene skip the HTTP round-trip.
    """
    try:
        response = requests.post(
            STAC_SEARCH_URL, json={"ids": [scene_id]}, timeout=10
        )
        if response.status_code == 200:
            features = response.json().get("features", [])
            if features:
                return {
                    k: resolve_asset_url(v.get("href", ""))
                    for k, v in features[0].get("assets", {}).items()
                }
    except Exception as exc:
        print(f"[tiler] Error resolving assets for {scene_id}: {exc}")
    return {}


def _band_keys(scene_id: str) -> tuple:
    """Return (red, green, blue, nir) asset key names based on sensor."""
    if "MUX" in scene_id:
        return "B7", "B6", "B5", "B8"
    if "WFI" in scene_id:
        return "B15", "B14", "B13", "B16"
    if "WPM" in scene_id:
        return "B3", "B2", "B1", "B4"
    return "B7", "B6", "B5", "B8"  # sensible default


def _read_band(url: str, x: int, y: int, z: int) -> tuple:
    """Read a single band tile; returns (data_array, mask_array)."""
    with Reader(url) as src:
        img = src.tile(x, y, z)
    return img.data[0], img.mask


def _auto_stretch(data: np.ndarray) -> np.ndarray:
    """Percentile linear stretch — 2 % / 98 % per band → uint8."""
    out = np.zeros_like(data, dtype=np.uint8)
    for b in range(data.shape[0]):
        p2, p98 = np.percentile(data[b], (2, 98))
        if p98 <= p2:
            p98 = p2 + 1
        out[b] = np.clip((data[b] - p2) / (p98 - p2) * 255, 0, 255).astype(np.uint8)
    return out


class TilerService:

    def render_tile(
        self,
        scene_id: str,
        index: str,
        colormap: str,
        x: int,
        y: int,
        z: int,
    ) -> bytes:
        assets = _get_scene_assets_cached(scene_id)
        if not assets:
            raise ValueError(f"No se encontraron activos para la escena '{scene_id}'.")

        b_red, b_green, b_blue, b_nir = _band_keys(scene_id)

        # ── NDVI ──────────────────────────────────────────────────────────────
        if index == "ndvi":
            for key, label in [(b_red, "Red"), (b_nir, "NIR")]:
                if key not in assets:
                    raise ValueError(f"La escena no tiene la banda {label} ({key}) para NDVI.")
            red, m_r = _read_band(assets[b_red], x, y, z)
            nir, m_n = _read_band(assets[b_nir], x, y, z)
            idx = index_service.calculate_ndvi(red, nir)
            scaled = ((idx + 1) / 2 * 255).astype(np.uint8)[np.newaxis]
            img = ImageData(scaled, m_r & m_n)
            return img.render(img_format="PNG", colormap=cmap.get(colormap or "rdylgn"))

        # ── NDWI ──────────────────────────────────────────────────────────────
        elif index == "ndwi":
            for key, label in [(b_green, "Green"), (b_nir, "NIR")]:
                if key not in assets:
                    raise ValueError(f"La escena no tiene la banda {label} ({key}) para NDWI.")
            green, m_g = _read_band(assets[b_green], x, y, z)
            nir, m_n = _read_band(assets[b_nir], x, y, z)
            idx = index_service.calculate_ndwi(green, nir)
            scaled = ((idx + 1) / 2 * 255).astype(np.uint8)[np.newaxis]
            img = ImageData(scaled, m_g & m_n)
            return img.render(img_format="PNG", colormap=cmap.get(colormap or "coolwarm"))

        # ── RGB (natural colour) ───────────────────────────────────────────────
        else:
            for key, label in [(b_red, "Red"), (b_green, "Green"), (b_blue, "Blue")]:
                if key not in assets:
                    raise ValueError(f"La escena no tiene la banda {label} ({key}) para RGB.")
            r, m_r = _read_band(assets[b_red],   x, y, z)
            g, m_g = _read_band(assets[b_green], x, y, z)
            b, m_b = _read_band(assets[b_blue],  x, y, z)
            rgb = _auto_stretch(np.stack([r, g, b]))
            img = ImageData(rgb, m_r & m_g & m_b)
            return img.render(img_format="PNG")


tiler_service = TilerService()
