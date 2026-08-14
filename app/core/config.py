"""
Central place where ALL environment/config values live.
Nothing else in the codebase should call os.getenv() directly —
everything imports `settings` from here. This is the standard
production pattern: one source of truth for config.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str

    # Kipps platform
    KIPPS_API_KEY: str = ""
    KIPPS_VOICE_AGENT_ID: str = ""
    KIPPS_CHAT_AGENT_ID: str = ""
    KIPPS_BASE_URL: str = "https://backend.kipps.ai"

    # App
    APP_ENV: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Import this everywhere you need a config value: `from app.core.config import settings`
settings = Settings()
