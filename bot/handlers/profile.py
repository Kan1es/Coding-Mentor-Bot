"""Profile handler - user statistics and achievements."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.db import Database
from database.models import ACHIEVEMENTS
from bot.keyboards import get_back_to_menu_keyboard
from bot.utils.rating import points_to_next_level, get_rank_emoji

router = Router()
db = Database()


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    """Show user profile and statistics."""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ User not found. Please use /start", show_alert=True)
        return
    
    # Get user rank
    rank = await db.get_user_rank(user_id)
    rank_emoji = get_rank_emoji(rank)
    
    # Get achievements
    user_achievements = await db.get_user_achievements(user_id)
    
    # Calculate stats
    completion_rate = (user['completed_challenges'] / user['total_challenges'] * 100) if user['total_challenges'] > 0 else 0
    
    # Build profile text
    profile_text = f"""👤 Profile: {user['username']}

📊 Statistics:
{rank_emoji} Rank: #{rank}
⭐ Rating: {user['rating']}
🎯 Level: {user['level']}
🔥 Streak: {user['streak']} days
✅ Completed: {user['completed_challenges']}/{user['total_challenges']} ({completion_rate:.1f}%)

🏆 Achievements ({len(user_achievements)}):
"""
    
    # Add achievements
    if user_achievements:
        for ach_id in user_achievements[:5]:  # Show first 5
            if ach_id in ACHIEVEMENTS:
                ach = ACHIEVEMENTS[ach_id]
                profile_text += f"\n{ach['name']}\n  {ach['description']}"
        
        if len(user_achievements) > 5:
            profile_text += f"\n\n...and {len(user_achievements) - 5} more!"
    else:
        profile_text += "\nNo achievements yet. Keep coding! 💪"
    
    await callback.message.edit_text(profile_text, reply_markup=get_back_to_menu_keyboard())
    await callback.answer()
