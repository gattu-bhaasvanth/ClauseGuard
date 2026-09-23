import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_ENV: str = "development"
    APP_NAME: str = "ClauseGuard"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database
    DATABASE_URL: str = ""

    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL or self.DATABASE_URL == "sqlite+aiosqlite:///./data/clauseguard.db":
            from pathlib import Path
            root_dir = Path(__file__).resolve().parent.parent.parent
            data_dir = root_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "clauseguard.db"
            self.DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

    # Security
    SECRET_KEY: str = "development-insecure-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Storage & Processing
    STORAGE_LOCAL_DIR: str = "./data/uploads"
    PROCESSED_DATA_DIR: str = "./data/processed"

    # LLM Settings
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
