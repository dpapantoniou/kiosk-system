
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Court Feedback Kiosk Backend"
    database_url: str = "sqlite:///./kiosk.db"  # start simple; move to PostgreSQL next

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
