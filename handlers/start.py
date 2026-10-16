"""
Start and Mini App launcher handler for Umar Tutor Bot.
Provides personalized greetings for Administrators and Students with direct access codes,
CEFR level, daily streaks, CMS access, and Mini App launcher.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import settings
from database.models import User
from keyboards.default_keyboards import (
    get_admin_welcome_keyboard,
    get_student_welcome_keyboard,
    get_webapp_inline_keyboard,
    get_remove_keyboard
)

router = Router(name="start")

# ==============================================================================
# WELCOME TEMPLATES & EDUCATIONAL TEXTS
# ==============================================================================

ADMIN_WELCOME_TEXT = """
👑 <b>Assalomu alaykum, Hurmatli Administrator {name}!</b>

⭐️ <b>Siz tizimda Boshqaruvchi (ADMIN / TEACHER) maqomiga egasiz!</b>
━━━━━━━━━━━━━━━━━━━━
🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>
🔑 <b>Shaxsiy kodingiz:</b> <code>{access_code}</code>
🛡 <b>Ruxsat darajasi:</b> <b>To'liq Admin (Barcha huquqlar faol)</b>
━━━━━━━━━━━━━━━━━━━━

⚡️ <b>Boshqaruv imkoniyatlari:</b>
• 📝 <b>CMS Boshqaruv:</b> Yangi darslar, lug'at, audio talaffuz (🔊), grammatika va testlar qo'shish hamda o'chirish
• 👥 <b>O'quvchilar Nazorati:</b> Barcha foydalanuvchilar ro'yxati, darajalari, o'zlashtirish foizlari
• ✍️ <b>Baholash Markazi:</b> O'quvchilar topshirgan speaking va writing ishlariga audio/matnli baho berish
• 🔴 <b>Jonli Darslar:</b> Telegram / Zoom / Google Meet darslarini e'lon qilish
• 📢 <b>Broadcast:</b> Barcha foydalanuvchilarga bitta bosishda xabar yuborish
• 👁 <b>Dual-Mode:</b> O'quvchi rejimida tizimni to'liq ko'rish va testlash

👇 <b>Quyidagi tugmalar orqali kerakli bo'limga o'ting:</b>
"""

STUDENT_WELCOME_TEXT = """
👋 <b>Assalomu alaykum, {name}!</b>

Men <b>"Umar Tutor"</b> — sizning shaxsiy interaktiv ingliz tili repetitoringizman! 🇬🇧✨
━━━━━━━━━━━━━━━━━━━━
🔑 <b>Shaxsiy o'quvchi kodingiz:</b> <code>{access_code}</code>
📊 <b>Darajangiz:</b> <b>{level}</b>
🔥 <b>Kunlik streak:</b> <b>{streak} kun ketma-ket</b>
⭐️ <b>To'plangan ballar:</b> <b>{score} ball</b>
━━━━━━━━━━━━━━━━━━━━

🎯 <b>Platformadagi asosiy imkoniyatlar:</b>
• 🚀 <b>Placement Test:</b> CEFR darajangizni aniqlash (A1 - C2)
• 📖 <b>Interaktiv Lug'at:</b> Yangi so'zlar, fonetika (IPA) va jonli audio talaffuz (🔊)
• 🎙 <b>AI Speaking Coach:</b> Ovoz yozish va nutqni sun'iy intellekt orqali tahlil qilish
• ✍️ <b>Grammar Checker:</b> Gaplardagi grammatik xatolarni topish va tushuntirish
• 🎧 <b>Listening & Shadowing:</b> Eshitish va talaffuzni mukammallashtirish
• 🔴 <b>Jonli Darslar:</b> Ustoz Umar bilan jonli muloqot va darslar

👇 <b>Quyidagi tugmani bosing va o'rganishni boshlang:</b>
"""

LEARNING_PLAN_TEXT = """
🎯 <b>Umar Tutor — 30 Kunlik Shaxsiy O'quv Rejasi</b>
━━━━━━━━━━━━━━━━━━━━
📌 <b>1-10 Kun (Foundation & Vocabulary):</b>
• Kunlik 5 ta yangi so'z, fonetika (IPA) va to'g'ri talaffuz (🔊)
• Present Simple & Past Simple zamonlarida sodda gaplar tuzish
• Boshlang'ich darajani mustahkamlash testlari

📌 <b>11-20 Kun (Grammar & Listening):</b>
• Perfect tenses, modal fe'llar va artikllar
• Listening mashqlari va audio dialoglarni tahlil qilish
• Kunlik mini-insholar va xatolarni Grammar Checker bilan tekshirish

📌 <b>21-30 Kun (Speaking & Shadowing):</b>
• Shadowing texnikasi orqali ona tili egalariga taqlid qilish
• AI Speaking Coach orqali ovozli javoblar va real-time tahlil
• CEFR darajani qayta baholash va keyingi bosqichga o'tish

🚀 <i>\"Muntazamlik — muvaffaqiyat garovidir! Har kuni 15 daqiqa shug'ullaning.\"</i>
"""

# ==============================================================================
# COMMANDS & CALLBACKS
# ==============================================================================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user: User):
    """Handle /start command with role detection (Admin vs Student)."""
    await state.clear()
    full_name = message.from_user.full_name
    tg_id = message.from_user.id

    is_admin = settings.is_admin(tg_id) or (user and user.is_admin)
    code = user.access_code if user and user.access_code else f"STU-{str(abs(tg_id))[-4:]}"
    base_url = settings.WEBAPP_URL or "https://umar-tutor-bot.onrender.com"

    # Clean old line reply keyboards if any
    try:
        cleanup_msg = await message.answer("⏳", reply_markup=get_remove_keyboard())
        await cleanup_msg.delete()
    except Exception:
        pass

    if is_admin:
        text = ADMIN_WELCOME_TEXT.format(
            name=full_name,
            telegram_id=tg_id,
            access_code=code
        )
        keyboard = get_admin_welcome_keyboard(base_url, tg_id)
    else:
        text = STUDENT_WELCOME_TEXT.format(
            name=full_name,
            access_code=code,
            level=user.level if user and user.level else "Starter",
            streak=user.streak_days if user and user.streak_days else 1,
            score=user.total_score if user and user.total_score else 0
        )
        keyboard = get_student_welcome_keyboard(base_url, user)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "menu_home")
async def callback_menu_home(callback: CallbackQuery, state: FSMContext, user: User):
    """Return to the main home greeting screen."""
    await state.clear()
    full_name = callback.from_user.full_name
    tg_id = callback.from_user.id

    is_admin = settings.is_admin(tg_id) or (user and user.is_admin)
    code = user.access_code if user and user.access_code else f"STU-{str(abs(tg_id))[-4:]}"
    base_url = settings.WEBAPP_URL or "https://umar-tutor-bot.onrender.com"

    if is_admin:
        text = ADMIN_WELCOME_TEXT.format(
            name=full_name,
            telegram_id=tg_id,
            access_code=code
        )
        keyboard = get_admin_welcome_keyboard(base_url, tg_id)
    else:
        text = STUDENT_WELCOME_TEXT.format(
            name=full_name,
            access_code=code,
            level=user.level if user and user.level else "Starter",
            streak=user.streak_days if user and user.streak_days else 1,
            score=user.total_score if user and user.total_score else 0
        )
        keyboard = get_student_welcome_keyboard(base_url, user)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "show_my_code")
async def callback_show_my_code(callback: CallbackQuery, user: User):
    """Popup alert displaying user's personal access PIN."""
    code = user.access_code if user and user.access_code else f"STU-{str(abs(callback.from_user.id))[-4:]}"
    await callback.answer(
        f"🔑 Sizning shaxsiy o'quvchi kodingiz: {code}\n\nUshbu kod orqali ilovaga kirishingiz va darslaringizni sinxronlashtirishingiz mumkin!",
        show_alert=True
    )

@router.message(Command("code"))
@router.message(Command("kod"))
async def cmd_my_code(message: Message, user: User):
    """Show personal access code."""
    code = user.access_code if user and user.access_code else f"STU-{str(abs(message.from_user.id))[-4:]}"
    await message.answer(
        f"🔑 <b>Sizning shaxsiy o'quvchi kodingiz:</b> <code>{code}</code>\n\n"
        f"Ushbu kod yordamida Umar Tutor ilovasida o'z profilingizga kirishingiz mumkin.",
        parse_mode="HTML"
    )

@router.message(Command("plan"))
@router.message(Command("reja"))
async def cmd_learning_plan(message: Message, user: User):
    """Show comprehensive 30-day learning curriculum."""
    level_str = user.level if user and user.level else "Starter"
    header = f"🎯 <b>Hozirgi darajangiz:</b> <code>{level_str}</code>\n\n"
    await message.answer(header + LEARNING_PLAN_TEXT, parse_mode="HTML")

@router.message(Command("help"))
@router.message(Command("app"))
async def cmd_help_app(message: Message, user: User):
    """Guide user to launch the Web App."""
    await message.answer(
        "🚀 <b>Umar Tutor</b> — ingliz tilini o'rganish bo'yicha to'liq interaktiv <b>Telegram Mini App</b>!\n\n"
        "Barcha audio talaffuzlar, daraja testlari, speaking mashqlari va grammatika tekshiruvi ilova ichida joylashgan.\n\n"
        "Ilovani ochish uchun quyidagi tugmani bosing:",
        reply_markup=get_webapp_inline_keyboard(user),
        parse_mode="HTML"
    )
