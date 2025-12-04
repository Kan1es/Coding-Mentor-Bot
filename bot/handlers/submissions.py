"""Submission handler - code submission and AI review."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import Database
from database.models import ACHIEVEMENTS
from bot.ai.mistral_client import MistralAIClient
from bot.utils.rating import calculate_points, calculate_level
from bot.keyboards import get_back_to_menu_keyboard
import re

router = Router()
db = Database()
ai_client = MistralAIClient()


class SubmissionStates(StatesGroup):
    """States for code submission flow."""
    waiting_for_code = State()
    waiting_for_challenge_id = State()


@router.callback_query(F.data == "submit_code")
async def start_submission(callback: CallbackQuery, state: FSMContext):
    """Start code submission process."""
    text = """💻 Code Submission

Please send:
1. Your code as a text message
2. Or upload a file (.py, .js, .cpp)

Format (optional):
```
Challenge ID: <number>
Language: <python/javascript/cpp>

<your code here>
```

Or just send your code and I'll ask for details! 📝"""
    
    await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard())
    await state.set_state(SubmissionStates.waiting_for_code)
    await callback.answer()


@router.message(SubmissionStates.waiting_for_code)
async def receive_code_submission(message: Message, state: FSMContext):
    """Receive and process code submission."""
    user_id = message.from_user.id
    
    # Get code from message or document
    if message.document:
        # Handle file upload
        file = await message.bot.download(message.document)
        code = file.read().decode('utf-8')
        
        # Detect language from file extension
        filename = message.document.file_name
        if filename.endswith('.py'):
            language = 'python'
        elif filename.endswith('.js'):
            language = 'javascript'
        elif filename.endswith('.cpp'):
            language = 'cpp'
        else:
            language = 'python'  # default
    else:
        code = message.text
        
        # Try to extract language from message
        lang_match = re.search(r'Language:\s*(python|javascript|cpp)', code, re.IGNORECASE)
        language = lang_match.group(1).lower() if lang_match else 'python'
    
    # Try to extract challenge ID
    challenge_id_match = re.search(r'Challenge ID:\s*(\d+)', code, re.IGNORECASE)
    
    if challenge_id_match:
        challenge_id = int(challenge_id_match.group(1))
        challenge = await db.get_challenge(challenge_id)
    else:
        # Try to get daily challenge
        challenge = await db.get_daily_challenge(user_id)
    
    if not challenge:
        await message.answer("❌ Please specify a valid Challenge ID or complete your daily challenge first.")
        await state.clear()
        return
    
    # Clean code (remove metadata)
    code = re.sub(r'Challenge ID:.*?\n', '', code, flags=re.IGNORECASE)
    code = re.sub(r'Language:.*?\n', '', code, flags=re.IGNORECASE)
    code = code.strip()
    
    # Show processing message
    processing_msg = await message.answer("🤖 Reviewing your code with AI...\nThis may take a moment...")
    
    # Get AI review
    feedback = await ai_client.review_code(code, language, challenge['description'])
    
    # Determine status based on feedback (simple heuristic)
    status = "completed" if "correct" in feedback.lower() or "good" in feedback.lower() else "attempted"
    
    # Calculate points
    user = await db.get_user(user_id)
    streak = await db.update_streak(user_id)
    points_earned = calculate_points(challenge['difficulty'], streak) if status == "completed" else 0
    
    # Save submission
    await db.add_submission(
        user_id=user_id,
        challenge_id=challenge['id'],
        code=code,
        language=language,
        status=status,
        feedback=feedback,
        points_earned=points_earned
    )
    
    # Update user stats
    new_rating = user['rating'] + points_earned
    new_total = user['total_challenges'] + 1
    new_completed = user['completed_challenges'] + (1 if status == "completed" else 0)
    new_level = calculate_level(new_rating)
    
    await db.update_user_stats(
        user_id,
        rating=new_rating,
        level=new_level,
        total_challenges=new_total,
        completed_challenges=new_completed
    )
    
    # Check for achievements
    await check_and_award_achievements(user_id, new_completed, streak)
    
    # Delete processing message
    await processing_msg.delete()
    
    # Send feedback
    result_text = f"""✅ Code Review Complete!

📊 Challenge: {challenge['title']}
Status: {status.capitalize()}
Points Earned: +{points_earned} ⭐
New Rating: {new_rating}
Level: {new_level} 🎯
Streak: {streak} 🔥

🤖 AI Feedback:
{feedback}

Keep coding! 💪"""
    
    await message.answer(result_text, reply_markup=get_back_to_menu_keyboard())
    await state.clear()


async def check_and_award_achievements(user_id: int, completed_challenges: int, streak: int):
    """Check and award achievements."""
    user_achievements = await db.get_user_achievements(user_id)
    
    # First challenge
    if completed_challenges == 1 and "first_challenge" not in user_achievements:
        await db.add_achievement(user_id, "first_challenge")
    
    # Streak achievements
    if streak >= 30 and "streak_30" not in user_achievements:
        await db.add_achievement(user_id, "streak_30")
    elif streak >= 7 and "streak_7" not in user_achievements:
        await db.add_achievement(user_id, "streak_7")
    elif streak >= 3 and "streak_3" not in user_achievements:
        await db.add_achievement(user_id, "streak_3")
    
    # Challenge count achievements
    if completed_challenges >= 100 and "challenges_100" not in user_achievements:
        await db.add_achievement(user_id, "challenges_100")
    elif completed_challenges >= 50 and "challenges_50" not in user_achievements:
        await db.add_achievement(user_id, "challenges_50")
    elif completed_challenges >= 10 and "challenges_10" not in user_achievements:
        await db.add_achievement(user_id, "challenges_10")
    
    # Top 10 achievement
    rank = await db.get_user_rank(user_id)
    if rank <= 10 and "top_10" not in user_achievements:
        await db.add_achievement(user_id, "top_10")
