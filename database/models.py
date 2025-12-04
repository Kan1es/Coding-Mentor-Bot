"""Database models and schema definitions."""
from datetime import datetime
from typing import Optional

# SQL schema definitions
USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    rating INTEGER DEFAULT 1000,
    level INTEGER DEFAULT 1,
    total_challenges INTEGER DEFAULT 0,
    completed_challenges INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    last_active TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

CHALLENGES_TABLE = """
CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    language TEXT NOT NULL,
    test_cases TEXT NOT NULL,
    solution TEXT,
    points INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

SUBMISSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    language TEXT NOT NULL,
    status TEXT NOT NULL,
    feedback TEXT,
    points_earned INTEGER DEFAULT 0,
    submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
)
"""

INTERVIEW_QUESTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS interview_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

USER_ACHIEVEMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id TEXT NOT NULL,
    earned_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
"""

USER_DAILY_CHALLENGES_TABLE = """
CREATE TABLE IF NOT EXISTS user_daily_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    assigned_date TEXT NOT NULL,
    completed BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
)
"""

# Achievement definitions
ACHIEVEMENTS = {
    "first_challenge": {
        "name": "🎯 First Steps",
        "description": "Complete your first challenge"
    },
    "streak_3": {
        "name": "🔥 On Fire",
        "description": "Maintain a 3-day streak"
    },
    "streak_7": {
        "name": "⚡ Unstoppable",
        "description": "Maintain a 7-day streak"
    },
    "streak_30": {
        "name": "💎 Legend",
        "description": "Maintain a 30-day streak"
    },
    "challenges_10": {
        "name": "📚 Learner",
        "description": "Complete 10 challenges"
    },
    "challenges_50": {
        "name": "🎓 Expert",
        "description": "Complete 50 challenges"
    },
    "challenges_100": {
        "name": "🏆 Master",
        "description": "Complete 100 challenges"
    },
    "top_10": {
        "name": "👑 Top 10",
        "description": "Reach top 10 on leaderboard"
    }
}
