from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Smart Banking API"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    cors_allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        validation_alias="CORS_ALLOWED_ORIGINS",
    )

    model_dir: str = str(BASE_DIR / "saved_models")
    dataset_path: str = str(BASE_DIR / "data" / "bank_customer_dataset.xlsx")

    database_url: str = Field(
        default=f"sqlite+aiosqlite:///{(BASE_DIR / 'smartbank.db').as_posix()}",
        validation_alias="DATABASE_URL",
    )

    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    max_upload_size_mb: int = Field(default=10, validation_alias="MAX_UPLOAD_SIZE_MB")
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")

    smtp_server: str = Field(default="smtp.gmail.com", validation_alias="SMTP_SERVER")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    sender_email: str = Field(default="smartbank.noreply@gmail.com", validation_alias="SENDER_EMAIL")
    sender_password: str = Field(default="", validation_alias="SENDER_PASSWORD")
    email_demo_mode: bool = Field(default=True, validation_alias="EMAIL_DEMO_MODE")

    @property
    def cors_origins_list(self) -> list[str]:
        parsed = [v.strip() for v in self.cors_allowed_origins.split(",") if v.strip()]
        return parsed or ["*"]

    @property
    def max_upload_size_bytes(self) -> int:
        return max(self.max_upload_size_mb, 1) * 1024 * 1024

    @property
    def GEMINI_API_KEY(self) -> str:
        return self.gemini_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
