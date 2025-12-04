"""Start command handler - welcome and registration."""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from database.db import Database
from bot.keyboards import get_main_menu

router = Router()
db = Database()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Create or get user
    user = await db.get_user(user_id)
    if not user:
        await db.create_user(user_id, username)
        welcome_text = f"""🎉 Welcome to Coding Mentor, {username}!

I'm your personal coding assistant to help you:
📝 Practice with daily coding challenges
💻 Get AI-powered code reviews
🎯 Prepare for technical interviews
🏆 Compete on the leaderboard

Let's start your coding journey! 🚀"""
    else:
        welcome_text = f"""👋 Welcome back, {username}!

Ready to continue your coding journey?
Current Rating: {user['rating']} ⭐
Level: {user['level']} 🎯
Streak: {user['streak']} 🔥"""
    
    await message.answer(welcome_text, reply_markup=get_main_menu())


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Show main menu."""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if user:
        text = f"""🏠 Main Menu

Rating: {user['rating']} ⭐
Level: {user['level']} 🎯
Streak: {user['streak']} 🔥

Choose an option:"""
    else:
        text = "🏠 Main Menu\n\nChoose an option:"
    
    await callback.message.edit_text(text, reply_markup=get_main_menu())
    await callback.answer()
