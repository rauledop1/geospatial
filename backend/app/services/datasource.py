"""
Data-source abstraction layer.

STRATEGY PATTERN — change DATA_SOURCE_BACKEND in .env to switch between:
  "local"   → reads from data/cog/ directory on this machine
  "https"   → reads COGs via public HTTPS (no AWS SDK needed)  ← DEFAULT
  "s3"      → reads via s3:// protocol (requires AWS credentials)

When switching to a different bucket in the future, only CBERS_COG_BASE_URL
or the path prefix in _resolve_local() needs to change.
"""
import os
from typing import Dict, Optional

# Public HTTPS URL of the brazil-eosats open-data bucket (no credentials needed)
_HTTPS_BASE = "https://brazil-eosats.s3.amazonaws.com"

# Backend strategy: "local" | "https" | "s3"
DATA_SOURCE_BACKEND = os.getenv("DATA_SOURCE_BACKEND", "https").lower()

# Local COG root directory  (used when DATA_SOURCE_BACKEND == "local")
_LOCAL_COG_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "cog")
)


def resolve_asset_url(s3_href: str) -> str:
    """
    Converts any asset href to the correct format for the active backend.

    s3_href examples:
      - "s3://brazil-eosats/CBERS4A/MUX/.../BAND7.tif"
      - "https://brazil-eosats.s3.amazonaws.com/..."
    """
    # Normalise: strip s3:// prefix → relative path inside the bucket
    if s3_href.startswith("s3://brazil-eosats/"):
        relative = s3_href[len("s3://brazil-eosats/"):]
    elif s3_href.startswith(_HTTPS_BASE):
        relative = s3_href[len(_HTTPS_BASE) + 1:]  # +1 for the /
    else:
        # Unknown format – return as-is and let GDAL/rasterio handle it
        return s3_href

    if DATA_SOURCE_BACKEND == "local":
        return os.path.join(_LOCAL_COG_ROOT, relative)
    elif DATA_SOURCE_BACKEND == "s3":
        return f"s3://brazil-eosats/{relative}"
    else:  # "https" (default — no AWS SDK, no credentials)
        return f"{_HTTPS_BASE}/{relative}"
