"""
Homework and lesson checker handler for Umar Tutor Bot.
Supports multiple-choice quizzes and open-ended writing submissions with auto-evaluation.
"""
import json
import os
from typing import List, Dict, Any
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.crud import save_homework_submission, increment_user_stats
from utils.states import HomeworkStates
from keyboards.inline_keyboards import (
    get_lessons_list_keyboard,
    get_lesson_detail_keyboard,
    get_quiz_options_keyboard,
)

router = Router(name="homework")

# Load lessons data
HW_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "homework.json")

def load_homework_lessons() -> List[Dict[str, Any]]:
    with open(HW_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

LESSONS = load_homework_lessons()

def get_lesson_by_id(lesson_id: int) -> Dict[str, Any]:
    for l in LESSONS:
        if l["id"] == lesson_id:
            return l
    return None

@router.message(Command("lessons"))
@router.message(Command("darslar"))
@router.message(F.text == "📚 Darslar & Vazifalar")
@router.message(F.text == "📚 Darslar va Vazifalar")
@router.callback_query(F.data == "goto_lessons")
async def show_lessons_menu(event: Message | CallbackQuery, state: FSMContext):
    """Display list of available lessons."""
    await state.clear()
    text = (
        "📚 **Darslar va Vazifalar Bo'limi**\n\n"
        "Quyidagi darslardan birini tanlang. Har bir darsda qisqa grammatika qoidalari, "
        "avtomatik tekshiriladigan test va yozma (writing) vazifasi mavjud:"
    )
    markup = get_lessons_list_keyboard(LESSONS)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data.startswith("lesson_select:"))
async def select_lesson(callback: CallbackQuery, state: FSMContext):
    """Show details of chosen lesson."""
    lesson_id = int(callback.data.split(":")[1])
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        await callback.answer("Dars topilmadi.", show_alert=True)
        return

    text = (
        f"📖 **{lesson['title']}** `[{lesson['level']}]`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 **Mavzu haqida:**\n{lesson['description']}\n\n"
        f"💡 Kerakli amalni tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=get_lesson_detail_keyboard(lesson_id), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("hw_rules:"))
async def show_lesson_rules(callback: CallbackQuery):
    """Show detailed grammar rules for lesson."""
    lesson_id = int(callback.data.split(":")[1])
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        return

    text = (
        f"📖 **{lesson['title']} - Grammatika Qoidalari**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{lesson['grammar_rules']}\n\n"
        f"Endi bilimlaringizni test va yozma mashq orqali mustahkamlang!"
    )
    back_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Darsga qaytish", callback_data=f"lesson_select:{lesson_id}")]
    ])
    await callback.message.edit_text(text, reply_markup=back_btn, parse_mode="Markdown")
    await callback.answer()

# --- Multiple Choice Quiz Flow ---

@router.callback_query(F.data.startswith("hw_quiz:"))
async def start_homework_quiz(callback: CallbackQuery, state: FSMContext):
    """Start quiz for chosen lesson."""
    lesson_id = int(callback.data.split(":")[1])
    lesson = get_lesson_by_id(lesson_id)
    if not lesson or not lesson.get("quiz"):
        await callback.answer("Ushbu dars uchun test mavjud emas.", show_alert=True)
        return

    questions = lesson["quiz"]
    await state.set_state(HomeworkStates.taking_quiz)
    await state.update_data(
        lesson_id=lesson_id,
        questions=questions,
        current_index=0,
        score=0
    )

    q = questions[0]
    text = (
        f"📝 **{lesson['title']} — Test (1/{len(questions)})**\n\n"
        f"❓ **{q['question']}**"
    )
    markup = get_quiz_options_keyboard(q["options"], 0, len(questions))
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("ans:"), HomeworkStates.taking_quiz)
async def process_hw_quiz_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User):
    """Process quiz answer for homework lesson."""
    selected_idx = int(callback.data.split(":")[1])
    data = await state.get_data()
    questions = data["questions"]
    curr_idx = data["current_index"]
    score = data["score"]
    lesson_id = data["lesson_id"]

    curr_q = questions[curr_idx]
    is_correct = (selected_idx == curr_q["correct"])
    new_score = score + (1 if is_correct else 0)

    feedback_header = "✅ **To'g'ri!**" if is_correct else "❌ **Noto'g'ri!**"
    feedback_text = (
        f"{feedback_header}\n\n"
        f"📌 **Savol:** {curr_q['question']}\n"
        f"👉 **To'g'ri javob:** `{curr_q['options'][curr_q['correct']]}`\n"
        f"💡 **Izoh:** {curr_q['explanation']}"
    )

    next_idx = curr_idx + 1
    if next_idx < len(questions):
        await state.update_data(current_index=next_idx, score=new_score)
        next_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Keyingi savol ➡️", callback_data="hw_quiz_next")]
        ])
        await callback.message.edit_text(feedback_text, reply_markup=next_btn, parse_mode="Markdown")
    else:
        # Quiz completed
        pct = round((new_score / len(questions)) * 100, 1)
        if user:
            await save_homework_submission(
                session=session,
                user_id=user.id,
                lesson_id=lesson_id,
                submission_type="quiz",
                content=f"Quiz completed. Score: {new_score}/{len(questions)}",
                score=new_score,
                max_score=len(questions),
                feedback=f"Avtomatik test natijasi: {pct}%",
                status="completed"
            )
            await increment_user_stats(session, user.id, homeworks=1, score_points=new_score * 15)

        await state.clear()
        congrats_text = (
            f"🎉 **Dars testi muvaffaqiyatli yakunlandi!**\n\n"
            f"🎯 **Natijangiz:** `{new_score} / {len(questions)}` ({pct}%)\n"
            f"⭐️ Ballar profilingizga qo'shildi!\n\n"
            f"Endi yozma vazifani (writing) topshirishingiz mumkin."
        )
        back_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Yozma vazifaga o'tish", callback_data=f"hw_writing:{lesson_id}")],
            [InlineKeyboardButton(text="📚 Darslar ro'yxatiga qaytish", callback_data="goto_lessons")]
        ])
        await callback.message.edit_text(congrats_text, reply_markup=back_btn, parse_mode="Markdown")

    await callback.answer()

@router.callback_query(F.data == "hw_quiz_next", HomeworkStates.taking_quiz)
async def next_hw_quiz_question(callback: CallbackQuery, state: FSMContext):
    """Advance to next quiz question."""
    data = await state.get_data()
    questions = data["questions"]
    curr_idx = data["current_index"]
    lesson_id = data["lesson_id"]
    lesson = get_lesson_by_id(lesson_id)

    q = questions[curr_idx]
    text = (
        f"📝 **{lesson['title']} — Test ({curr_idx+1}/{len(questions)})**\n\n"
        f"❓ **{q['question']}**"
    )
    markup = get_quiz_options_keyboard(q["options"], curr_idx, len(questions))
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

# --- Open-ended Writing Homework Flow ---

@router.callback_query(F.data.startswith("hw_writing:"))
async def start_writing_task(callback: CallbackQuery, state: FSMContext):
    """Initiate open-ended writing submission."""
    lesson_id = int(callback.data.split(":")[1])
    lesson = get_lesson_by_id(lesson_id)
    if not lesson or not lesson.get("writing_task"):
        await callback.answer("Ushbu dars uchun yozma vazifa mavjud emas.", show_alert=True)
        return

    task = lesson["writing_task"]
    await state.set_state(HomeworkStates.waiting_text_submission)
    await state.update_data(lesson_id=lesson_id, task=task)

    text = (
        f"✍️ **Yozma Vazifa (Writing Task)**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 **Vazifa sharti:**\n{task['prompt']}\n\n"
        f"📏 **Minimal hajm:** {task['min_words']} ta so'z\n"
        f"💡 **Tavsiya etiladigan so'zlar:** {', '.join(task['required_keywords'])}\n\n"
        f"📝 Javobingizni quyida ingliz tilida xabar sifatida yozib yuboring:"
    )
    cancel_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"lesson_select:{lesson_id}")]
    ])
    await callback.message.edit_text(text, reply_markup=cancel_btn, parse_mode="Markdown")
    await callback.answer()

@router.message(HomeworkStates.waiting_text_submission)
async def evaluate_writing_submission(message: Message, state: FSMContext, session: AsyncSession, user: User):
    """Evaluates student's open-ended writing response and gives instant feedback."""
    submission_text = message.text.strip()
    data = await state.get_data()
    lesson_id = data.get("lesson_id")
    task = data.get("task")
    lesson = get_lesson_by_id(lesson_id)

    words = submission_text.split()
    word_count = len(words)
    min_words = task.get("min_words", 15)

    if word_count < 5:
        await message.answer(
            f"⚠️ Siz yozgan matn juda qisqa ({word_count} ta so'z). "
            f"Iltimos, vazifa shartiga binoan kamida {min_words} ta so'zdan iborat matn yozing."
        )
        return

    # Check keyword usage
    keywords = task.get("required_keywords", [])
    used_keywords = [kw for kw in keywords if kw.lower() in submission_text.lower()]
    keyword_coverage = len(used_keywords) / len(keywords) if keywords else 1.0

    # Auto-score calculation
    base_score = 60
    if word_count >= min_words:
        base_score += 20
    else:
        base_score += int((word_count / min_words) * 20)

    base_score += int(keyword_coverage * 20)
    final_score = min(100, base_score)

    feedback_msg = (
        f"📝 **Matn hajmi:** {word_count} ta so'z (Talab: {min_words}+)\n"
        f"🔑 **Mavzuga oid so'zlar:** {len(used_keywords)}/{len(keywords)} ta ishlatildi ({', '.join(used_keywords) if used_keywords else 'umumiy'})\n"
        f"⭐️ **Baho:** {final_score} / 100 ball\n\n"
        f"💡 **Namunaviy to'g'ri javob (Model Answer):**\n_{task['sample_answer']}_\n\n"
        f"✅ Vazifangiz qabul qilindi va bazaga saqlandi!"
    )

    if user:
        await save_homework_submission(
            session=session,
            user_id=user.id,
            lesson_id=lesson_id,
            submission_type="writing",
            content=submission_text,
            score=final_score,
            max_score=100,
            feedback=feedback_msg,
            status="completed"
        )
        await increment_user_stats(session, user.id, homeworks=1, score_points=25)

    await state.clear()

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Boshqa darslarga o'tish", callback_data="goto_lessons")],
        [InlineKeyboardButton(text="📊 Mening Profilim", callback_data="goto_profile")]
    ])

    await message.answer(
        f"🎉 **Ajoyib! Yozma vazifangiz tekshirildi:**\n\n{feedback_msg}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
