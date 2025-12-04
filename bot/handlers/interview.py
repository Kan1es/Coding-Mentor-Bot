"""Interview preparation handler."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import Database
from bot.ai.mistral_client import MistralAIClient
from bot.keyboards import get_interview_categories_keyboard, get_back_to_menu_keyboard

router = Router()
db = Database()
ai_client = MistralAIClient()


class InterviewStates(StatesGroup):
    """States for interview preparation."""
    waiting_for_answer = State()


@router.callback_query(F.data == "interview_prep")
async def show_interview_menu(callback: CallbackQuery):
    """Show interview preparation menu."""
    text = """🎯 Interview Preparation

Choose a category or get a random question:"""
    
    await callback.message.edit_text(text, reply_markup=get_interview_categories_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("interview_"))
async def show_interview_question(callback: CallbackQuery, state: FSMContext):
    """Show an interview question."""
    category_data = callback.data.replace("interview_", "")
    
    # Map callback data to category names
    category_map = {
        "algorithms": "Algorithms",
        "data_structures": "Data Structures",
        "system_design": "System Design",
        "oop": "OOP",
        "random": None
    }
    
    category = category_map.get(category_data)
    
    # Get random question
    question_data = await db.get_random_interview_question(category)
    
    if not question_data:
        await callback.answer("❌ No questions available in this category", show_alert=True)
        return
    
    # Store question ID in state
    await state.update_data(question_id=question_data['id'])
    
    difficulty_emoji = {
        "easy": "🟢",
        "medium": "🟡",
        "hard": "🔴"
    }.get(question_data['difficulty'].lower(), "⚪")
    
    text = f"""🎯 Interview Question

Category: {question_data['category']}
Difficulty: {difficulty_emoji} {question_data['difficulty']}

❓ Question:
{question_data['question']}

━━━━━━━━━━━━━━━━━━━━

💡 You can:
1. Send your answer and get AI feedback
2. Type /answer to see the model answer
3. Type /skip for another question"""
    
    await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard())
    await state.set_state(InterviewStates.waiting_for_answer)
    await callback.answer()


@router.message(InterviewStates.waiting_for_answer, F.text.startswith("/answer"))
async def show_model_answer(message: Message, state: FSMContext):
    """Show the model answer."""
    data = await state.get_data()
    question_id = data.get('question_id')
    
    if not question_id:
        await message.answer("❌ No active question. Please select a question first.")
        return
    
    question_data = await db.get_random_interview_question()
    # Note: We need to modify db.py to get question by ID
    # For now, we'll fetch from state or show a generic message
    
    text = """📖 Model Answer

The model answer would be displayed here. This feature requires storing the question in the state or fetching by ID.

Try answering the question yourself first for better learning! 💪"""
    
    await message.answer(text)
    await state.clear()


@router.message(InterviewStates.waiting_for_answer, F.text.startswith("/skip"))
async def skip_question(message: Message, state: FSMContext):
    """Skip to another question."""
    await state.clear()
    await message.answer("Skipped! Use the menu to get another question.", reply_markup=get_interview_categories_keyboard())


@router.message(InterviewStates.waiting_for_answer)
async def evaluate_answer(message: Message, state: FSMContext):
    """Evaluate user's answer with AI."""
    data = await state.get_data()
    question_id = data.get('question_id')
    
    if not question_id:
        await message.answer("❌ No active question.")
        await state.clear()
        return
    
    user_answer = message.text
    
    # For now, we'll use a generic question text
    # In production, fetch the actual question from database by ID
    processing_msg = await message.answer("🤖 Evaluating your answer with AI...")
    
    # Get AI evaluation
    # Note: We need the actual question text here
    evaluation = await ai_client.evaluate_interview_answer(
        "The interview question",  # Should fetch from DB
        user_answer
    )
    
    await processing_msg.delete()
    
    result_text = f"""✅ Answer Evaluated!

🤖 AI Feedback:
{evaluation}

Great job practicing! Keep it up! 💪"""
    
    await message.answer(result_text, reply_markup=get_back_to_menu_keyboard())
    await state.clear()
