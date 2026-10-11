"""
Speaking Practice Hub handler for Umar Tutor Bot.
Includes shadowing prompts, free speech topics, voice evaluation, and curated resources.
"""
import json
import os
from typing import Dict, Any, List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.crud import save_speaking_submission, increment_user_stats
from utils.states import SpeakingStates
from services.speaking_evaluator import evaluate_voice_submission
from keyboards.inline_keyboards import (
    get_speaking_hub_keyboard,
    get_shadowing_list_keyboard,
    get_free_speech_list_keyboard,
    get_speaking_ready_keyboard,
)

router = Router(name="speaking")

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "speaking_topics.json")

def load_speaking_data() -> Dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

SPEAKING_DATA = load_speaking_data()

@router.message(F.text == "🎙 Speaking Practice")
@router.callback_query(F.data == "goto_speaking")
async def show_speaking_hub(event: Message | CallbackQuery, state: FSMContext):
    """Entry point for Speaking Hub."""
    await state.clear()
    text = (
        "🎙 **Speaking Practice Hub (Nutqni Rivojlantirish)**\n\n"
        "Ingliz tilida erkin gapirishning eng samarali yo'li — har kuni ovoz chiqarib mashq qilishdir! 🗣\n\n"
        "Quyidagi bo'limlardan birini tanlang:\n"
        "• 🗣 **Shadowing**: Tayyor jumlalarni ohang va intonatsiyaga qarab o'qib takrorlash.\n"
        "• 🎯 **Erkin Mavzular**: Berilgan savolga 20-50 soniya davomida o'z fikringizni bildirish.\n"
        "• 🌐 **Eng Yaxshi Ilovalar**: Talaffuz va suhbat uchun rasmiy manbalar va tavsiyalar."
    )
    markup = get_speaking_hub_keyboard()

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data == "speak_mode:shadowing")
async def list_shadowing_prompts(callback: CallbackQuery):
    """Show list of shadowing prompts."""
    prompts = SPEAKING_DATA.get("shadowing_prompts", [])
    text = (
        "🗣 **Shadowing Mashqlari**\n\n"
        "Quyidagi matnlardan birini tanlang. Uni baland ovozda, to'g'ri intonatsiya bilan o'qib, botga ovozli xabar qilib yuborasiz:"
    )
    await callback.message.edit_text(text, reply_markup=get_shadowing_list_keyboard(prompts), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "speak_mode:free")
async def list_free_speech_prompts(callback: CallbackQuery):
    """Show list of free speech prompts."""
    topics = SPEAKING_DATA.get("free_speech_prompts", [])
    text = (
        "🎙 **Erkin Nutq Mavzulari (Free Speech)**\n\n"
        "Mavzuni tanlang va unga tayyorlanib, 30-60 soniyalik ovozli xabar yuboring:"
    )
    await callback.message.edit_text(text, reply_markup=get_free_speech_list_keyboard(topics), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "speak_mode:resources")
async def show_speaking_resources(callback: CallbackQuery):
    """Show curated resources and apps for speaking practice."""
    resources = SPEAKING_DATA.get("curated_resources", [])
    buttons = []
    text_lines = ["🌐 **Tavsiya etilgan eng sara speaking platformalari:**\n"]

    for r in resources:
        text_lines.append(f"🔹 **{r['name']}**\n{r['description']}\n🔗 [Havolaga o'tish]({r['url']})\n")
        buttons.append([InlineKeyboardButton(text=f"↗️ {r['name']}", url=r['url'])])

    buttons.append([InlineKeyboardButton(text="⬅️ Speaking menyusiga qaytish", callback_data="goto_speaking")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        "\n".join(text_lines),
        reply_markup=markup,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data.startswith("shadow_sel:"))
async def select_shadowing_prompt(callback: CallbackQuery, state: FSMContext):
    """Show selected shadowing text card."""
    prompt_id = callback.data.split(":")[1]
    prompts = SPEAKING_DATA.get("shadowing_prompts", [])
    selected = next((p for p in prompts if p["id"] == prompt_id), None)

    if not selected:
        await callback.answer("Mavzu topilmadi.", show_alert=True)
        return

    await state.update_data(current_prompt=selected, prompt_type="shadowing")

    text = (
        f"🗣 **Shadowing: {selected['title']}** `[{selected['level']}]`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📜 **O'qilishi kerak bo'lgan matn:**\n\n"
        f"💬 *\"{selected['text']}\"*\n\n"
        f"📌 **Ko'rsatma:** {selected['instructions_uz']}\n\n"
        f"Tayyor bo'lsangiz, quyidagi tugmani bosing va ovozli xabar yuboring:"
    )
    await callback.message.edit_text(text, reply_markup=get_speaking_ready_keyboard(prompt_id), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("free_sel:"))
async def select_free_prompt(callback: CallbackQuery, state: FSMContext):
    """Show selected free topic card."""
    topic_id = callback.data.split(":")[1]
    topics = SPEAKING_DATA.get("free_speech_prompts", [])
    selected = next((t for t in topics if t["id"] == topic_id), None)

    if not selected:
        await callback.answer("Mavzu topilmadi.", show_alert=True)
        return

    await state.update_data(current_prompt=selected, prompt_type="free")

    text = (
        f"🎯 **Erkin Mavzu: {selected['topic']}**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🇺🇿 **Mavzu ma'nosi:**\n{selected['topic_uz']}\n\n"
        f"💡 **Tavsiya:** {selected['tips_uz']}\n\n"
        f"Tayyor bo'lsangiz, pastdagi tugmani bosing va ovozli xabaringizni yozib yuboring:"
    )
    await callback.message.edit_text(text, reply_markup=get_speaking_ready_keyboard(topic_id), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("voice_ready:"))
async def prepare_voice_recording(callback: CallbackQuery, state: FSMContext):
    """Prompt user to record and send voice note."""
    prompt_id = callback.data.split(":")[1]
    await state.set_state(SpeakingStates.waiting_voice)
    await state.update_data(prompt_id=prompt_id)

    text = (
        "🎙 **Ovozingizni kutmoqdaman!**\n\n"
        "Iltimos, Telegram mikrofon tugmasini bosib, ovozli xabar (voice message) yozing va yuboring.\n\n"
        "⏱ *Tavsiya etiladigan muddat: 10 - 45 soniya.*"
    )
    cancel_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="goto_speaking")]
    ])
    await callback.message.edit_text(text, reply_markup=cancel_btn, parse_mode="Markdown")
    await callback.answer()

@router.message(SpeakingStates.waiting_voice, F.voice)
async def handle_voice_message(message: Message, state: FSMContext, session: AsyncSession, user: User):
    """Evaluates incoming voice message."""
    data = await state.get_data()
    prompt_obj = data.get("current_prompt", {})
    prompt_id = data.get("prompt_id", "prompt")
    prompt_title = prompt_obj.get("title") or prompt_obj.get("topic") or "Speaking Mashqi"

    duration = message.voice.duration
    file_id = message.voice.file_id

    # Evaluate voice recording
    res = evaluate_voice_submission(duration, prompt_title)

    if not res["success"]:
        await message.answer(res["message"])
        return

    # Build AI Feedback card matching mobile UI mockup
    metrics_str = "\n".join(res["metrics"])
    minutes = duration // 60
    seconds = duration % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    feedback_text = (
        f"🤖 **AI Speaking Feedback & Tahlil**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎙 **Mavzu:** {prompt_title}\n"
        f"⏱ **Davomiyligi:** `{time_str}`\n"
        f"⭐️ **Baho:** `{res['score']} / 100` ball\n\n"
        f"📊 **Talaffuz va Sur'at:**\n{metrics_str}\n\n"
        f"💬 **Izoh:** {res['fluency_note']}\n\n"
        f"💡 **Tavsiya:** {res['tip']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎉 *Ovozli mashg'ulot muvaffaqiyatli saqlandi va ballar profilingizga qo'shildi!*"
    )

    # Save to database
    if user:
        await save_speaking_submission(
            session=session,
            user_id=user.id,
            prompt_id=prompt_id,
            prompt_text=prompt_title,
            file_id=file_id,
            duration=duration,
            score=res["score"],
            feedback=feedback_text
        )
        await increment_user_stats(session, user.id, speaking=1, score_points=30)

    await state.clear()

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎙 Yana mashq qilish", callback_data="goto_speaking")],
        [InlineKeyboardButton(text="📊 Mening Profilim", callback_data="goto_profile")]
    ])

    await message.answer(feedback_text, reply_markup=reply_markup, parse_mode="Markdown")

@router.message(SpeakingStates.waiting_voice, ~F.voice)
async def handle_non_voice_in_speaking(message: Message):
    """Handle text message when voice was expected."""
    await message.answer(
        "⚠️ Iltimos, yozma matn emas, balki Telegram mikrofoni orqali **ovozli xabar (voice note)** yuboring! 🎙\n\n"
        "Agar bekor qilmoqchi bo'lsangiz, '🔙 Asosiy menyu' tugmasini bosing."
    )
