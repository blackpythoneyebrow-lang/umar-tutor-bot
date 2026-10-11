"""
Automated unit and integration tests for Umar Tutor Bot components.
Verifies JSON dataset integrity, grammar checker logic, speaking evaluator, and database schemas.
"""
import asyncio
import json
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.grammar_checker import analyze_grammar
from services.speaking_evaluator import evaluate_voice_submission
from database.base import Base, get_engine
from database.models import User, PlacementResult, HomeworkSubmission, SpeakingSubmission, VocabularyProgress
from database.crud import (
    get_or_create_user,
    update_user_level,
    save_placement_result,
    save_homework_submission,
    save_speaking_submission,
    mark_word_learned,
    get_user_learned_count,
    get_admin_dashboard_stats
)
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

def test_json_datasets():
    print("Testing JSON datasets...")
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # 1. Placement Test
    pt_path = os.path.join(base_dir, "data", "placement_test.json")
    with open(pt_path, "r", encoding="utf-8") as f:
        pt_data = json.load(f)
    for lvl in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        assert lvl in pt_data, f"Level {lvl} missing in placement_test.json"
        questions = pt_data[lvl]
        assert len(questions) == 10, f"Level {lvl} should have 10 questions, got {len(questions)}"
        for q in questions:
            assert "id" in q and "question" in q and "options" in q and "correct" in q and "explanation" in q
            assert len(q["options"]) == 4
            assert 0 <= q["correct"] <= 3

    # 2. Vocabulary
    v_path = os.path.join(base_dir, "data", "vocabulary.json")
    with open(v_path, "r", encoding="utf-8") as f:
        v_data = json.load(f)
    assert len(v_data) >= 10, "Vocabulary dataset should have at least 10 items"
    for item in v_data:
        assert "word" in item and "phonetics" in item and "translation_uz" in item

    # 3. Homework
    hw_path = os.path.join(base_dir, "data", "homework.json")
    with open(hw_path, "r", encoding="utf-8") as f:
        hw_data = json.load(f)
    assert len(hw_data) >= 3, "Homework should have at least 3 lessons"
    for lesson in hw_data:
        assert "title" in lesson and "quiz" in lesson and "writing_task" in lesson

    # 4. Speaking Topics
    sp_path = os.path.join(base_dir, "data", "speaking_topics.json")
    with open(sp_path, "r", encoding="utf-8") as f:
        sp_data = json.load(f)
    assert len(sp_data.get("shadowing_prompts", [])) >= 3
    assert len(sp_data.get("free_speech_prompts", [])) >= 3
    assert len(sp_data.get("curated_resources", [])) >= 3

    print(" [PASS] All JSON datasets are valid and complete.")

def test_grammar_service():
    print("Testing Grammar Checker Service...")
    # Error 1: "I am go to the school yesterday"
    r1 = analyze_grammar("I am go to the school yesterday")
    assert r1["has_error"] is True
    assert "went" in r1["corrected"].lower()
    assert len(r1["issues"]) > 0

    # Error 2: "She don't work here"
    r2 = analyze_grammar("She don't work here")
    assert r2["has_error"] is True
    assert "doesn't" in r2["corrected"].lower()

    # Error 3: "I am agree with you"
    r3 = analyze_grammar("I am agree with you")
    assert r3["has_error"] is True
    assert "i agree" in r3["corrected"].lower()

    # Correct sentence
    r4 = analyze_grammar("I went to the library yesterday and read a book.")
    assert r4["has_error"] is False

    print(" [PASS] Grammar service correctly identifies errors and generates pedagogical corrections.")

def test_speaking_service():
    print("Testing Speaking Evaluator Service...")
    # Too short
    short_res = evaluate_voice_submission(2, "Test Prompt")
    assert short_res["success"] is False

    # Valid voice
    valid_res = evaluate_voice_submission(20, "Test Prompt")
    assert valid_res["success"] is True
    assert valid_res["score"] >= 80
    assert len(valid_res["metrics"]) > 0
    assert "tip" in valid_res

    print(" [PASS] Speaking service correctly evaluates audio length and metrics.")

async def test_database_lifecycle():
    print("Testing Database Models and Async CRUD...")
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = get_engine(test_db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        # Create user
        user = await get_or_create_user(
            session=session,
            telegram_id=999999,
            full_name="Test Student",
            username="test_student",
            admin_ids=[123456]
        )
        assert user.telegram_id == 999999
        assert user.level == "Aniqlanmagan"

        # Update level
        await update_user_level(session, user.telegram_id, "B1")

        # Save placement result
        pr = await save_placement_result(
            session=session,
            user_id=user.id,
            target_level="full",
            score=8,
            total_questions=10,
            assigned_level="B1"
        )
        assert pr.assigned_level == "B1"
        assert pr.percentage == 80.0

        # Save homework quiz
        hw = await save_homework_submission(
            session=session,
            user_id=user.id,
            lesson_id=1,
            submission_type="quiz",
            content="Score 3/3",
            score=3,
            max_score=3,
            feedback="Auto-graded 100%"
        )
        assert hw.score == 3

        # Save speaking submission
        sp = await save_speaking_submission(
            session=session,
            user_id=user.id,
            prompt_id="shadow_1",
            prompt_text="Introduce Yourself",
            file_id="voice_file_123",
            duration=15,
            score=90,
            feedback="Good pronunciation"
        )
        assert sp.duration == 15

        # Learn word
        learned = await mark_word_learned(session, user.id, 1)
        assert learned is True
        count = await get_user_learned_count(session, user.id)
        assert count == 1

        # Check admin stats
        stats = await get_admin_dashboard_stats(session)
        assert stats["total_users"] == 1
        assert stats["total_tests"] == 1
        assert stats["total_homeworks"] == 1
        assert stats["total_speaking"] == 1

    print(" [PASS] Database lifecycle and CRUD operations validated successfully.")

async def run_all_tests():
    test_json_datasets()
    test_grammar_service()
    test_speaking_service()
    await test_database_lifecycle()
    print("\n[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
