"""Task scheduler for automated bot tasks."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date
import random
from database.db import Database
from bot.config import DAILY_CHALLENGE_TIME


class BotScheduler:
    """Scheduler for automated bot tasks."""
    
    def __init__(self, db: Database):
        self.db = db
        self.scheduler = AsyncIOScheduler()
    
    async def assign_daily_challenges(self):
        """Assign daily challenges to all users."""
        # Get all users
        leaderboard = await self.db.get_leaderboard(limit=1000)
        
        for user_data in leaderboard:
            user_id = user_data['user_id']
            level = user_data['level']
            
            # Select difficulty based on user level
            if level <= 3:
                difficulty = "easy"
            elif level <= 7:
                difficulty = "medium"
            else:
                difficulty = "hard"
            
            # Get random challenge of appropriate difficulty
            challenges = await self.db.get_challenges_by_difficulty(difficulty)
            if challenges:
                challenge = random.choice(challenges)
                await self.db.assign_daily_challenge(user_id, challenge['id'])
    
    async def check_streaks(self):
        """Check and update user streaks."""
        # This runs daily to ensure streaks are accurate
        leaderboard = await self.db.get_leaderboard(limit=1000)
        
        for user_data in leaderboard:
            user_id = user_data['user_id']
            await self.db.update_streak(user_id)
    
    def start(self):
        """Start the scheduler."""
        # Parse daily challenge time (format: "HH:MM")
        hour, minute = map(int, DAILY_CHALLENGE_TIME.split(":"))
        
        # Schedule daily challenge assignment
        self.scheduler.add_job(
            self.assign_daily_challenges,
            CronTrigger(hour=hour, minute=minute),
            id="daily_challenges",
            replace_existing=True
        )
        
        # Schedule streak checking (midnight)
        self.scheduler.add_job(
            self.check_streaks,
            CronTrigger(hour=0, minute=0),
            id="check_streaks",
            replace_existing=True
        )
        
        self.scheduler.start()
    
    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
