from __future__ import annotations

from pydantic_settings import BaseSettings
from typing import Optional


class AppSettings(BaseSettings):
    """Application settings using pydantic-settings.

    Extend with Dolphin configuration.
    """

    app_name: str = "ORCA"
    debug: bool = True
    database_url: Optional[str] = "sqlite:///orca.db"

    # Dolphin API configuration
    dolphin_base_url: str = "https://api.dolphin.example"
    dolphin_api_token: Optional[str] = None
    dolphin_timeout: float = 10.0
    dolphin_retry_count: int = 3

    class Config:
        env_prefix = "ORCA_"


settings = AppSettings()
