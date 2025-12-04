"""Leaderboard handler - rankings and competition."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.db import Database
from bot.keyboards import get_leaderboard_keyboard, get_back_to_menu_keyboard
from bot.utils.rating import get_rank_emoji

router = Router()
db = Database()


@router.callback_query(F.data == "leaderboard")
async def show_leaderboard_menu(callback: CallbackQuery):
    """Show leaderboard menu."""
    text = """🏆 Leaderboard

Choose how many top users to display:"""
    
    await callback.message.edit_text(text, reply_markup=get_leaderboard_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("leaderboard_"))
async def show_leaderboard(callback: CallbackQuery):
    """Display leaderboard."""
    limit = int(callback.data.split("_")[1])
    
    # Get leaderboard
    leaderboard = await db.get_leaderboard(limit=limit)
    
    if not leaderboard:
        await callback.answer("❌ No users found", show_alert=True)
        return
    
    # Get current user's rank
    user_id = callback.from_user.id
    user_rank = await db.get_user_rank(user_id)
    
    # Build leaderboard text
    text = f"🏆 Top {limit} Leaderboard\n\n"
    
    for idx, user_data in enumerate(leaderboard, 1):
        rank_emoji = get_rank_emoji(idx)
        
        # Highlight current user
        if user_data['user_id'] == user_id:
            text += f"➤ {rank_emoji} #{idx} {user_data['username']}\n"
        else:
            text += f"{rank_emoji} #{idx} {user_data['username']}\n"
        
        text += f"   ⭐ {user_data['rating']} | 🎯 Lvl {user_data['level']} | ✅ {user_data['completed_challenges']} | 🔥 {user_data['streak']}\n\n"
    
    # Add current user's position if not in top
    if user_rank > limit:
        user = await db.get_user(user_id)
        if user:
            text += f"\n━━━━━━━━━━━━━━━━━━━━\n"
            text += f"Your position: #{user_rank}\n"
            text += f"⭐ {user['rating']} | 🎯 Lvl {user['level']} | ✅ {user['completed_challenges']}\n"
    
    await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard())
    await callback.answer()
