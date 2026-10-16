"""
Router aggregator for Umar Tutor Bot.
"""
from aiogram import Router

from handlers.start import router as start_router
from handlers.testing import router as testing_router
from handlers.homework import router as homework_router
from handlers.speaking import router as speaking_router
from handlers.vocabulary import router as vocabulary_router
from handlers.grammar import router as grammar_router
from handlers.profile import router as profile_router
from handlers.admin import router as admin_router
from handlers.fallback import router as fallback_router

def get_main_router() -> Router:
    """Combines all modular handlers into a single parent router."""
    main_router = Router(name="main_router")

    # Include routers in logical precedence
    main_router.include_router(start_router)
    main_router.include_router(admin_router)
    main_router.include_router(testing_router)
    main_router.include_router(homework_router)
    main_router.include_router(speaking_router)
    main_router.include_router(vocabulary_router)
    main_router.include_router(grammar_router)
    main_router.include_router(profile_router)
    main_router.include_router(fallback_router)

    return main_router
