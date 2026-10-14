"""
Database base and session management for Umar Tutor bot.
Using SQLAlchemy 2.0 async engine with aiosqlite.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = None
async_session = None

def get_engine(db_url: str):
    global engine, async_session
    if engine is None:
        # SQLite connection setup
        engine = create_async_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False}
        )
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return engine

def get_session_maker():
    global async_session
    if async_session is None:
        from config import settings
        get_engine(settings.DATABASE_URL)
    return async_session

async def init_db(db_url: str):
    """Create all tables in the database."""
    eng = get_engine(db_url)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
