from pydantic_settings import BaseSettings
from enum import Enum
from typing import Optional


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prd"


class Settings(BaseSettings):
    APP_NAME: str = "Barbershop Waitlist API"
    DATABASE_URL: str = "sqlite:///./barbershop.db"
    ENV: Environment = Environment.DEVELOPMENT
    WORKERS: int = 1  # Default to 1 worker, should be set via env var in production
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # TODO: Safety net for future authentication implementation
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
