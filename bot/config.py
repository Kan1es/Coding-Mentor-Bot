"""Configuration management for the bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv("ADMIN_USER_IDS", "").split(",") if id.strip()]

# Database
DATABASE_PATH = "data/bot.db"

# Rating system constants
RATING_EASY_POINTS = 10
RATING_MEDIUM_POINTS = 25
RATING_HARD_POINTS = 50
STREAK_BONUS_MULTIPLIER = 1.1
LEVEL_UP_THRESHOLD = 100  # Points needed per level

# Challenge settings
DAILY_CHALLENGE_TIME = "09:00"  # 9 AM

# Supported languages
SUPPORTED_LANGUAGES = ["python", "javascript", "cpp"]

# Mistral AI settings
MISTRAL_MODEL = "mistral-large-latest"  # or "codestral-latest" for code-specific tasks
MISTRAL_MAX_TOKENS = 1000
MISTRAL_TEMPERATURE = 0.7

#test