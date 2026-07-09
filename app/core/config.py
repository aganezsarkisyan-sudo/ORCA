from __future__ import annotations

from pydantic_settings import BaseSettings
from typing import Optional


class AppSettings(BaseSettings):
    """Application settings using pydantic-settings.

    Currently minimal — extend as needed.
    """

    app_name: str = "ORCA"
    debug: bool = True
    database_url: Optional[str] = "sqlite:///orca.db"

    class Config:
        env_prefix = "ORCA_"


settings = AppSettings()
