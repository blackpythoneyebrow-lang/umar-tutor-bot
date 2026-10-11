"""
Bot, Dispatcher, and Middleware setup for Umar Tutor Bot.
"""
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database.base import init_db, get_session_maker
from middlewares.db_session import DbSessionMiddleware
from middlewares.user_tracker import UserTrackerMiddleware
from handlers import get_main_router

# Initialize Bot
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Initialize Dispatcher with memory storage
dp = Dispatcher(storage=MemoryStorage())

async def setup_bot_and_dispatcher():
    """Configures database, middlewares, and routers."""
    # 1. Initialize SQLite tables
    await init_db(settings.DATABASE_URL)
    session_maker = get_session_maker()

    # 2. Attach Middlewares
    dp.update.middleware(DbSessionMiddleware(session_maker))
    dp.update.middleware(UserTrackerMiddleware())

    # 3. Register Handler Routers
    dp.include_router(get_main_router())
