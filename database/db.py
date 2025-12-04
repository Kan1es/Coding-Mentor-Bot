"""Database connection manager and CRUD operations."""
import aiosqlite
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from bot.config import DATABASE_PATH
from database.models import (
    USERS_TABLE, CHALLENGES_TABLE, SUBMISSIONS_TABLE,
    INTERVIEW_QUESTIONS_TABLE, USER_ACHIEVEMENTS_TABLE,
    USER_DAILY_CHALLENGES_TABLE
)


class Database:
    """Database manager for the bot."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database and create tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(USERS_TABLE)
            await db.execute(CHALLENGES_TABLE)
            await db.execute(SUBMISSIONS_TABLE)
            await db.execute(INTERVIEW_QUESTIONS_TABLE)
            await db.execute(USER_ACHIEVEMENTS_TABLE)
            await db.execute(USER_DAILY_CHALLENGES_TABLE)
            await db.commit()
    
    # User operations
    async def create_user(self, user_id: int, username: str) -> None:
        """Create a new user."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username, last_active) VALUES (?, ?, ?)",
                (user_id, username, datetime.now().isoformat())
            )
            await db.commit()
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def update_user_stats(self, user_id: int, **kwargs) -> None:
        """Update user statistics."""
        fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE users SET {fields}, last_active = ? WHERE user_id = ?",
                values + [datetime.now().isoformat(), user_id]
            )
            await db.commit()
    
    async def update_streak(self, user_id: int) -> int:
        """Update user streak and return new streak value."""
        user = await self.get_user(user_id)
        if not user:
            return 0
        
        last_active = datetime.fromisoformat(user['last_active']).date()
        today = date.today()
        
        if (today - last_active).days == 1:
            # Continue streak
            new_streak = user['streak'] + 1
        elif (today - last_active).days == 0:
            # Same day
            new_streak = user['streak']
        else:
            # Streak broken
            new_streak = 1
        
        await self.update_user_stats(user_id, streak=new_streak)
        return new_streak
    
    # Challenge operations
    async def add_challenge(self, title: str, description: str, difficulty: str,
                           language: str, test_cases: str, solution: str, points: int) -> int:
        """Add a new challenge."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO challenges (title, description, difficulty, language, test_cases, solution, points)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, description, difficulty, language, test_cases, solution, points)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_challenge(self, challenge_id: int) -> Optional[Dict[str, Any]]:
        """Get challenge by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def get_challenges_by_difficulty(self, difficulty: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get challenges by difficulty and optionally by language."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if language:
                query = "SELECT * FROM challenges WHERE difficulty = ? AND language = ?"
                params = (difficulty, language)
            else:
                query = "SELECT * FROM challenges WHERE difficulty = ?"
                params = (difficulty,)
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_daily_challenge(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get today's challenge for user."""
        today = date.today().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT c.* FROM challenges c
                   JOIN user_daily_challenges udc ON c.id = udc.challenge_id
                   WHERE udc.user_id = ? AND udc.assigned_date = ?""",
                (user_id, today)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def assign_daily_challenge(self, user_id: int, challenge_id: int) -> None:
        """Assign a daily challenge to user."""
        today = date.today().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR IGNORE INTO user_daily_challenges (user_id, challenge_id, assigned_date)
                   VALUES (?, ?, ?)""",
                (user_id, challenge_id, today)
            )
            await db.commit()
    
    # Submission operations
    async def add_submission(self, user_id: int, challenge_id: int, code: str,
                            language: str, status: str, feedback: str, points_earned: int) -> int:
        """Add a code submission."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO submissions (user_id, challenge_id, code, language, status, feedback, points_earned)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, challenge_id, code, language, status, feedback, points_earned)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_user_submissions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent submissions."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT s.*, c.title as challenge_title FROM submissions s
                   JOIN challenges c ON s.challenge_id = c.id
                   WHERE s.user_id = ?
                   ORDER BY s.submitted_at DESC LIMIT ?""",
                (user_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    # Interview questions
    async def add_interview_question(self, category: str, question: str, answer: str, difficulty: str) -> int:
        """Add an interview question."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO interview_questions (category, question, answer, difficulty)
                   VALUES (?, ?, ?, ?)""",
                (category, question, answer, difficulty)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_random_interview_question(self, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a random interview question."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if category:
                query = "SELECT * FROM interview_questions WHERE category = ? ORDER BY RANDOM() LIMIT 1"
                params = (category,)
            else:
                query = "SELECT * FROM interview_questions ORDER BY RANDOM() LIMIT 1"
                params = ()
            
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def get_interview_categories(self) -> List[str]:
        """Get all interview question categories."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT DISTINCT category FROM interview_questions") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    # Achievements
    async def add_achievement(self, user_id: int, achievement_id: str) -> None:
        """Add an achievement to user."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR IGNORE INTO user_achievements (user_id, achievement_id)
                   VALUES (?, ?)""",
                (user_id, achievement_id)
            )
            await db.commit()
    
    async def get_user_achievements(self, user_id: int) -> List[str]:
        """Get user's achievements."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT achievement_id FROM user_achievements WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    # Leaderboard
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by rating."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT user_id, username, rating, level, completed_challenges, streak
                   FROM users
                   ORDER BY rating DESC
                   LIMIT ?""",
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_user_rank(self, user_id: int) -> int:
        """Get user's rank on leaderboard."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT COUNT(*) + 1 as rank FROM users
                   WHERE rating > (SELECT rating FROM users WHERE user_id = ?)""",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
