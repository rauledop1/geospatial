import os
from pathlib import Path
from typing import Any, Dict
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App General Settings
    APP_NAME: str = "Geoportal Chile - CBERS-4A"
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # STAC API configuration
    STAC_API_URL: str = "https://brazildatacube.dpi.inpe.br/stac/"
    BDC_ACCESS_TOKEN: str = ""

    # AWS Credentials for reading COGs
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_NO_SIGN_REQUEST: bool = True

    # GDAL configuration for HTTP/S3 stream optimization
    GDAL_DISABLE_READDIR_ON_OPEN: str = "EMPTY_DIR"
    GDAL_HTTP_MERGE_CONSECUTIVE_PARTS: str = "YES"
    GDAL_NUM_THREADS: str = "ALL_CPUS"
    VSI_CACHE: str = "TRUE"
    VSI_CACHE_SIZE: int = 50000000

    # Load from .env file
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def set_gdal_env(self):
        """Sets environment variables for GDAL to read COGs directly from AWS S3."""
        os.environ["AWS_NO_SIGN_REQUEST"] = "YES" if self.AWS_NO_SIGN_REQUEST else "NO"
        if self.AWS_ACCESS_KEY_ID:
            os.environ["AWS_ACCESS_KEY_ID"] = self.AWS_ACCESS_KEY_ID
        if self.AWS_SECRET_ACCESS_KEY:
            os.environ["AWS_SECRET_ACCESS_KEY"] = self.AWS_SECRET_ACCESS_KEY
        os.environ["AWS_DEFAULT_REGION"] = self.AWS_DEFAULT_REGION
        os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = self.GDAL_DISABLE_READDIR_ON_OPEN
        os.environ["GDAL_HTTP_MERGE_CONSECUTIVE_PARTS"] = self.GDAL_HTTP_MERGE_CONSECUTIVE_PARTS
        os.environ["GDAL_NUM_THREADS"] = self.GDAL_NUM_THREADS
        os.environ["VSI_CACHE"] = self.VSI_CACHE
        os.environ["VSI_CACHE_SIZE"] = str(self.VSI_CACHE_SIZE)
        # Avoid hangs on flaky S3 calls
        os.environ["GDAL_HTTP_MAX_RETRY"] = "3"
        os.environ["GDAL_HTTP_RETRY_DELAY"] = "1"

def load_geoportal_config() -> Dict[str, Any]:
    """Loads geoportal YAML settings (ag.yaml)."""
    # config.py is at: project_root/backend/app/config.py
    # ag.yaml is at: project_root/ag.yaml
    root_path = Path(__file__).resolve().parent.parent.parent
    yaml_path = root_path / "ag.yaml"
    
    if yaml_path.exists():
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading ag.yaml: {e}")
            return {}
    return {}

# Instantiation and initialization
settings = Settings()
settings.set_gdal_env()
geoportal_config = load_geoportal_config()
