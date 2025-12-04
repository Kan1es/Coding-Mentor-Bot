"""Rating calculation utilities."""
from bot.config import (
    RATING_EASY_POINTS, RATING_MEDIUM_POINTS, RATING_HARD_POINTS,
    STREAK_BONUS_MULTIPLIER, LEVEL_UP_THRESHOLD
)


def calculate_points(difficulty: str, streak: int = 0) -> int:
    """
    Calculate points earned for completing a challenge.
    
    Args:
        difficulty: Challenge difficulty (easy, medium, hard)
        streak: Current user streak
        
    Returns:
        Points earned
    """
    base_points = {
        "easy": RATING_EASY_POINTS,
        "medium": RATING_MEDIUM_POINTS,
        "hard": RATING_HARD_POINTS
    }.get(difficulty.lower(), RATING_EASY_POINTS)
    
    # Apply streak bonus
    if streak >= 7:
        multiplier = STREAK_BONUS_MULTIPLIER ** 2  # 1.21x for 7+ days
    elif streak >= 3:
        multiplier = STREAK_BONUS_MULTIPLIER  # 1.1x for 3+ days
    else:
        multiplier = 1.0
    
    return int(base_points * multiplier)


def calculate_level(total_points: int) -> int:
    """
    Calculate user level based on total points.
    
    Args:
        total_points: Total points earned
        
    Returns:
        User level
    """
    return (total_points // LEVEL_UP_THRESHOLD) + 1


def points_to_next_level(current_points: int) -> int:
    """
    Calculate points needed for next level.
    
    Args:
        current_points: Current total points
        
    Returns:
        Points needed for next level
    """
    current_level = calculate_level(current_points)
    next_level_threshold = current_level * LEVEL_UP_THRESHOLD
    return next_level_threshold - current_points


def get_rank_emoji(rank: int) -> str:
    """
    Get emoji for leaderboard rank.
    
    Args:
        rank: User's rank
        
    Returns:
        Emoji representing the rank
    """
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    elif rank <= 10:
        return "🏅"
    else:
        return "📊"


def format_rating_change(old_rating: int, new_rating: int) -> str:
    """
    Format rating change message.
    
    Args:
        old_rating: Previous rating
        new_rating: New rating
        
    Returns:
        Formatted string
    """
    change = new_rating - old_rating
    if change > 0:
        return f"+{change} ⬆️"
    elif change < 0:
        return f"{change} ⬇️"
    else:
        return "±0"
