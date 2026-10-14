"""
Configuration settings for Umar Tutor Bot.
Loaded from environment variables or .env file.
"""
import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"
    ADMIN_IDS: Union[str, List[int]] = ""

    # Database
    DATABASE_PATH: str = "umar_tutor.db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./umar_tutor.db"

    # Deployment / Webhook & Web App
    USE_WEBHOOK: bool = False
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"
    WEBAPP_URL: str = ""  # WebApp URL (empty = auto cloudflared tunnel locally, or https://... in prod)
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", 8080))

    # Learning defaults
    DAILY_WORDS_TARGET: int = 5
    PASSING_TEST_PERCENTAGE: float = 70.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("WEBAPP_URL", mode="before")
    @classmethod
    def assemble_webapp_url(cls, v):
        if v and str(v).strip().startswith("https://"):
            return str(v).strip()
        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if render_url and render_url.startswith("https://"):
            return render_url
        return ""

    @field_validator("ADMIN_IDS", mode="before")

    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, list):
            return [int(x) for x in v if str(x).strip()]
        if isinstance(v, str):
            clean_str = v.strip()
            if not clean_str:
                return []
            return [int(x.strip()) for x in clean_str.split(",") if x.strip().isdigit()]
        if isinstance(v, int):
            return [v]
        return []

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v, info):
        if v and "sqlite" in v:
            return v
        db_path = info.data.get("DATABASE_PATH", "umar_tutor.db")
        return f"sqlite+aiosqlite:///{db_path}"

settings = Settings()
