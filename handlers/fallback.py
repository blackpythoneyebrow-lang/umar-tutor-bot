"""
Fallback handler for Umar Tutor Bot.
Politely guides users to the interactive Web App when arbitrary text is received.
"""
from aiogram import Router, F
from aiogram.types import Message

from database.models import User
from keyboards.default_keyboards import get_webapp_inline_keyboard

router = Router(name="fallback")

@router.message(F.text)
async def fallback_to_app(message: Message, user: User = None):
    """If user types any unrecognized text message, remind them to open the Web App."""
    await message.answer(
        "✨ <b>Umar Tutor — Barcha imkoniyatlar siz uchun ochiq!</b> 🇬🇧\n\n"
        "Interaktiv darslar, audio talaffuzlar (🔊), grammatika, testlar va sun'iy intellekt speaking mashqlari Mini App ichida joylashgan.\n\n"
        "Ilovani ochish uchun pastdagi tugmani bosing:",
        reply_markup=get_webapp_inline_keyboard(user),
        parse_mode="HTML"
    )
