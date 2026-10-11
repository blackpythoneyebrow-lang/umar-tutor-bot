"""
Keyboards module for Umar Tutor Bot.
Line reply buttons are removed so the user only interacts via Telegram WebApp (Mini App).
"""
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import settings

def get_remove_keyboard() -> ReplyKeyboardRemove:
    """Removes any persistent reply keyboard from the user screen."""
    return ReplyKeyboardRemove()

def get_webapp_inline_keyboard() -> InlineKeyboardMarkup:
    """Returns clean inline button to launch the WebApp."""
    url = settings.WEBAPP_URL if settings.WEBAPP_URL else "https://telegram.org"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Umar Tutor Ilovasini Ochish (Mini App)",
                web_app=WebAppInfo(url=url)
            )
        ]
    ])
