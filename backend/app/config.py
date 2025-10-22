"""Application configuration settings."""
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration for the FastAPI application."""

    app_name: str = Field("Tool Maintenance Management System API", description="Human friendly service name.")
    environment: str = Field("development", description="Runtime environment identifier.")
    database_url: str = Field("sqlite+aiosqlite:///./tool_maintenance.db", description="SQLAlchemy database URL.")
    access_token_secret: str = Field("change-me", description="Secret used for signing JWT access tokens.")
    access_token_expire_minutes: int = Field(60 * 8, description="Default access token lifetime in minutes.")
    api_prefix: str = Field("/api", description="Base path for API routes.")
    cors_origins: list[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins.")
    api_port: int = Field(6000, description="Port the HTTP server listens on by default.")
    debug: bool = Field(False, description="Enable debug mode.")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
