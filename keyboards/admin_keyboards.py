"""
Admin keyboards for Umar Tutor Bot.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin dashboard navigation."""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Umumiy Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 Talabalar Ro'yxati", callback_data="admin_students")
        ],
        [
            InlineKeyboardButton(text="📢 Barchaga Xabar Yuborish (Broadcast)", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="🔙 Foydalanuvchi menyusiga qaytish", callback_data="menu_home")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_students_filter_keyboard() -> InlineKeyboardMarkup:
    """Filter students by English level."""
    buttons = [
        [
            InlineKeyboardButton(text="Barchasi", callback_data="adm_filter:Barchasi"),
            InlineKeyboardButton(text="Aniqlanmagan", callback_data="adm_filter:Aniqlanmagan")
        ],
        [
            InlineKeyboardButton(text="A1", callback_data="adm_filter:A1"),
            InlineKeyboardButton(text="A2", callback_data="adm_filter:A2"),
            InlineKeyboardButton(text="B1", callback_data="adm_filter:B1")
        ],
        [
            InlineKeyboardButton(text="B2", callback_data="adm_filter:B2"),
            InlineKeyboardButton(text="C1", callback_data="adm_filter:C1"),
            InlineKeyboardButton(text="C2", callback_data="adm_filter:C2")
        ],
        [
            InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_home")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Confirmation before sending broadcast."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Ha, barchaga yuborilsin!", callback_data="broadcast_confirm"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
