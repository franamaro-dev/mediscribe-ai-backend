"""
MediScribe AI — Core Configuration.

Loads settings from environment variables via pydantic-settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ── OpenAI ───────────────────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./mediscribe.db"

    # ── App ──────────────────────────────────────────────────
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    APP_TITLE: str = "MediScribe AI"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "Backend para automatización de informes clínicos "
        "mediante IA (Speech-to-Text + NLP/LLM)."
    )


@lru_cache
def get_settings() -> Settings:
    """Singleton settings instance (cached)."""
    return Settings()
