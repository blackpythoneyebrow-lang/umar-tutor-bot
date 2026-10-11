"""
Modern inline keyboards for Umar Tutor Bot.
Features styled callbacks for tests, lessons, speaking, vocabulary, and profile.
"""
from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Placement Test Keyboards ---

def get_test_choice_keyboard() -> InlineKeyboardMarkup:
    """Select between full comprehensive placement test or specific CEFR level test."""
    buttons = [
        [
            InlineKeyboardButton(
                text="⚡️ Keng qamrovli Placement Test (A1-C2)",
                callback_data="test_mode:full"
            )
        ],
        [
            InlineKeyboardButton(text="🟢 A1 - Beginner", callback_data="test_mode:A1"),
            InlineKeyboardButton(text="🟢 A2 - Elementary", callback_data="test_mode:A2")
        ],
        [
            InlineKeyboardButton(text="🟡 B1 - Intermediate", callback_data="test_mode:B1"),
            InlineKeyboardButton(text="🟡 B2 - Upper-Int", callback_data="test_mode:B2")
        ],
        [
            InlineKeyboardButton(text="🔴 C1 - Advanced", callback_data="test_mode:C1"),
            InlineKeyboardButton(text="🔴 C2 - Proficiency", callback_data="test_mode:C2")
        ],
        [
            InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="test_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quiz_options_keyboard(options: List[str], current_index: int, total: int) -> InlineKeyboardMarkup:
    """Generate 4 choice buttons for quiz question."""
    labels = ["A", "B", "C", "D"]
    keyboard = []
    
    for idx, opt in enumerate(options):
        label = labels[idx] if idx < len(labels) else f"#{idx+1}"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{label}) {opt}",
                callback_data=f"ans:{idx}"
            )
        ])
        
    keyboard.append([
        InlineKeyboardButton(
            text=f"❌ Testni to'xtatish ({current_index+1}/{total})",
            callback_data="test_quit"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_test_finished_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown after placement test completion."""
    buttons = [
        [
            InlineKeyboardButton(text="📚 Darslarga o'tish", callback_data="goto_lessons"),
            InlineKeyboardButton(text="🎙 Speaking qilish", callback_data="goto_speaking")
        ],
        [
            InlineKeyboardButton(text="📊 Profilimni ko'rish", callback_data="goto_profile"),
            InlineKeyboardButton(text="🔄 Qayta test topshirish", callback_data="test_restart")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Homework Keyboards ---

def get_lessons_list_keyboard(lessons: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Generate list of available lessons."""
    buttons = []
    for lesson in lessons:
        buttons.append([
            InlineKeyboardButton(
                text=f"📖 {lesson['title']} ({lesson['level']})",
                callback_data=f"lesson_select:{lesson['id']}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Menyuga qaytish", callback_data="menu_home")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lesson_detail_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    """Actions available for a selected lesson."""
    buttons = [
        [
            InlineKeyboardButton(text="📝 Test topshirish (Quiz)", callback_data=f"hw_quiz:{lesson_id}"),
            InlineKeyboardButton(text="✍️ Yozma vazifa (Writing)", callback_data=f"hw_writing:{lesson_id}")
        ],
        [
            InlineKeyboardButton(text="📖 Grammatika qoidalari", callback_data=f"hw_rules:{lesson_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Darslar ro'yxatiga qaytish", callback_data="goto_lessons")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Speaking Hub Keyboards ---

def get_speaking_hub_keyboard() -> InlineKeyboardMarkup:
    """Hub menu for speaking practice."""
    buttons = [
        [
            InlineKeyboardButton(text="🗣 Shadowing (O'qib takrorlash)", callback_data="speak_mode:shadowing")
        ],
        [
            InlineKeyboardButton(text="🎙 Erkin mavzular (Free Speech)", callback_data="speak_mode:free")
        ],
        [
            InlineKeyboardButton(text="🌐 Tavsiya etilgan ilovalar & saytlar", callback_data="speak_mode:resources")
        ],
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_home")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_shadowing_list_keyboard(prompts: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """List of shadow-reading prompts."""
    buttons = []
    for p in prompts:
        buttons.append([
            InlineKeyboardButton(
                text=f"🔹 {p['title']} [{p['level']}]",
                callback_data=f"shadow_sel:{p['id']}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="goto_speaking")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_free_speech_list_keyboard(topics: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """List of free speech topics."""
    buttons = []
    for t in topics:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎯 {t['topic']}",
                callback_data=f"free_sel:{t['id']}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="goto_speaking")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_speaking_ready_keyboard(prompt_id: str) -> InlineKeyboardMarkup:
    """Prompt view with ready button."""
    buttons = [
        [
            InlineKeyboardButton(text="🎙 Ovoz yuborishga tayyorman", callback_data=f"voice_ready:{prompt_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Boshqa mavzu tanlash", callback_data="goto_speaking")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Vocabulary Keyboards ---

def get_vocabulary_keyboard(word_id: int) -> InlineKeyboardMarkup:
    """Word of the day actions."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Yodladim", callback_data=f"vocab_learned:{word_id}"),
            InlineKeyboardButton(text="➡️ Keyingi so'z", callback_data="vocab_next")
        ],
        [
            InlineKeyboardButton(text="🔀 Tasodifiy so'z", callback_data="vocab_random"),
            InlineKeyboardButton(text="🔙 Menyuga qaytish", callback_data="menu_home")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Profile Keyboards ---

def get_profile_actions_keyboard() -> InlineKeyboardMarkup:
    """Actions within user profile."""
    buttons = [
        [
            InlineKeyboardButton(text="🎯 Darajamni yangilash (Test)", callback_data="goto_test"),
            InlineKeyboardButton(text="📋 Shaxsiy O'quv Rejasi", callback_data="goto_plan")
        ],
        [
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="refresh_profile"),
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="menu_home")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
