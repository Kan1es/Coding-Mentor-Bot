"""Challenge handler - daily challenges and browsing."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.db import Database
from bot.keyboards import get_challenge_actions_keyboard, get_difficulty_keyboard, get_back_to_menu_keyboard
from bot.ai.mistral_client import MistralAIClient
import random
import json

router = Router()
db = Database()
ai_client = MistralAIClient()


@router.callback_query(F.data == "daily_challenge")
async def show_daily_challenge(callback: CallbackQuery):
    """Show today's daily challenge."""
    user_id = callback.from_user.id
    
    # Get or assign daily challenge
    challenge = await db.get_daily_challenge(user_id)
    
    if not challenge:
        # Assign new challenge based on user level
        user = await db.get_user(user_id)
        if not user:
            await callback.answer("❌ Please use /start first", show_alert=True)
            return
        
        # Select difficulty based on level
        if user['level'] <= 3:
            difficulty = "easy"
        elif user['level'] <= 7:
            difficulty = "medium"
        else:
            difficulty = "hard"
        
        # Get random challenge
        challenges = await db.get_challenges_by_difficulty(difficulty)
        if not challenges:
            await callback.answer("❌ No challenges available", show_alert=True)
            return
        
        challenge = random.choice(challenges)
        await db.assign_daily_challenge(user_id, challenge['id'])
    
    # Format challenge text
    difficulty_emoji = {
        "easy": "🟢",
        "medium": "🟡",
        "hard": "🔴"
    }.get(challenge['difficulty'].lower(), "⚪")
    
    text = f"""📝 Daily Challenge

{difficulty_emoji} {challenge['title']}
Difficulty: {challenge['difficulty'].capitalize()}
Language: {challenge['language'].upper()}
Points: {challenge['points']} ⭐

📋 Description:
{challenge['description']}

🧪 Test Cases:
{challenge['test_cases']}

Good luck! 🚀"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_challenge_actions_keyboard(challenge['id'])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hint_"))
async def get_hint(callback: CallbackQuery):
    """Generate a hint for the challenge."""
    challenge_id = int(callback.data.split("_")[1])
    
    challenge = await db.get_challenge(challenge_id)
    if not challenge:
        await callback.answer("❌ Challenge not found", show_alert=True)
        return
    
    await callback.answer("💡 Generating hint...", show_alert=False)
    
    # Generate hint using AI
    hint = await ai_client.generate_hint(challenge['description'], challenge['language'])
    
    hint_text = f"""💡 Hint for: {challenge['title']}

{hint}

Good luck! You got this! 💪"""
    
    await callback.message.answer(hint_text)


@router.callback_query(F.data.startswith("submit_solution_"))
async def prompt_solution_submission(callback: CallbackQuery):
    """Prompt user to submit their solution."""
    challenge_id = callback.data.split("_")[2]
    
    text = f"""✍️ Submit Your Solution

Please send your code as:
1. A text message with your code
2. Or upload a file (.py, .js, .cpp)

Challenge ID: {challenge_id}

I'll review it with AI and provide feedback! 🤖"""
    
    await callback.message.answer(text)
    await callback.answer()
