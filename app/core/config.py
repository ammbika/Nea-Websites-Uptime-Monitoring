from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///monitor.db"
    CHECK_INTERVAL_SECONDS: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 10
    APP_TITLE: str = "Uptime Monitor"

    class Config:
        env_file = ".env"

settings = Settings()
