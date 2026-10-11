"""
Placement Test and CEFR Level Assessment handler for Umar Tutor Bot.
Features full diagnostic placement test and level-specific assessments (A1-C2).
"""
import json
import os
import random
from typing import List, Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.crud import save_placement_result, update_user_level, increment_user_stats
from utils.states import PlacementTestStates
from keyboards.inline_keyboards import (
    get_test_choice_keyboard,
    get_quiz_options_keyboard,
    get_test_finished_keyboard,
)

router = Router(name="testing")

# Load questions from JSON
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "placement_test.json")

def load_placement_questions() -> Dict[str, List[Dict[str, Any]]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

QUESTIONS_POOL = load_placement_questions()

def get_diagnostic_questions() -> List[Dict[str, Any]]:
    """
    Selects 2 questions from each CEFR level (A1, A2, B1, B2, C1, C2)
    totalling 12 well-distributed diagnostic questions.
    """
    selected = []
    for lvl in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        pool = QUESTIONS_POOL.get(lvl, [])
        sample_count = min(2, len(pool))
        sample = random.sample(pool, sample_count) if pool else []
        for q in sample:
            q_copy = dict(q)
            q_copy["tier"] = lvl
            selected.append(q_copy)
    return selected

def evaluate_cefr_level(score: int, total: int) -> str:
    """Calculates CEFR tier based on percentage in diagnostic test."""
    pct = (score / total) * 100 if total > 0 else 0
    if pct < 25:
        return "A1"
    elif pct < 45:
        return "A2"
    elif pct < 65:
        return "B1"
    elif pct < 80:
        return "B2"
    elif pct < 92:
        return "C1"
    else:
        return "C2"

LEVEL_DESCRIPTIONS = {
    "A1": "🟢 **A1 - Beginner (Boshlang'ich)**\nOddiy kundalik iboralarni va sodda gaplarni tushunasiz. Asosiy e'tiborni lug'at boyligini oshirish va Present Simple'ga qaratish tavsiya etiladi.",
    "A2": "🟢 **A2 - Elementary (Bazaviy)**\nO'zingiz, oilangiz va kundalik ehtiyojlar haqida erkin gapira olasiz. O'tgan zamon (Past Simple) va modal fe'llarni mustahkamlash zarur.",
    "B1": "🟡 **B1 - Intermediate (O'rta)**\nKo'p uchraydigan mavzularda erkin muloqot qila olasiz va fikrlaringizni bayon qilasiz. Murakkabroq zamonlar (Perfect tenses) va so'z boyligini kengaytirish lozim.",
    "B2": "🟡 **B2 - Upper-Intermediate (Yuqori o'rta)**\nMurakkab matnlarning asosiy mohiyatini tushunasiz va xorijliklar bilan ravon muloqot qila olasiz. Idiomalar va rasmiy tilni o'rganish tavsiya etiladi.",
    "C1": "🔴 **C1 - Advanced (Ilg'or)**\nKeng ko'lamdagi qiyin va uzun matnlarni chuqur tushunasiz. Til vositalaridan moslashuvchan va professional darajada foydalanasiz.",
    "C2": "🔴 **C2 - Proficiency (Mukammal)**\nOna tili darajasida so'zlasha olasiz. Har qanday akademik va nozik ma'nodagi suhbatlarni bemalol o'zlashtirasiz."
}

@router.message(F.text == "🎯 Darajani aniqlash (Test)")
async def test_menu_entry(message: Message, state: FSMContext):
    """Entry point for placement testing."""
    await state.clear()
    await message.answer(
        "🎯 **Ingliz tili darajangizni aniqlash bo'limi**\n\n"
        "Qaysi turdagi testni topshirmoqchisiz?\n\n"
        "⚡️ **Keng qamrovli test**: Barcha darajalardan (A1-C2) saralangan savollar orqali umumiy darajangiz aniqlanadi.\n"
        "🎯 **Alohida daraja testi**: Aniq bitta daraja (masalan, B1) bo'yicha 10 ta savolga javob berasiz.",
        reply_markup=get_test_choice_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "goto_test")
@router.callback_query(F.data == "test_restart")
async def callback_start_test(callback: CallbackQuery, state: FSMContext):
    """Callback to start test."""
    await state.clear()
    await callback.message.edit_text(
        "🎯 **Ingliz tili darajangizni aniqlash bo'limi**\n\nQaysi testni tanlaysiz?",
        reply_markup=get_test_choice_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("test_mode:"))
async def choose_test_mode(callback: CallbackQuery, state: FSMContext):
    """Prepares questions and starts test runner."""
    mode = callback.data.split(":")[1]

    if mode == "full":
        questions = get_diagnostic_questions()
        test_title = "Keng qamrovli Placement Test (A1-C2)"
    else:
        pool = QUESTIONS_POOL.get(mode, [])
        questions = random.sample(pool, min(10, len(pool))) if pool else []
        test_title = f"{mode} Daraja Testi"

    if not questions:
        await callback.answer("Savollar topilmadi.", show_alert=True)
        return

    await state.set_state(PlacementTestStates.taking_test)
    await state.update_data(
        questions=questions,
        current_index=0,
        score=0,
        mode=mode,
        test_title=test_title,
        history=[]
    )

    await show_question(callback.message, questions[0], 0, len(questions), is_edit=True)
    await callback.answer()

async def show_question(
    message: Message,
    question_data: Dict[str, Any],
    index: int,
    total: int,
    is_edit: bool = False
):
    """Renders single question card with options."""
    tier_badge = f" `[{question_data.get('tier')}]`" if "tier" in question_data else ""
    progress_bar = "🟩" * (index) + "⬜️" * (total - index)

    text = (
        f"📝 **Savol {index + 1}/{total}**{tier_badge}\n"
        f"{progress_bar}\n\n"
        f"❓ **{question_data['question']}**\n\n"
        f"Quyidagi javoblardan to'g'risini tanlang:"
    )

    markup = get_quiz_options_keyboard(question_data["options"], index, total)

    if is_edit:
        await message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data.startswith("ans:"), PlacementTestStates.taking_test)
async def process_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User):
    """Processes user's selected choice."""
    selected_idx = int(callback.data.split(":")[1])
    data = await state.get_data()

    questions = data["questions"]
    curr_idx = data["current_index"]
    score = data["score"]
    curr_q = questions[curr_idx]

    is_correct = (selected_idx == curr_q["correct"])
    new_score = score + (1 if is_correct else 0)

    # Save to history
    data["history"].append({
        "question": curr_q["question"],
        "is_correct": is_correct,
        "selected": curr_q["options"][selected_idx],
        "correct": curr_q["options"][curr_q["correct"]],
        "explanation": curr_q["explanation"]
    })

    # Show instant explanation modal / feedback card
    feedback_icon = "✅ **To'g'ri javob!**" if is_correct else "❌ **Noto'g'ri javob!**"
    explanation_text = (
        f"{feedback_icon}\n\n"
        f"📌 **Savol:** {curr_q['question']}\n"
        f"👉 **To'g'ri javob:** `{curr_q['options'][curr_q['correct']]}`\n\n"
        f"💡 **Izoh:** {curr_q['explanation']}"
    )

    next_idx = curr_idx + 1

    if next_idx < len(questions):
        # Update state for next question
        await state.update_data(current_index=next_idx, score=new_score)
        
        # Intermediate feedback with button to proceed
        next_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Keyingi savol ➡️ ({next_idx + 1}/{len(questions)})", callback_data="test_next_step")]
        ])
        await callback.message.edit_text(explanation_text, reply_markup=next_btn, parse_mode="Markdown")
    else:
        # Test finished! Calculate results
        await finish_test(callback.message, state, new_score, len(questions), session, user)

    await callback.answer()

@router.callback_query(F.data == "test_next_step", PlacementTestStates.taking_test)
async def next_question_step(callback: CallbackQuery, state: FSMContext):
    """Advances to next question."""
    data = await state.get_data()
    questions = data["questions"]
    curr_idx = data["current_index"]
    await show_question(callback.message, questions[curr_idx], curr_idx, len(questions), is_edit=True)
    await callback.answer()

async def finish_test(
    message: Message,
    state: FSMContext,
    final_score: int,
    total: int,
    session: AsyncSession,
    user: User
):
    """Calculates CEFR level, updates database, and shows stylish report card."""
    data = await state.get_data()
    mode = data.get("mode", "full")
    test_title = data.get("test_title", "Placement Test")

    pct = round((final_score / total) * 100, 1)

    if mode == "full":
        assigned_level = evaluate_cefr_level(final_score, total)
    else:
        assigned_level = mode if pct >= 70.0 else user.level or "A1"

    # Save to database
    if user:
        await save_placement_result(
            session=session,
            user_id=user.id,
            target_level=mode,
            score=final_score,
            total_questions=total,
            assigned_level=assigned_level
        )
        await update_user_level(session, user.telegram_id, assigned_level)
        await increment_user_stats(session, user.id, tests=1, score_points=final_score * 10)

    await state.clear()

    level_desc = LEVEL_DESCRIPTIONS.get(assigned_level, "")

    result_text = (
        f"🏆 **TABRIKLAYMIZ! TEST YAKUNLANDI** 🎓\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 **Test turi:** `{test_title}`\n"
        f"🎯 **Natijangiz:** `{final_score} / {total}` ball ({pct}%)\n"
        f"🎖 **Belgilangan Darajangiz:** ⭐️ **{assigned_level}** ⭐️\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{level_desc}\n\n"
        f"✨ *Darajangiz profilingizga muvaffaqiyatli saqlandi! Endi darslar va speaking mashqlarini boshlashingiz mumkin.*"
    )

    await message.edit_text(
        result_text,
        reply_markup=get_test_finished_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "test_quit")
@router.callback_query(F.data == "test_cancel")
async def cancel_test(callback: CallbackQuery, state: FSMContext):
    """Aborts current test session."""
    await state.clear()
    await callback.message.edit_text("❌ Test to'xtatildi. Istalgan vaqt qayta boshlashingiz mumkin.")
    await callback.answer()
