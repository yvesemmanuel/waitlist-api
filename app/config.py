from pydantic_settings import BaseSettings
from enum import Enum
from typing import Optional
from pydantic import ConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prd"


class Settings(BaseSettings):
    APP_NAME: str = "Waitlist Management API"
    DATABASE_URL: str = "sqlite:///./waitlist.db"
    ENV: Environment = Environment.DEVELOPMENT
    WORKERS: int = 1
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = ConfigDict(env_file=".env")


settings = Settings()
