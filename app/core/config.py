from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str

    # Kipps platform
    KIPPS_API_KEY: str = ""
    KIPPS_VOICE_AGENT_ID: str = ""
    KIPPS_CHAT_AGENT_ID: str = ""
    KIPPS_BASE_URL: str = "https://backend.kipps.ai"
    KIPPS_WEBHOOK_URL: str = ""
    KIPPS_WEBHOOK_SECRET: str = ""
    # App
    APP_ENV: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
