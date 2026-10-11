"""
User tracking and streak update middleware for aiogram 3.x.
Ensures every user interaction is tracked in database and injects 'user' into handler context.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.crud import get_or_create_user, update_user_activity_and_streak

class UserTrackerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        tg_user: TgUser = data.get("event_from_user")
        session: AsyncSession = data.get("session")

        if tg_user and session:
            # Upsert user record
            user = await get_or_create_user(
                session=session,
                telegram_id=tg_user.id,
                full_name=tg_user.full_name,
                username=tg_user.username,
                admin_ids=settings.ADMIN_IDS
            )
            # Update last activity and daily streak
            user = await update_user_activity_and_streak(session, tg_user.id) or user
            data["user"] = user

        return await handler(event, data)
