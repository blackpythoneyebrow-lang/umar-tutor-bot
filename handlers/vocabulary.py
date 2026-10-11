"""
Vocabulary Builder handler for Umar Tutor Bot.
Features Word of the Day cards, phonetics (IPA), examples, and learning progress tracking.
"""
import json
import os
import random
from typing import List, Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.crud import mark_word_learned, get_user_learned_count, increment_user_stats
from keyboards.inline_keyboards import get_vocabulary_keyboard

router = Router(name="vocabulary")

VOCAB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vocabulary.json")

def load_vocabulary() -> List[Dict[str, Any]]:
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

WORDS = load_vocabulary()

def get_word_card_text(word_data: Dict[str, Any], learned_count: int, total_words: int) -> str:
    """Formats word card matching the mobile UI layout."""
    progress_pct = int((learned_count / total_words) * 100) if total_words > 0 else 0
    filled = min(10, int(progress_pct / 10))
    bar = "🟦" * filled + "⬜️" * (10 - filled)

    return (
        f"📖 **Kunlik Lug'at (Vocabulary Builder)**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔤 **{word_data['word']}** `[{word_data['part_of_speech']}]` `[{word_data['level']}]`\n"
        f"🗣 **Talaffuzi (IPA):** `{word_data['phonetics']}`\n\n"
        f"🇺🇿 **Tarjimasi:** {word_data['translation_uz']}\n"
        f"💬 **Ta'rifi:** _{word_data['definition']}_\n\n"
        f"📝 **Misol:**\n"
        f"• *\"{word_data['example']}\"*\n"
        f"• 🇺🇿 *\"{word_data['example_uz']}\"*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **O'zlashtirish:** {learned_count}/{total_words} so'z ({progress_pct}%)\n"
        f"{bar}"
    )

@router.message(F.text == "📖 Kunlik Lug'at")
async def show_daily_word(message: Message, session: AsyncSession, user: User):
    """Entry point for Vocabulary Builder."""
    total_words = len(WORDS)
    learned_count = await get_user_learned_count(session, user.id) if user else 0

    word = WORDS[0]
    text = get_word_card_text(word, learned_count, total_words)
    await message.answer(text, reply_markup=get_vocabulary_keyboard(word["id"]), parse_mode="Markdown")

@router.callback_query(F.data.startswith("vocab_learned:"))
async def on_word_learned(callback: CallbackQuery, session: AsyncSession, user: User):
    """Mark current word as learned and advance."""
    word_id = int(callback.data.split(":")[1])
    is_new = await mark_word_learned(session, user.id, word_id) if user else False

    if is_new and user:
        await increment_user_stats(session, user.id, words=1, score_points=10)
        await callback.answer("🎉 So'z yodlanganlar ro'yxatiga qo'shildi! (+10 ball)", show_alert=False)
    else:
        await callback.answer("Ushbu so'z allaqachon yodlangan.", show_alert=False)

    # Next word
    await advance_to_next_word(callback, session, user, current_id=word_id)

@router.callback_query(F.data == "vocab_next")
async def on_vocab_next(callback: CallbackQuery, session: AsyncSession, user: User):
    """Navigate to next vocabulary card."""
    await advance_to_next_word(callback, session, user)
    await callback.answer()

@router.callback_query(F.data == "vocab_random")
async def on_vocab_random(callback: CallbackQuery, session: AsyncSession, user: User):
    """Pick a random vocabulary card."""
    word = random.choice(WORDS)
    total_words = len(WORDS)
    learned_count = await get_user_learned_count(session, user.id) if user else 0

    text = get_word_card_text(word, learned_count, total_words)
    await callback.message.edit_text(text, reply_markup=get_vocabulary_keyboard(word["id"]), parse_mode="Markdown")
    await callback.answer()

async def advance_to_next_word(callback: CallbackQuery, session: AsyncSession, user: User, current_id: int = None):
    """Helper to display next word sequentially."""
    total_words = len(WORDS)
    learned_count = await get_user_learned_count(session, user.id) if user else 0

    next_idx = 0
    if current_id:
        for idx, w in enumerate(WORDS):
            if w["id"] == current_id:
                next_idx = (idx + 1) % total_words
                break

    word = WORDS[next_idx]
    text = get_word_card_text(word, learned_count, total_words)
    await callback.message.edit_text(text, reply_markup=get_vocabulary_keyboard(word["id"]), parse_mode="Markdown")
