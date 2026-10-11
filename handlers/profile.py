"""
Student profile and progress tracking handler for Umar Tutor Bot.
Displays CEFR level, daily streaks, test scores, and statistics.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.crud import get_user_by_telegram_id, get_user_learned_count
from keyboards.inline_keyboards import get_profile_actions_keyboard

router = Router(name="profile")

def format_profile_text(user: User, learned_words_count: int) -> str:
    """Formats student profile card matching the UI mockup design."""
    level = user.level if user.level else "Aniqlanmagan"
    streak = user.streak_days or 1
    tests = user.tests_completed or 0
    hw = user.homeworks_completed or 0
    speaking = user.speaking_completed or 0
    score = user.total_score or 0

    # Calculate overall accuracy/activity rating
    total_activities = tests + hw + speaking
    activity_status = "🚀 Faol o'rganuvchi" if total_activities > 5 else "🌱 Yangi boshlovchi"

    return (
        f"👤 **O'quvchi Profili:** `{user.full_name}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎖 **CEFR Darajangiz:** ⭐️ **{level}** ⭐️\n"
        f"🔥 **Kunlik Streak:** `{streak}` kun ketma-ket!\n"
        f"⭐️ **Umumiy to'plangan ball:** `{score}` ball\n"
        f"⚡️ **Status:** {activity_status}\n\n"
        f"📊 **Bajarilgan Mashg'ulotlar:**\n"
        f"• 🎯 Daraja testlari: `{tests}` ta\n"
        f"• 📚 Dars va vazifalar: `{hw}` ta\n"
        f"• 🎙 Ovozli (Speaking) mashqlar: `{speaking}` ta\n"
        f"• 🔤 O'rganilgan so'zlar: `{learned_words_count}` ta\n\n"
        f"🎯 **Maqsad:** Har kuni 15 daqiqa ingliz tili amaliyoti!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌟 *\"Small steps every day lead to big results.\"*"
    )

@router.message(F.text == "📊 Mening Profilim")
async def show_profile_message(message: Message, session: AsyncSession, user: User):
    """Entry point for Profile via main menu."""
    if not user:
        user = await get_user_by_telegram_id(session, message.from_user.id)
    
    learned_count = await get_user_learned_count(session, user.id) if user else 0
    text = format_profile_text(user, learned_count)
    await message.answer(text, reply_markup=get_profile_actions_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "goto_profile")
@router.callback_query(F.data == "refresh_profile")
async def callback_show_profile(callback: CallbackQuery, session: AsyncSession, user: User):
    """Profile view via inline callback."""
    if not user:
        user = await get_user_by_telegram_id(session, callback.from_user.id)

    learned_count = await get_user_learned_count(session, user.id) if user else 0
    text = format_profile_text(user, learned_count)
    await callback.message.edit_text(text, reply_markup=get_profile_actions_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "goto_plan")
async def callback_show_plan_from_profile(callback: CallbackQuery, user: User):
    """Shows learning plan from profile."""
    from handlers.start import LEARNING_PLAN_TEXT
    level_str = user.level if user else "Aniqlanmagan"
    plan_header = f"🎯 **Hozirgi darajangiz:** `{level_str}`\n\n"
    await callback.message.edit_text(
        plan_header + LEARNING_PLAN_TEXT,
        reply_markup=get_profile_actions_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
