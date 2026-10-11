"""
SQLAlchemy database models for Umar Tutor Bot.
Extended for Multi-Role (Student/Teacher/Admin), Multi-Level, CMS, Error Analytics & Live Meetings.
"""
from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default="student")  # "student", "teacher", "admin"
    access_code = Column(String(50), nullable=True, index=True)  # Student personal PIN / access code
    level = Column(String(20), default="Starter")  # Starter, A1, A2, B1, B2, IELTS
    streak_days = Column(Integer, default=1)
    last_active_date = Column(DateTime, default=datetime.utcnow)
    
    # Progress metrics
    words_learned = Column(Integer, default=0)
    tests_completed = Column(Integer, default=0)
    homeworks_completed = Column(Integer, default=0)
    speaking_completed = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    
    # Detailed Skill Mastery percentages stored as JSON:
    # {"vocab": 75, "grammar": 68, "speaking": 60, "listening": 70, "reading": 65, "quiz": 80}
    skill_percentages = Column(Text, nullable=True)
    weak_points = Column(Text, nullable=True)  # JSON list of detected weak points / recommendations
    
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_results = relationship("PlacementResult", back_populates="user", cascade="all, delete-orphan")
    homework_submissions = relationship("HomeworkSubmission", back_populates="user", cascade="all, delete-orphan")
    speaking_submissions = relationship("SpeakingSubmission", back_populates="user", cascade="all, delete-orphan")
    learned_words = relationship("VocabularyProgress", back_populates="user", cascade="all, delete-orphan")
    mistakes = relationship("MistakeLog", back_populates="user", cascade="all, delete-orphan")
    submission_reviews = relationship("SubmissionReview", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.telegram_id} ({self.full_name}, role={self.role}, level={self.level})>"


class PlacementResult(Base):
    __tablename__ = "placement_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_level = Column(String(20), default="Placement")
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    assigned_level = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="test_results")

    def __repr__(self):
        return f"<PlacementResult user={self.user_id} score={self.score}/{self.total_questions} level={self.assigned_level}>"


class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, nullable=False)
    submission_type = Column(String(20), nullable=False)  # "quiz" or "writing"
    content = Column(Text, nullable=False)  # JSON or text response
    score = Column(Integer, default=0)
    max_score = Column(Integer, default=100)
    feedback = Column(Text, nullable=True)
    status = Column(String(20), default="completed")  # "completed", "pending_review"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="homework_submissions")


class SpeakingSubmission(Base):
    __tablename__ = "speaking_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prompt_id = Column(String(50), nullable=False)
    prompt_text = Column(Text, nullable=False)
    file_id = Column(String(255), nullable=True)  # Audio file_id or recording ref
    transcription = Column(Text, nullable=True)
    duration = Column(Integer, default=0)  # seconds
    score = Column(Integer, default=80)
    feedback = Column(Text, nullable=True)  # ChatGPT-style detailed AI feedback
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="speaking_submissions")


class VocabularyProgress(Base):
    __tablename__ = "vocabulary_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, nullable=False)
    learned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="learned_words")


class MistakeLog(Base):
    """Logs student mistakes for error analytics and personalized weak point recommendations."""
    __tablename__ = "mistake_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)  # quiz, grammar, vocab, listening, reading
    level = Column(String(20), default="A1")
    question_text = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mistakes")


class CourseMaterial(Base):
    """Dynamic materials added by teachers/admins via CMS."""
    __tablename__ = "course_materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)  # "vocab", "quiz", "grammar", "listening", "reading", "shadowing"
    level = Column(String(20), nullable=False)      # "Starter", "A1", "A2", "B1", "B2", "IELTS"
    title = Column(String(255), nullable=False)
    content_json = Column(Text, nullable=False)     # Complete material structured payload
    created_by = Column(String(100), default="Teacher Umar")
    created_at = Column(DateTime, default=datetime.utcnow)


class LiveMeeting(Base):
    """Live online classes created by Teacher/Admin."""
    __tablename__ = "live_meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    level = Column(String(50), default="Barcha darajalar")
    datetime_str = Column(String(100), nullable=False)  # e.g., "Bugun, 20:00"
    meeting_link = Column(String(500), nullable=False)
    platform = Column(String(50), default="Telegram")    # "Zoom", "Google Meet", "Telegram"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubmissionReview(Base):
    """Student submissions queued for Teacher/Admin grading and marking."""
    __tablename__ = "submission_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submission_type = Column(String(50), nullable=False)  # "speaking", "writing", "quiz"
    title = Column(String(255), nullable=False)
    student_content = Column(Text, nullable=False)
    audio_url = Column(String(500), nullable=True)
    score = Column(Integer, nullable=True)
    teacher_feedback = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # "pending", "reviewed"
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="submission_reviews")
