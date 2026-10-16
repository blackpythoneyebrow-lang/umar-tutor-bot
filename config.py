"""
Configuration settings for Umar Tutor Bot.
Loaded from environment variables or .env file.
"""
import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ==============================================================================
# 👑 ADMIN TELEGRAM ID RO'YXATI (ADMIN LIST)
# Bu yerga 1 ta, 2 ta, 3 ta yoki istalgancha admin Telegram ID sini yozishingiz mumkin!
# Masalan: [786373932] yoki [786373932, 123456789, 987654321]
# Ushbu ID egalari botga yoki Mini App'ga kirganda avtomatik O'qituvchi/Admin huquqini oladi!
# ==============================================================================
ADMIN_TELEGRAM_IDS = [
    786373932,   # 1-Admin (Bosh admin)
    8737899414,  # 2-Admin
    2011411073,  # 3-Admin
]

DEFAULT_WEBAPP_URL = "https://umar-tutor-bot.onrender.com"

class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str = "8857569388:AAFYJKztG3v4fnYlYA7lwhyVi8GpXW4O6f8"
    ADMIN_IDS: Union[str, List[int]] = ADMIN_TELEGRAM_IDS

    # Database
    DATABASE_PATH: str = "umar_tutor.db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./umar_tutor.db"

    # Deployment / Webhook & Web App
    USE_WEBHOOK: bool = False
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"
    WEBAPP_URL: str = DEFAULT_WEBAPP_URL  # Production default
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
        return DEFAULT_WEBAPP_URL

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        res = []
        if isinstance(v, list):
            res = [int(x) for x in v if str(x).strip()]
        elif isinstance(v, str):
            clean_str = v.strip()
            if clean_str:
                res = [int(x.strip()) for x in clean_str.split(",") if x.strip().isdigit()]
        elif isinstance(v, int):
            res = [v]
        # Always merge hardcoded ADMIN_TELEGRAM_IDS
        for aid in ADMIN_TELEGRAM_IDS:
            if aid not in res:
                res.append(aid)
        return res

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v, info):
        if v and "sqlite" in v:
            return v
        db_path = info.data.get("DATABASE_PATH", "umar_tutor.db")
        return f"sqlite+aiosqlite:///{db_path}"

    def is_admin(self, telegram_id) -> bool:
        """Check if a given telegram ID has admin privileges."""
        if not telegram_id:
            return False
        try:
            tid = int(telegram_id)
            if tid in ADMIN_TELEGRAM_IDS:
                return True
            if isinstance(self.ADMIN_IDS, list):
                return tid in self.ADMIN_IDS
            return tid in [int(x.strip()) for x in str(self.ADMIN_IDS).split(",") if x.strip().isdigit()]
        except (ValueError, TypeError):
            return False

settings = Settings()
