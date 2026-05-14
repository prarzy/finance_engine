from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""
    
    APP_ENV: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    FX_CACHE_TTL_SECONDS: int = 300
    EXCHANGERATE_API_KEY: str
    ALLOWED_ORIGINS: list[str]
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


def get_settings() -> Settings:
    """FastAPI dependency to get the singleton settings instance."""
    return settings
