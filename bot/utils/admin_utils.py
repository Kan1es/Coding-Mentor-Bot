"""Admin utility functions."""
from typing import Dict, Any
from aiogram import Bot
from database.db import Database
from bot.config import ADMIN_USER_IDS
import asyncio


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in ADMIN_USER_IDS


def format_user_info(user: Dict[str, Any], detailed: bool = False) -> str:
    """Format user data for display."""
    is_banned = user.get('is_banned', 0)
    ban_status = "🚫 BANNED" if is_banned else "✅ Active"
    
    info = f"""
👤 **User Info**

**ID:** `{user['user_id']}`
**Username:** @{user['username'] or 'N/A'}
**Status:** {ban_status}

📊 **Statistics:**
⭐ Rating: {user['rating']}
🎯 Level: {user['level']}
🔥 Streak: {user['streak']} days
✅ Completed: {user['completed_challenges']}/{user['total_challenges']}

📅 **Activity:**
Last Active: {user['last_active'][:10]}
Joined: {user['created_at'][:10]}
"""
    
    return info.strip()


def format_challenge_info(challenge: Dict[str, Any]) -> str:
    """Format challenge data for display."""
    difficulty_emoji = {
        'easy': '🟢',
        'medium': '🟡',
        'hard': '🔴'
    }
    
    emoji = difficulty_emoji.get(challenge['difficulty'].lower(), '⚪')
    
    info = f"""
💻 **Challenge #{challenge['id']}**

**Title:** {challenge['title']}
**Difficulty:** {emoji} {challenge['difficulty'].title()}
**Language:** {challenge['language']}
**Points:** {challenge['points']}

**Description:**
{challenge['description'][:200]}{'...' if len(challenge['description']) > 200 else ''}

Created: {challenge['created_at'][:10]}
"""
    
    return info.strip()


def format_interview_question_info(question: Dict[str, Any]) -> str:
    """Format interview question for display."""
    difficulty_emoji = {
        'easy': '🟢',
        'medium': '🟡',
        'hard': '🔴'
    }
    
    emoji = difficulty_emoji.get(question['difficulty'].lower(), '⚪')
    
    info = f"""
🎯 **Question #{question['id']}**

**Category:** {question['category']}
**Difficulty:** {emoji} {question['difficulty'].title()}

**Question:**
{question['question'][:300]}{'...' if len(question['question']) > 300 else ''}

Created: {question['created_at'][:10]}
"""
    
    return info.strip()


async def broadcast_message(bot: Bot, db: Database, message_text: str, 
                           exclude_banned: bool = True) -> Dict[str, int]:
    """
    Broadcast message to all users.
    
    Returns dict with 'success' and 'failed' counts.
    """
    users = await db.get_all_users(limit=10000)  # Get all users
    
    success_count = 0
    failed_count = 0
    
    for user in users:
        # Skip banned users if requested
        if exclude_banned and user.get('is_banned'):
            continue
        
        try:
            await bot.send_message(user['user_id'], message_text, parse_mode='Markdown')
            success_count += 1
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.05)
        except Exception:
            failed_count += 1
    
    return {
        'success': success_count,
        'failed': failed_count
    }


def validate_challenge_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate challenge data.
    
    Returns (is_valid, error_message).
    """
    required_fields = ['title', 'description', 'difficulty', 'language', 'test_cases', 'points']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    if data['difficulty'].lower() not in ['easy', 'medium', 'hard']:
        return False, "Difficulty must be: easy, medium, or hard"
    
    if data['language'].lower() not in ['python', 'javascript', 'cpp']:
        return False, "Language must be: python, javascript, or cpp"
    
    try:
        points = int(data['points'])
        if points <= 0:
            return False, "Points must be positive"
    except ValueError:
        return False, "Points must be a number"
    
    return True, ""
