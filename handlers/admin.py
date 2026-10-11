"""
Admin dashboard and student management handler for Umar Tutor Bot.
Provides system metrics, student directory with CEFR filtering, and announcement broadcast.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.models import User
from database.crud import (
    get_admin_dashboard_stats,
    get_students_list,
    get_all_user_ids,
)
from utils.states import AdminStates
from keyboards.admin_keyboards import (
    get_admin_main_keyboard,
    get_admin_students_filter_keyboard,
    get_admin_broadcast_confirm_keyboard,
)

router = Router(name="admin")

def is_admin_user(user: User, tg_id: int) -> bool:
    """Check if current user has admin privileges."""
    if tg_id in settings.ADMIN_IDS:
        return True
    if user and user.is_admin:
        return True
    return False

@router.message(Command("admin"))
@router.message(F.text == "👑 Admin Panel")
async def show_admin_panel(message: Message, state: FSMContext, user: User):
    """Admin dashboard entrance."""
    await state.clear()
    if not is_admin_user(user, message.from_user.id):
        await message.answer("⛔️ Kechirasiz, sizda admin huquqlari mavjud emas.")
        return

    text = (
        "👑 **Umar Tutor — Boshqaruv Paneli (Admin Dashboard)**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Xush kelibsiz, Administrator! Bu yerdan bot statistikasi, talabalar ro'yxati "
        "va barchaga xabar yuborish (broadcast) funksiyalaridan foydalanishingiz mumkin."
    )
    await message.answer(text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_home")
async def callback_admin_home(callback: CallbackQuery, state: FSMContext, user: User):
    """Return to admin panel main screen."""
    await state.clear()
    if not is_admin_user(user, callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    text = (
        "👑 **Umar Tutor — Boshqaruv Paneli (Admin Dashboard)**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Kerakli bo'limni tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def show_admin_statistics(callback: CallbackQuery, session: AsyncSession, user: User):
    """Display comprehensive bot usage statistics."""
    if not is_admin_user(user, callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    stats = await get_admin_dashboard_stats(session)

    text = (
        "📊 **Umar Tutor — Batafsil Statistika**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **Jami ro'yxatdan o'tgan o'quvchilar:** `{stats['total_users']}` nafar\n"
        f"⚡️ **Bugun faol bo'lganlar:** `{stats['active_today']}` nafar\n\n"
        f"🎯 **Topshirilgan daraja testlari:** `{stats['total_tests']}` ta\n"
        f"📈 **O'rtacha test natijasi:** `{stats['avg_test_score']}%`\n\n"
        f"📚 **Bajarilgan dars vazifalari:** `{stats['total_homeworks']}` ta\n"
        f"🎙 **Yuborilgan ovozli (speaking) xabarlar:** `{stats['total_speaking']}` ta\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "admin_students")
async def show_students_filter(callback: CallbackQuery, user: User):
    """Show level filter for students list."""
    if not is_admin_user(user, callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    text = (
        "👥 **Talabalar Ro'yxati**\n\n"
        "Qaysi darajadagi talabalarni ko'rmoqchisiz? Quyidagi filtrlardan birini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_students_filter_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("adm_filter:"))
async def list_students_by_level(callback: CallbackQuery, session: AsyncSession, user: User):
    """Display student list by selected filter."""
    if not is_admin_user(user, callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    lvl_filter = callback.data.split(":")[1]
    students = await get_students_list(session, level_filter=lvl_filter, limit=25)

    if not students:
        text = f"👥 **Talabalar Ro'yxati ({lvl_filter}):**\n\nUshbu filtr bo'yicha hali o'quvchilar mavjud emas."
    else:
        lines = [f"👥 **Talabalar Ro'yxati [{lvl_filter}] ({len(students)} nafar):**\n"]
        for idx, s in enumerate(students, 1):
            uname = f"@{s.username}" if s.username else "username yo'q"
            lines.append(
                f"{idx}. **{s.full_name}** ({uname})\n"
                f"   🎖 Daraja: `{s.level}` | 🔥 Streak: `{s.streak_days}` kun | ⭐️ Ball: `{s.total_score}`"
            )
        text = "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=get_admin_students_filter_keyboard(), parse_mode="Markdown")
    await callback.answer()

# --- Broadcast Announcement Flow ---

@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext, user: User):
    """Initiate broadcast creation."""
    if not is_admin_user(user, callback.from_user.id):
        await callback.answer("Ruxsat berilmagan.", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_broadcast_text)
    text = (
        "📢 **Barcha o'quvchilarga xabar yuborish (Broadcast)**\n\n"
        "Yubormoqchi bo'lgan xabaringiz matnini quyida yozib jo'nating. "
        "Matnda Markdown formatlashdan foydalanishingiz mumkin.\n\n"
        "Xabar avval sizga tekshirib ko'rish uchun ko'rsatiladi."
    )
    await callback.message.edit_text(text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.message(AdminStates.waiting_broadcast_text, F.text)
async def preview_broadcast_message(message: Message, state: FSMContext):
    """Show preview of broadcast text and ask for confirmation."""
    broadcast_content = message.text
    await state.update_data(broadcast_text=broadcast_content)
    await state.set_state(AdminStates.confirm_broadcast)

    preview_text = (
        "📢 **Xabar Ko'rinishi (Preview):**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{broadcast_content}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Ushbu xabar barcha ro'yxatdan o'tgan o'quvchilarga yuborilsinmi?"
    )
    await message.answer(preview_text, reply_markup=get_admin_broadcast_confirm_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "broadcast_confirm", AdminStates.confirm_broadcast)
async def execute_broadcast(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Send broadcast to all registered users."""
    data = await state.get_data()
    text = data.get("broadcast_text")
    await state.clear()

    user_ids = await get_all_user_ids(session)
    sent_count = 0
    fail_count = 0

    status_msg = await callback.message.edit_text(
        f"⏳ Xabar yuborilmoqda... (0/{len(user_ids)})",
        parse_mode="Markdown"
    )

    for uid in user_ids:
        try:
            await callback.bot.send_message(chat_id=uid, text=text, parse_mode="Markdown")
            sent_count += 1
        except Exception:
            fail_count += 1

    report_text = (
        "✅ **Xabar tarqatish yakunlandi!**\n\n"
        f"📬 Muvaffaqiyatli yetkazildi: `{sent_count}` ta\n"
        f"❌ Yetkazilmadi (bloklangan/xatolik): `{fail_count}` ta"
    )
    await status_msg.edit_text(report_text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "broadcast_cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Cancel broadcast."""
    await state.clear()
    await callback.message.edit_text("❌ Xabar yuborish bekor qilindi.", reply_markup=get_admin_main_keyboard())
    await callback.answer()
