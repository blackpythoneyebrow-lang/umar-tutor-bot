"""
Database CRUD operations for Umar Tutor Bot.
Handles Users, Roles, Student Access Codes, Skill Metrics, Error Analytics,
Course Materials (CMS), Live Meetings, and Teacher Marking.
"""
import json
import random
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, func, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    User,
    PlacementResult,
    HomeworkSubmission,
    SpeakingSubmission,
    VocabularyProgress,
    MistakeLog,
    CourseMaterial,
    LiveMeeting,
    SubmissionReview,
)

DEFAULT_SKILLS = {
    "vocab": 75,
    "grammar": 70,
    "speaking": 65,
    "listening": 70,
    "reading": 68,
    "quiz": 75
}

DEFAULT_WEAK_POINTS = [
    "Past Simple va Present Perfect zamonlari farqi",
    "Speakingda bog'lovchi so'zlar (however, therefore) ishlatish",
    "B2 darajadagi akademik so'zlar boyligini oshirish"
]

def generate_student_code(telegram_id: int) -> str:
    """Generate friendly unique student access PIN e.g. STU-4921"""
    suffix = str(abs(telegram_id))[-4:]
    return f"STU-{suffix}"

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    full_name: str,
    username: Optional[str] = None,
    admin_ids: Optional[List[int]] = None
) -> User:
    """Retrieve existing user or create a new user record with access code and initial skills."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    is_admin = bool(admin_ids and telegram_id in admin_ids)

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            role="admin" if is_admin else "student",
            access_code=generate_student_code(telegram_id),
            level="A1",
            streak_days=1,
            last_active_date=datetime.utcnow(),
            skill_percentages=json.dumps(DEFAULT_SKILLS),
            weak_points=json.dumps(DEFAULT_WEAK_POINTS),
            is_admin=is_admin
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        updated = False
        if user.full_name != full_name:
            user.full_name = full_name
            updated = True
        if user.username != username:
            user.username = username
            updated = True
        if is_admin and not user.is_admin:
            user.is_admin = True
            if user.role != "teacher" and user.role != "admin":
                user.role = "admin"
            updated = True
        if not user.access_code:
            user.access_code = generate_student_code(telegram_id)
            updated = True
        if not user.skill_percentages:
            user.skill_percentages = json.dumps(DEFAULT_SKILLS)
            updated = True
        if not user.weak_points:
            user.weak_points = json.dumps(DEFAULT_WEAK_POINTS)
            updated = True
            
        if updated:
            await session.commit()
            await session.refresh(user)

    return user

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Find user by Telegram ID."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_access_code(session: AsyncSession, code: str) -> Optional[User]:
    """Find user by student access code or telegram ID."""
    clean_code = code.strip().upper()
    stmt = select(User).where(func.upper(User.access_code) == clean_code)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()
    if not user and clean_code.isdigit():
        stmt2 = select(User).where(User.telegram_id == int(clean_code))
        res2 = await session.execute(stmt2)
        user = res2.scalar_one_or_none()
    return user

async def create_student_account(
    session: AsyncSession,
    full_name: str,
    level: str = "Starter",
    custom_code: Optional[str] = None,
    telegram_id: Optional[int] = None
) -> User:
    """Create a new dedicated student account with personal code."""
    code = custom_code.strip().upper() if custom_code and custom_code.strip() else None
    if not code:
        code = f"STU-{random.randint(1000, 9999)}"

    # Ensure unique code
    existing = await get_user_by_access_code(session, code)
    if existing:
        if telegram_id and existing.telegram_id == telegram_id:
            existing.full_name = full_name
            existing.level = level
            await session.commit()
            return existing
        code = f"STU-{random.randint(1000, 9999)}"

    if telegram_id:
        existing_tg = await get_user_by_telegram_id(session, telegram_id)
        if existing_tg:
            existing_tg.full_name = full_name
            existing_tg.level = level
            existing_tg.access_code = code
            await session.commit()
            return existing_tg

    user = User(
        telegram_id=telegram_id or random.randint(100000000, 999999999),
        full_name=full_name,
        role="student",
        access_code=code,
        level=level,
        streak_days=1,
        last_active_date=datetime.utcnow(),
        skill_percentages=json.dumps(DEFAULT_SKILLS),
        weak_points=json.dumps(DEFAULT_WEAK_POINTS),
        is_admin=False
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def update_user_activity_and_streak(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Updates user last active timestamp and streak days."""
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        return None

    now = datetime.utcnow()
    last_active = user.last_active_date or now
    last_date = last_active.date()
    today = now.date()

    if today == last_date + timedelta(days=1):
        user.streak_days = (user.streak_days or 1) + 1
    elif today > last_date + timedelta(days=1):
        user.streak_days = 1

    user.last_active_date = now
    await session.commit()
    await session.refresh(user)
    return user

async def update_user_level(session: AsyncSession, telegram_id: int, new_level: str) -> None:
    """Update assigned English level (Starter, A1, A2, B1, B2, IELTS)."""
    stmt = update(User).where(User.telegram_id == telegram_id).values(
        level=new_level,
        updated_at=datetime.utcnow()
    )
    await session.execute(stmt)
    await session.commit()

async def update_user_role(session: AsyncSession, telegram_id: int, new_role: str) -> None:
    """Update user role (student, teacher, admin)."""
    stmt = update(User).where(User.telegram_id == telegram_id).values(
        role=new_role,
        updated_at=datetime.utcnow()
    )
    await session.execute(stmt)
    await session.commit()

async def update_user_skills(
    session: AsyncSession,
    user_id: int,
    skill_updates: Dict[str, int],
    new_weak_point: Optional[str] = None
) -> Dict[str, Any]:
    """Update student skill percentages and optionally add a weak point."""
    user = await session.get(User, user_id)
    if not user:
        return DEFAULT_SKILLS

    current_skills = DEFAULT_SKILLS.copy()
    if user.skill_percentages:
        try:
            current_skills.update(json.loads(user.skill_percentages))
        except Exception:
            pass

    for skill, val in skill_updates.items():
        if skill in current_skills:
            # Weighted smooth update
            current_skills[skill] = max(10, min(100, int((current_skills[skill] * 0.7) + (val * 0.3))))

    user.skill_percentages = json.dumps(current_skills)

    if new_weak_point:
        current_weak = []
        if user.weak_points:
            try:
                current_weak = json.loads(user.weak_points)
            except Exception:
                pass
        if new_weak_point not in current_weak:
            current_weak.insert(0, new_weak_point)
            current_weak = current_weak[:5]  # Keep top 5
            user.weak_points = json.dumps(current_weak)

    await session.commit()
    return current_skills

# --- Error Logging & Analytics ---

async def log_mistake(
    session: AsyncSession,
    user_id: int,
    category: str,
    level: str,
    question_text: str,
    user_answer: str,
    correct_answer: str,
    explanation: str
) -> MistakeLog:
    """Logs a student mistake for teacher analytics and student recommendation engine."""
    log = MistakeLog(
        user_id=user_id,
        category=category,
        level=level,
        question_text=question_text,
        user_answer=user_answer,
        correct_answer=correct_answer,
        explanation=explanation,
        created_at=datetime.utcnow()
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log

async def get_teacher_error_analytics(session: AsyncSession) -> Dict[str, Any]:
    """Aggregates student mistake patterns for Teacher/Admin Error Analytics."""
    # Group mistakes by category
    stmt_cat = (
        select(MistakeLog.category, func.count(MistakeLog.id))
        .group_by(MistakeLog.category)
        .order_by(desc(func.count(MistakeLog.id)))
    )
    cat_res = await session.execute(stmt_cat)
    by_category = [{"category": row[0], "count": row[1]} for row in cat_res.all()]

    # Group by question text to find most failed questions
    stmt_top = (
        select(MistakeLog.question_text, MistakeLog.correct_answer, MistakeLog.explanation, func.count(MistakeLog.id).label("err_count"))
        .group_by(MistakeLog.question_text, MistakeLog.correct_answer, MistakeLog.explanation)
        .order_by(desc("err_count"))
        .limit(6)
    )
    top_res = await session.execute(stmt_top)
    top_mistakes = [
        {
            "question": row[0],
            "correct_answer": row[1],
            "explanation": row[2],
            "error_count": row[3]
        }
        for row in top_res.all()
    ]

    total_mistakes = sum(item["count"] for item in by_category)

    return {
        "total_mistakes": total_mistakes,
        "by_category": by_category,
        "top_mistakes": top_mistakes
    }

# --- Course Material CMS Operations ---

async def create_course_material(
    session: AsyncSession,
    category: str,
    level: str,
    title: str,
    content_payload: Dict[str, Any],
    created_by: str = "Teacher Umar"
) -> CourseMaterial:
    """Save new material added by teacher in CMS."""
    mat = CourseMaterial(
        category=category,
        level=level,
        title=title,
        content_json=json.dumps(content_payload, ensure_ascii=False),
        created_by=created_by,
        created_at=datetime.utcnow()
    )
    session.add(mat)
    await session.commit()
    await session.refresh(mat)
    return mat

async def get_course_materials(
    session: AsyncSession,
    category: Optional[str] = None,
    level: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve CMS course materials with optional filters."""
    stmt = select(CourseMaterial).order_by(desc(CourseMaterial.created_at))
    if category:
        stmt = stmt.where(CourseMaterial.category == category)
    if level and level != "All" and level != "Barchasi":
        stmt = stmt.where(CourseMaterial.level == level)
        
    res = await session.execute(stmt)
    records = res.scalars().all()
    out = []
    for r in records:
        try:
            payload = json.loads(r.content_json)
        except Exception:
            payload = {}
        out.append({
            "id": r.id,
            "category": r.category,
            "level": r.level,
            "title": r.title,
            "created_by": r.created_by,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "data": payload
        })
    return out

async def delete_course_material(session: AsyncSession, material_id: int) -> bool:
    """Delete a course material."""
    stmt = delete(CourseMaterial).where(CourseMaterial.id == material_id)
    res = await session.execute(stmt)
    await session.commit()
    return res.rowcount > 0

# --- Live Meetings Operations ---

async def create_live_meeting(
    session: AsyncSession,
    title: str,
    level: str,
    datetime_str: str,
    meeting_link: str,
    platform: str = "Telegram"
) -> LiveMeeting:
    """Create a new live online class scheduled by teacher."""
    meeting = LiveMeeting(
        title=title,
        level=level,
        datetime_str=datetime_str,
        meeting_link=meeting_link,
        platform=platform,
        is_active=True,
        created_at=datetime.utcnow()
    )
    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)
    return meeting

async def get_active_live_meetings(session: AsyncSession) -> List[Dict[str, Any]]:
    """Get active live meetings."""
    stmt = select(LiveMeeting).where(LiveMeeting.is_active == True).order_by(desc(LiveMeeting.created_at))
    res = await session.execute(stmt)
    meetings = res.scalars().all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "level": m.level,
            "datetime_str": m.datetime_str,
            "meeting_link": m.meeting_link,
            "platform": m.platform
        }
        for m in meetings
    ]

async def delete_live_meeting(session: AsyncSession, meeting_id: int) -> bool:
    """Remove or close an active meeting."""
    stmt = delete(LiveMeeting).where(LiveMeeting.id == meeting_id)
    res = await session.execute(stmt)
    await session.commit()
    return res.rowcount > 0

# --- Teacher Marking & Feedback Hub ---

async def create_submission_review(
    session: AsyncSession,
    user_id: int,
    submission_type: str,
    title: str,
    student_content: str,
    audio_url: Optional[str] = None
) -> SubmissionReview:
    """Register student work into Teacher Marking queue."""
    sub = SubmissionReview(
        user_id=user_id,
        submission_type=submission_type,
        title=title,
        student_content=student_content,
        audio_url=audio_url,
        status="pending",
        created_at=datetime.utcnow()
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub

async def get_all_submissions_for_teacher(session: AsyncSession, limit: int = 25) -> List[Dict[str, Any]]:
    """Retrieve submissions for teacher grading hub."""
    stmt = (
        select(SubmissionReview, User.full_name, User.level)
        .join(User, SubmissionReview.user_id == User.id)
        .order_by(desc(SubmissionReview.created_at))
        .limit(limit)
    )
    res = await session.execute(stmt)
    results = []
    for sub, name, u_level in res.all():
        results.append({
            "id": sub.id,
            "user_id": sub.user_id,
            "student_name": name,
            "student_level": u_level,
            "type": sub.submission_type,
            "title": sub.title,
            "content": sub.student_content,
            "audio_url": sub.audio_url,
            "score": sub.score,
            "teacher_feedback": sub.teacher_feedback,
            "status": sub.status,
            "created_at": sub.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return results

async def grade_submission(
    session: AsyncSession,
    submission_id: int,
    score: int,
    teacher_feedback: str
) -> Optional[SubmissionReview]:
    """Teacher assigns score and written evaluation."""
    sub = await session.get(SubmissionReview, submission_id)
    if not sub:
        return None
    sub.score = score
    sub.teacher_feedback = teacher_feedback
    sub.status = "reviewed"
    sub.reviewed_at = datetime.utcnow()
    await session.commit()
    await session.refresh(sub)
    return sub

# --- General & Placement / Homework methods ---

async def save_placement_result(
    session: AsyncSession,
    user_id: int,
    target_level: str,
    score: int,
    total_questions: int,
    percentage: float,
    assigned_level: str
) -> PlacementResult:
    result = PlacementResult(
        user_id=user_id,
        target_level=target_level,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        assigned_level=assigned_level,
        created_at=datetime.utcnow()
    )
    session.add(result)
    await session.commit()
    await session.refresh(result)
    return result

async def save_homework_submission(
    session: AsyncSession,
    user_id: int,
    lesson_id: int,
    submission_type: str,
    content: str,
    score: int,
    feedback: Optional[str] = None
) -> HomeworkSubmission:
    sub = HomeworkSubmission(
        user_id=user_id,
        lesson_id=lesson_id,
        submission_type=submission_type,
        content=content,
        score=score,
        feedback=feedback,
        status="completed",
        created_at=datetime.utcnow()
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub

async def save_speaking_submission(
    session: AsyncSession,
    user_id: int,
    prompt_id: str,
    prompt_text: str,
    transcription: str,
    duration: int,
    score: int,
    feedback: str
) -> SpeakingSubmission:
    sub = SpeakingSubmission(
        user_id=user_id,
        prompt_id=prompt_id,
        prompt_text=prompt_text,
        transcription=transcription,
        duration=duration,
        score=score,
        feedback=feedback,
        created_at=datetime.utcnow()
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub

async def mark_word_learned(session: AsyncSession, user_id: int, word_id: int) -> bool:
    stmt = select(VocabularyProgress).where(
        VocabularyProgress.user_id == user_id,
        VocabularyProgress.word_id == word_id
    )
    res = await session.execute(stmt)
    if res.scalar_one_or_none():
        return False
    item = VocabularyProgress(user_id=user_id, word_id=word_id, learned_at=datetime.utcnow())
    session.add(item)
    await session.commit()
    return True

async def get_teacher_students_list(
    session: AsyncSession,
    level_filter: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get rich student list for Teacher Portal."""
    stmt = select(User).order_by(desc(User.last_active_date))
    if level_filter and level_filter != "Barchasi" and level_filter != "All":
        stmt = stmt.where(User.level == level_filter)
    stmt = stmt.limit(limit)
    res = await session.execute(stmt)
    users = res.scalars().all()
    out = []
    for u in users:
        skills = DEFAULT_SKILLS
        if u.skill_percentages:
            try:
                skills = json.loads(u.skill_percentages)
            except Exception:
                pass
        avg_score = round(sum(skills.values()) / len(skills)) if skills else 70
        out.append({
            "id": u.id,
            "telegram_id": u.telegram_id,
            "full_name": u.full_name,
            "role": u.role,
            "access_code": u.access_code or f"STU-{u.id}",
            "level": u.level or "Starter",
            "streak_days": u.streak_days or 1,
            "avg_score": avg_score,
            "last_active": u.last_active_date.strftime("%Y-%m-%d %H:%M") if u.last_active_date else "Bugun",
            "skills": skills
        })
    return out

async def get_admin_dashboard_stats(session: AsyncSession) -> Dict[str, Any]:
    total_users_stmt = select(func.count(User.id))
    total_users = (await session.execute(total_users_stmt)).scalar_one() or 0

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    active_today_stmt = select(func.count(User.id)).where(User.last_active_date >= today_start)
    active_today = (await session.execute(active_today_stmt)).scalar_one() or 0

    total_mistakes_stmt = select(func.count(MistakeLog.id))
    total_mistakes = (await session.execute(total_mistakes_stmt)).scalar_one() or 0

    total_submissions_stmt = select(func.count(SubmissionReview.id))
    total_submissions = (await session.execute(total_submissions_stmt)).scalar_one() or 0

    return {
        "total_users": total_users,
        "active_today": active_today,
        "total_mistakes": total_mistakes,
        "total_submissions": total_submissions
    }

async def increment_user_stats(
    session: AsyncSession,
    user_id: int,
    tests: int = 0,
    homeworks: int = 0,
    speaking: int = 0,
    words: int = 0,
    score_points: int = 0
) -> None:
    """Increment progress metrics for user."""
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            tests_completed=User.tests_completed + tests,
            homeworks_completed=User.homeworks_completed + homeworks,
            speaking_completed=User.speaking_completed + speaking,
            words_learned=User.words_learned + words,
            total_score=User.total_score + score_points,
            updated_at=datetime.utcnow()
        )
    )
    await session.execute(stmt)
    await session.commit()

async def get_user_learned_count(session: AsyncSession, user_id: int) -> int:
    """Count of words marked as learned by user."""
    stmt = select(func.count(VocabularyProgress.id)).where(VocabularyProgress.user_id == user_id)
    res = await session.execute(stmt)
    return res.scalar_one() or 0

async def get_students_list(
    session: AsyncSession,
    level_filter: Optional[str] = None,
    limit: int = 30
) -> List[User]:
    """Get list of users for admin."""
    stmt = select(User).order_by(desc(User.last_active_date))
    if level_filter and level_filter != "Barchasi":
        stmt = stmt.where(User.level == level_filter)
    stmt = stmt.limit(limit)
    res = await session.execute(stmt)
    return list(res.scalars().all())

async def get_all_user_ids(session: AsyncSession) -> List[int]:
    """Get all telegram IDs for broadcast."""
    stmt = select(User.telegram_id)
    res = await session.execute(stmt)
    return list(res.scalars().all())

