"""
Keyboards module for Umar Tutor Bot.
Line reply buttons are removed so the user only interacts via Telegram WebApp (Mini App).
"""
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import settings

CACHE_VERSION = "2.3"

def get_remove_keyboard() -> ReplyKeyboardRemove:
    """Removes any persistent reply keyboard from the user screen."""
    return ReplyKeyboardRemove()

def get_admin_welcome_keyboard(webapp_base_url: str = None, tg_id: int = None) -> InlineKeyboardMarkup:
    """Returns rich inline keyboard for Administrators with CMS, statistics, and student mode."""
    base = webapp_base_url or settings.WEBAPP_URL or "https://umar-tutor-bot.onrender.com"
    id_param = f"&user_id={tg_id}" if tg_id else ""
    url_admin = f"{base}?role=admin{id_param}&v={CACHE_VERSION}"
    url_student = f"{base}?role=student{id_param}&v={CACHE_VERSION}"
    url_cms = f"{base}?role=admin&tab=cms{id_param}&v={CACHE_VERSION}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👑 Admin Panel (CMS & Boshqaruv)",
                web_app=WebAppInfo(url=url_admin)
            )
        ],
        [
            InlineKeyboardButton(
                text="👁 O'quvchi rejimida kirish",
                web_app=WebAppInfo(url=url_student)
            ),
            InlineKeyboardButton(
                text="📝 Yangi Material (CMS)",
                web_app=WebAppInfo(url=url_cms)
            )
        ],
        [
            InlineKeyboardButton(text="📊 Bot Statistikasi", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 O'quvchilar Ro'yxati", callback_data="admin_students")
        ],
        [
            InlineKeyboardButton(text="📢 Barchaga Xabar Yuborish", callback_data="admin_broadcast")
        ]
    ])

def get_student_welcome_keyboard(webapp_base_url: str = None, user = None) -> InlineKeyboardMarkup:
    """Returns interactive inline keyboard for Students with WebApp launch, profile, and test."""
    base = webapp_base_url or settings.WEBAPP_URL or "https://umar-tutor-bot.onrender.com"
    code = user.access_code if user and user.access_code else "STU-0000"
    url_app = f"{base}?code={code}&v={CACHE_VERSION}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Umar Tutor Mini Appni Ochish",
                web_app=WebAppInfo(url=url_app)
            )
        ],
        [
            InlineKeyboardButton(text="📊 Mening Profilim", callback_data="goto_profile"),
            InlineKeyboardButton(text="🎯 Darajani Aniqlash Testi", callback_data="goto_test")
        ],
        [
            InlineKeyboardButton(text="📚 Darslar va Vazifalar", callback_data="goto_lessons"),
            InlineKeyboardButton(text="🎙 Speaking Mashqi", callback_data="goto_speaking")
        ],
        [
            InlineKeyboardButton(text="📋 Shaxsiy O'quv Rejasi", callback_data="goto_plan"),
            InlineKeyboardButton(text=f"🔑 Kod: {code}", callback_data="show_my_code")
        ]
    ])

def get_webapp_inline_keyboard(user = None) -> InlineKeyboardMarkup:
    """Returns appropriate inline keyboard depending on whether user is an Admin or Student."""
    base = settings.WEBAPP_URL or "https://umar-tutor-bot.onrender.com"
    if user:
        tg_id = getattr(user, "telegram_id", None)
        is_admin = settings.is_admin(tg_id) or getattr(user, "is_admin", False)
        if is_admin:
            return get_admin_welcome_keyboard(base, tg_id)
        return get_student_welcome_keyboard(base, user)
    return get_student_welcome_keyboard(base, user)
