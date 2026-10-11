"""
Start and Mini App launcher handler for Umar Tutor Bot.
Designed exclusively for Telegram WebApp experience without line buttons.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import settings
from database.models import User
from keyboards.default_keyboards import get_webapp_inline_keyboard, get_remove_keyboard

router = Router(name="start")

WELCOME_TEXT = """
👋 **Assalomu alaykum, {name}!**

Xush kelibsiz! Men **"Umar Tutor"** — ingliz tilini interaktiv o'rganish bo'yicha shaxsiy Mini App yordamchingizman. 🇬🇧✨

🎯 **Ilova ichida barcha funksiyalar mavjud:**
• 🚀 **Placement Test**: Boshlang'ich darajani aniqlash (A1-C2)
• 📖 **Kunlik Lug'at**: Yangi so'zlar, fonetika (IPA) va audio talaffuz (🔊)
• 🎙 **Speaking Practice**: Ovoz yozish va sun'iy intellekt tahlili
• ✍️ **Grammar Correction**: Grammatik xatolarni aniqlash va tushuntirish
• 🎧 **Listening**: Dialoglarni eshitish va mashqlar
• 📊 **O'sish Statistikasi**: Kunlik streak (🔥), ballar va shaxsiy reja

Quyidagi **"🚀 Umar Tutor Ilovasini Ochish"** tugmasini bosing va zamonaviy interfeysdan foydalaning! 👇
"""

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user: User):
    """Handle /start command - removes old reply line buttons and presents WebApp button."""
    await state.clear()
    full_name = message.from_user.full_name

    # Clear any old line reply keyboard
    try:
        cleanup_msg = await message.answer("⏳", reply_markup=get_remove_keyboard())
        await cleanup_msg.delete()
    except Exception:
        pass

    # Send welcome card with WebApp button
    await message.answer(
        WELCOME_TEXT.format(name=full_name),
        reply_markup=get_webapp_inline_keyboard(),
        parse_mode="Markdown"
    )

@router.message(Command("help"))
@router.message(Command("app"))
async def cmd_help_app(message: Message):
    """Guide user to launch the Web App."""
    await message.answer(
        "🚀 **Umar Tutor** to'liq zamonaviy **Telegram Mini App** sifatida ishlaydi.\n\n"
        "Ilovani ochish uchun quyidagi tugmani bosing:",
        reply_markup=get_webapp_inline_keyboard(),
        parse_mode="Markdown"
    )

@router.message(F.text)
async def fallback_to_app(message: Message):
    """If user types any message, remind them to open the Web App."""
    await message.answer(
        "✨ Barcha darslar, testlar va mashg'ulotlar ilovamiz ichida joylashgan!\n\n"
        "Ilovani ochish uchun pastdagi tugmani bosing:",
        reply_markup=get_webapp_inline_keyboard(),
        parse_mode="Markdown"
    )
