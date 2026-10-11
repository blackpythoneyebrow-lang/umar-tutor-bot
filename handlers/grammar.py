"""
Grammar Correction Assistant handler for Umar Tutor Bot.
Analyzes sentences sent by users, detects mistakes, shows corrections and pedagogical explanations.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from utils.states import GrammarStates
from services.grammar_checker import analyze_grammar

router = Router(name="grammar")

@router.message(F.text == "✍️ Grammar Helper")
async def start_grammar_checker(message: Message, state: FSMContext):
    """Entry point for Grammar Helper."""
    await state.set_state(GrammarStates.waiting_sentence)
    cancel_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="menu_home")]
    ])
    text = (
        "✍️ **Grammar Correction Assistant (Grammatika Yordamchisi)**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Istalgan inglizcha gap yoki jumlani yozib yuboring!\n\n"
        "Misol uchun:\n"
        "• _I am go to the school yesterday._\n"
        "• _She don't like playing tennis._\n"
        "• _I have 20 years old._\n\n"
        "Men xatolarni topib, to'g'ri variantini va qoidasini o'zbek tilida tushuntirib beraman! 🔍"
    )
    await message.answer(text, reply_markup=cancel_btn, parse_mode="Markdown")

@router.message(GrammarStates.waiting_sentence, F.text)
async def process_grammar_input(message: Message, state: FSMContext):
    """Processes sentence and replies with correction card."""
    user_sentence = message.text.strip()

    if user_sentence.startswith("/"):
        await state.clear()
        return

    result = analyze_grammar(user_sentence)

    actions_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Yana gap tekshirish", callback_data="grammar_again")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="menu_home")]
    ])

    if result.get("has_error"):
        issues_text = ""
        for idx, issue in enumerate(result.get("issues", []), 1):
            issues_text += (
                f"🔹 **{issue['title']}**\n"
                f"💡 {issue['explanation']}\n"
                f"📌 *Misol:* `{issue['tip']}`\n\n"
            )

        card = (
            f"✍️ **Grammar Correction Natijasi** 🛠\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ **Siz yozgan variant:**\n`{result['original']}`\n\n"
            f"✅ **To'g'rilangan variant:**\n`{result['corrected']}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📖 **Xatolar tahlili va qoidalar:**\n\n"
            f"{issues_text}"
            f"💡 *Mashq qilishda davom eting!*"
        )
    else:
        card = (
            f"✍️ **Grammar Correction Natijasi** ✨\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **Jumla:** `{result['original']}`\n\n"
            f"🎉 {result['message']}"
        )

    await message.answer(card, reply_markup=actions_markup, parse_mode="Markdown")

@router.callback_query(F.data == "grammar_again")
async def on_grammar_again(callback: CallbackQuery, state: FSMContext):
    """Prompt for another sentence."""
    await state.set_state(GrammarStates.waiting_sentence)
    await callback.message.answer(
        "✍️ Yangi inglizcha gapni yozib yuboring:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="menu_home")]
        ])
    )
    await callback.answer()
