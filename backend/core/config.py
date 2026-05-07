from functools import lru_cache # decorador que armazena em cache os resultados de uma função.
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configs da env
class Settings(BaseSettings):
    APP_NAME: str = "Logged"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    WHATSAPP_FAKE_MODE: bool = True
    WHATSAPP_API_URL: str = ""
    WHATSAPP_API_TOKEN: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
