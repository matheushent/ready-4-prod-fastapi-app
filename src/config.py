"""This module defines the static configurations of the FastAPI application.

It includes settings and constants that are used throughout the application
to ensure consistent behavior and configuration management.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """The configuration settings for the FastAPI application.

    This class defines the
    """

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_HOST_READ_ONLY: Optional[str] = None
    DB_PORT: int = 5432

    model_config = SettingsConfigDict(env_file=".env")


settings = Config()
