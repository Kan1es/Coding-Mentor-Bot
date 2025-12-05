"""Main bot entry point."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import TELEGRAM_BOT_TOKEN
from database.db import Database
from bot.utils.scheduler import BotScheduler

# Import handlers
from bot.handlers import start, challenges, submissions, interview, profile, leaderboard, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main bot function."""
    # Initialize bot and dispatcher
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Initialize database
    db = Database()
    await db.init_db()
    logger.info("Database initialized")
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(challenges.router)
    dp.include_router(submissions.router)
    dp.include_router(interview.router)
    dp.include_router(profile.router)
    dp.include_router(leaderboard.router)
    logger.info("Handlers registered")
    
    # Initialize and start scheduler
    scheduler = BotScheduler(db)
    scheduler.start()
    logger.info("Scheduler started")
    
    # Start polling
    try:
        logger.info("Bot started")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
