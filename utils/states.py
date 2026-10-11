"""
Aiogram FSM States for Umar Tutor bot.
"""
from aiogram.fsm.state import State, StatesGroup

class PlacementTestStates(StatesGroup):
    choosing_mode = State()      # Choose between Diagnostic test or specific CEFR level test
    taking_test = State()        # In progress answering questions

class HomeworkStates(StatesGroup):
    choosing_lesson = State()
    taking_quiz = State()
    waiting_text_submission = State()

class SpeakingStates(StatesGroup):
    choosing_prompt = State()
    waiting_voice = State()

class GrammarStates(StatesGroup):
    waiting_sentence = State()

class AdminStates(StatesGroup):
    panel = State()
    waiting_broadcast_text = State()
    confirm_broadcast = State()
    student_list_filter = State()
