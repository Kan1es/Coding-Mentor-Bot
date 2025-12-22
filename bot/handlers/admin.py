"""Admin panel handlers."""
import json
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import Database
from bot.keyboards import (
    get_admin_menu, get_admin_stats_keyboard, get_admin_users_keyboard,
    get_user_actions_keyboard, get_admin_challenges_keyboard,
    get_challenge_actions_keyboard, get_admin_interview_keyboard,
    get_interview_question_actions_keyboard, get_broadcast_keyboard,
    get_confirm_keyboard, get_main_menu
)
from bot.utils.admin_utils import (
    is_admin, format_user_info, format_challenge_info,
    format_interview_question_info, broadcast_message, validate_challenge_data
)

router = Router()
db = Database()


# FSM States for admin operations
class AdminStates(StatesGroup):
    waiting_for_search_query = State()
    waiting_for_ban_reason = State()
    waiting_for_challenge_title = State()
    waiting_for_challenge_description = State()
    waiting_for_challenge_difficulty = State()
    waiting_for_challenge_language = State()
    waiting_for_challenge_test_cases = State()
    waiting_for_challenge_solution = State()
    waiting_for_challenge_points = State()
    waiting_for_broadcast_message = State()
    waiting_for_interview_category = State()
    waiting_for_interview_question = State()
    waiting_for_interview_answer = State()
    waiting_for_interview_difficulty = State()


# Admin Panel Main Menu
@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery):
    """Show admin panel main menu."""
    user_id = callback.from_user.id
    
    # Redirect non-admins to main menu instead of showing error
    if not is_admin(user_id):
        user = await db.get_user(user_id)
        if user:
            text = f"""🏠 Main Menu

Rating: {user['rating']} ⭐
Level: {user['level']} 🎯
Streak: {user['streak']} 🔥

Choose an option:"""
        else:
            text = "🏠 Main Menu\n\nChoose an option:"
        
        await callback.message.edit_text(text, reply_markup=get_main_menu(user_id))
        await callback.answer()
        return
    
    text = """
⚙️ **Admin Panel**

Welcome to the admin control panel.
Select an option below to manage the bot.
"""
    
    await callback.message.edit_text(
        text.strip(),
        reply_markup=get_admin_menu(),
        parse_mode='Markdown'
    )
    await callback.answer()


# Statistics Dashboard
@router.callback_query(F.data == "admin_stats")
async def show_statistics(callback: CallbackQuery):
    """Show bot statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    # Gather statistics
    total_users = await db.get_user_count()
    active_7d = await db.get_active_users_count(7)
    active_30d = await db.get_active_users_count(30)
    total_challenges = await db.get_challenge_count()
    challenges_by_diff = await db.get_challenges_count_by_difficulty()
    total_submissions = await db.get_total_submissions()
    submissions_by_status = await db.get_submissions_by_status()
    total_questions = await db.get_interview_question_count()
    
    # Calculate success rate
    success = submissions_by_status.get('success', 0)
    total_sub = total_submissions if total_submissions > 0 else 1
    success_rate = (success / total_sub) * 100
    
    text = f"""
📊 **Bot Statistics**

👥 **Users:**
• Total: {total_users}
• Active (7 days): {active_7d}
• Active (30 days): {active_30d}

💻 **Challenges:**
• Total: {total_challenges}
• 🟢 Easy: {challenges_by_diff.get('easy', 0)}
• 🟡 Medium: {challenges_by_diff.get('medium', 0)}
• 🔴 Hard: {challenges_by_diff.get('hard', 0)}

📝 **Submissions:**
• Total: {total_submissions}
• Success Rate: {success_rate:.1f}%
• ✅ Successful: {submissions_by_status.get('success', 0)}
• ❌ Failed: {submissions_by_status.get('failed', 0)}

🎯 **Interview Questions:** {total_questions}
"""
    
    await callback.message.edit_text(
        text.strip(),
        reply_markup=get_admin_stats_keyboard(),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data == "admin_recent_activity")
async def show_recent_activity(callback: CallbackQuery):
    """Show recent user activity."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    activities = await db.get_recent_activity(days=7, limit=10)
    
    if not activities:
        text = "📈 **Recent Activity**\n\nNo recent activity in the last 7 days."
    else:
        text = "📈 **Recent Activity (Last 7 Days)**\n\n"
        for activity in activities:
            status_emoji = "✅" if activity['status'] == 'success' else "❌"
            text += f"{status_emoji} @{activity['username']} - {activity['challenge_title']}\n"
            text += f"   {activity['submitted_at'][:16]}\n\n"
    
    await callback.message.edit_text(
        text.strip(),
        reply_markup=get_admin_stats_keyboard(),
        parse_mode='Markdown'
    )
    await callback.answer()


# User Management
@router.callback_query(F.data.startswith("admin_users"))
async def show_users(callback: CallbackQuery):
    """Show user list with pagination."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    # Parse page number
    page = 0
    if "_page_" in callback.data:
        page = int(callback.data.split("_")[-1])
    
    limit = 10
    offset = page * limit
    
    users = await db.get_all_users(limit=limit + 1, offset=offset)
    has_next = len(users) > limit
    users = users[:limit]
    
    if not users:
        text = "👥 **User Management**\n\nNo users found."
    else:
        text = f"👥 **User Management** (Page {page + 1})\n\n"
        for user in users:
            ban_status = "🚫" if user.get('is_banned') else "✅"
            text += f"{ban_status} `{user['user_id']}` - @{user['username'] or 'N/A'}\n"
            text += f"   Rating: {user['rating']} | Level: {user['level']}\n\n"
    
    await callback.message.edit_text(
        text.strip(),
        reply_markup=get_admin_users_keyboard(page, has_next),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data == "admin_search_user")
async def request_user_search(callback: CallbackQuery, state: FSMContext):
    """Request user search query."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔍 **Search User**\n\nSend user ID or username to search:",
        parse_mode='Markdown'
    )
    await state.set_state(AdminStates.waiting_for_search_query)
    await callback.answer()


@router.message(AdminStates.waiting_for_search_query)
async def process_user_search(message: Message, state: FSMContext):
    """Process user search query."""
    if not is_admin(message.from_user.id):
        return
    
    query = message.text.strip()
    users = await db.search_users(query)
    
    if not users:
        text = f"🔍 **Search Results**\n\nNo users found for: `{query}`"
        await message.answer(text, reply_markup=get_admin_users_keyboard(), parse_mode='Markdown')
    else:
        text = f"🔍 **Search Results** ({len(users)} found)\n\n"
        for user in users:
            ban_status = "🚫" if user.get('is_banned') else "✅"
            text += f"{ban_status} `{user['user_id']}` - @{user['username'] or 'N/A'}\n"
            text += f"   Rating: {user['rating']} | Level: {user['level']}\n\n"
        
        await message.answer(text.strip(), reply_markup=get_admin_users_keyboard(), parse_mode='Markdown')
    
    await state.clear()


@router.callback_query(F.data.startswith("admin_user_details_"))
async def show_user_details(callback: CallbackQuery):
    """Show detailed user information."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[-1])
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("User not found.", show_alert=True)
        return
    
    is_banned = await db.is_user_banned(user_id)
    user['is_banned'] = is_banned
    
    text = format_user_info(user, detailed=True)
    
    await callback.message.edit_text(
        text,
        reply_markup=get_user_actions_keyboard(user_id, is_banned),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_ban_"))
async def ban_user(callback: CallbackQuery):
    """Ban a user."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[-1])
    
    await db.ban_user(user_id, callback.from_user.id, "Banned by admin")
    await callback.answer("✅ User banned successfully.", show_alert=True)
    
    # Refresh user details
    await show_user_details(callback)


@router.callback_query(F.data.startswith("admin_unban_"))
async def unban_user(callback: CallbackQuery):
    """Unban a user."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[-1])
    
    await db.unban_user(user_id)
    await callback.answer("✅ User unbanned successfully.", show_alert=True)
    
    # Refresh user details
    await show_user_details(callback)


@router.callback_query(F.data.startswith("admin_delete_user_"))
async def confirm_delete_user(callback: CallbackQuery):
    """Confirm user deletion."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[-1])
    
    text = f"⚠️ **Confirm Deletion**\n\nAre you sure you want to delete user `{user_id}`?\nThis action cannot be undone!"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_keyboard("delete_user", user_id),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm_delete_user_"))
async def execute_delete_user(callback: CallbackQuery):
    """Execute user deletion."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[-1])
    
    await db.delete_user(user_id)
    await callback.answer("✅ User deleted successfully.", show_alert=True)
    
    # Return to user list
    await show_users(callback)


# Challenge Management
@router.callback_query(F.data.startswith("admin_challenges"))
async def show_challenges(callback: CallbackQuery):
    """Show challenge list with pagination."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    # Parse page number
    page = 0
    if "_page_" in callback.data:
        page = int(callback.data.split("_")[-1])
    
    limit = 10
    offset = page * limit
    
    challenges = await db.get_all_challenges(limit=limit + 1, offset=offset)
    has_next = len(challenges) > limit
    challenges = challenges[:limit]
    
    if not challenges:
        text = "💻 **Challenge Management**\n\nNo challenges found."
    else:
        text = f"💻 **Challenge Management** (Page {page + 1})\n\n"
        for ch in challenges:
            diff_emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}.get(ch['difficulty'].lower(), '⚪')
            text += f"{diff_emoji} **#{ch['id']}** - {ch['title']}\n"
            text += f"   {ch['language']} | {ch['points']} pts\n\n"
    
    await callback.message.edit_text(
        text.strip(),
        reply_markup=get_admin_challenges_keyboard(page, has_next),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_challenge")
async def start_add_challenge(callback: CallbackQuery, state: FSMContext):
    """Start challenge creation process."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ **Add New Challenge**\n\nSend the challenge title:",
        parse_mode='Markdown'
    )
    await state.set_state(AdminStates.waiting_for_challenge_title)
    await callback.answer()


@router.message(AdminStates.waiting_for_challenge_title)
async def process_challenge_title(message: Message, state: FSMContext):
    """Process challenge title."""
    if not is_admin(message.from_user.id):
        return
    
    await state.update_data(title=message.text.strip())
    await message.answer("Send the challenge description:")
    await state.set_state(AdminStates.waiting_for_challenge_description)


@router.message(AdminStates.waiting_for_challenge_description)
async def process_challenge_description(message: Message, state: FSMContext):
    """Process challenge description."""
    if not is_admin(message.from_user.id):
        return
    
    await state.update_data(description=message.text.strip())
    await message.answer("Send the difficulty (easy/medium/hard):")
    await state.set_state(AdminStates.waiting_for_challenge_difficulty)


@router.message(AdminStates.waiting_for_challenge_difficulty)
async def process_challenge_difficulty(message: Message, state: FSMContext):
    """Process challenge difficulty."""
    if not is_admin(message.from_user.id):
        return
    
    difficulty = message.text.strip().lower()
    if difficulty not in ['easy', 'medium', 'hard']:
        await message.answer("❌ Invalid difficulty. Please send: easy, medium, or hard")
        return
    
    await state.update_data(difficulty=difficulty)
    await message.answer("Send the programming language (python/javascript/cpp):")
    await state.set_state(AdminStates.waiting_for_challenge_language)


@router.message(AdminStates.waiting_for_challenge_language)
async def process_challenge_language(message: Message, state: FSMContext):
    """Process challenge language."""
    if not is_admin(message.from_user.id):
        return
    
    language = message.text.strip().lower()
    if language not in ['python', 'javascript', 'cpp']:
        await message.answer("❌ Invalid language. Please send: python, javascript, or cpp")
        return
    
    await state.update_data(language=language)
    await message.answer("Send the test cases (JSON format):")
    await state.set_state(AdminStates.waiting_for_challenge_test_cases)


@router.message(AdminStates.waiting_for_challenge_test_cases)
async def process_challenge_test_cases(message: Message, state: FSMContext):
    """Process challenge test cases."""
    if not is_admin(message.from_user.id):
        return
    
    test_cases = message.text.strip()
    # Validate JSON
    try:
        json.loads(test_cases)
    except json.JSONDecodeError:
        await message.answer("❌ Invalid JSON format. Please send valid JSON test cases.")
        return
    
    await state.update_data(test_cases=test_cases)
    await message.answer("Send the solution code (optional, send 'skip' to skip):")
    await state.set_state(AdminStates.waiting_for_challenge_solution)


@router.message(AdminStates.waiting_for_challenge_solution)
async def process_challenge_solution(message: Message, state: FSMContext):
    """Process challenge solution."""
    if not is_admin(message.from_user.id):
        return
    
    solution = message.text.strip() if message.text.strip().lower() != 'skip' else ""
    await state.update_data(solution=solution)
    await message.answer("Send the points value:")
    await state.set_state(AdminStates.waiting_for_challenge_points)


@router.message(AdminStates.waiting_for_challenge_points)
async def process_challenge_points(message: Message, state: FSMContext):
    """Process challenge points and create challenge."""
    if not is_admin(message.from_user.id):
        return
    
    try:
        points = int(message.text.strip())
        if points <= 0:
            await message.answer("❌ Points must be positive.")
            return
    except ValueError:
        await message.answer("❌ Invalid number. Please send a valid points value.")
        return
    
    # Get all data and create challenge
    data = await state.get_data()
    
    challenge_id = await db.add_challenge(
        title=data['title'],
        description=data['description'],
        difficulty=data['difficulty'],
        language=data['language'],
        test_cases=data['test_cases'],
        solution=data.get('solution', ''),
        points=points
    )
    
    await message.answer(
        f"✅ Challenge created successfully!\nChallenge ID: {challenge_id}",
        reply_markup=get_admin_challenges_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin_delete_challenge_"))
async def confirm_delete_challenge(callback: CallbackQuery):
    """Confirm challenge deletion."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    challenge_id = int(callback.data.split("_")[-1])
    
    text = f"⚠️ **Confirm Deletion**\n\nAre you sure you want to delete challenge #{challenge_id}?\nThis will also delete all related submissions!"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_keyboard("delete_challenge", challenge_id),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm_delete_challenge_"))
async def execute_delete_challenge(callback: CallbackQuery):
    """Execute challenge deletion."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    challenge_id = int(callback.data.split("_")[-1])
    
    await db.delete_challenge(challenge_id)
    await callback.answer("✅ Challenge deleted successfully.", show_alert=True)
    
    # Return to challenge list
    await show_challenges(callback)


# Broadcast
@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    """Start broadcast message composition."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 **Broadcast Message**\n\nSend the message you want to broadcast to all users:\n\n(Markdown formatting supported)",
        parse_mode='Markdown'
    )
    await state.set_state(AdminStates.waiting_for_broadcast_message)
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Process and send broadcast message."""
    if not is_admin(message.from_user.id):
        return
    
    broadcast_text = message.text.strip()
    
    # Preview
    preview_text = f"📢 **Broadcast Preview:**\n\n{broadcast_text}\n\n---\nSend to all users?"
    
    await state.update_data(broadcast_text=broadcast_text)
    await message.answer(preview_text, reply_markup=get_broadcast_keyboard(), parse_mode='Markdown')


@router.callback_query(F.data == "admin_broadcast_confirm")
async def execute_broadcast(callback: CallbackQuery, state: FSMContext):
    """Execute broadcast to all users."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    data = await state.get_data()
    broadcast_text = data.get('broadcast_text')
    
    if not broadcast_text:
        await callback.answer("❌ No message to broadcast.", show_alert=True)
        return
    
    await callback.message.edit_text("📤 Broadcasting message... Please wait.")
    
    # Send broadcast
    result = await broadcast_message(callback.bot, db, broadcast_text, exclude_banned=True)
    
    result_text = f"""
✅ **Broadcast Complete**

📊 Results:
• Sent: {result['success']}
• Failed: {result['failed']}
"""
    
    await callback.message.edit_text(result_text.strip(), reply_markup=get_admin_menu(), parse_mode='Markdown')
    await state.clear()
    await callback.answer()


# Interview Questions Management
@router.callback_query(F.data.startswith("admin_interview"))
async def show_interview_questions(callback: CallbackQuery):
    """Show interview questions list."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    # Parse page number
    page = 0
    if "_page_" in callback.data:
        page = int(callback.data.split("_")[-1])
    
    limit = 10
    offset = page * limit
    
    questions = await db.get_all_interview_questions(limit=limit + 1, offset=offset)
    has_next = len(questions) > limit
    questions = questions[:limit]
    
    if not questions:
        text = "🎯 **Interview Questions Management**\n\nNo questions found."
    else:
        text = f"🎯 **Interview Questions** (Page {page + 1})\n\n"
        for q in questions:
            diff_emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}.get(q['difficulty'].lower(), '⚪')
            text += f"{diff_emoji} **#{q['id']}** - {q['category']}\n"
            text += f"   {q['question'][:50]}...\n\n"
    
    await callback.message.edit_text(
        text.strip(),
        reply_markup=get_admin_interview_keyboard(page, has_next),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_interview_question")
async def start_add_interview_question(callback: CallbackQuery, state: FSMContext):
    """Start interview question creation."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ **Add Interview Question**\n\nSend the category (e.g., algorithms, data_structures, system_design, oop):",
        parse_mode='Markdown'
    )
    await state.set_state(AdminStates.waiting_for_interview_category)
    await callback.answer()


@router.message(AdminStates.waiting_for_interview_category)
async def process_interview_category(message: Message, state: FSMContext):
    """Process interview question category."""
    if not is_admin(message.from_user.id):
        return
    
    await state.update_data(category=message.text.strip())
    await message.answer("Send the question:")
    await state.set_state(AdminStates.waiting_for_interview_question)


@router.message(AdminStates.waiting_for_interview_question)
async def process_interview_question(message: Message, state: FSMContext):
    """Process interview question text."""
    if not is_admin(message.from_user.id):
        return
    
    await state.update_data(question=message.text.strip())
    await message.answer("Send the answer:")
    await state.set_state(AdminStates.waiting_for_interview_answer)


@router.message(AdminStates.waiting_for_interview_answer)
async def process_interview_answer(message: Message, state: FSMContext):
    """Process interview question answer."""
    if not is_admin(message.from_user.id):
        return
    
    await state.update_data(answer=message.text.strip())
    await message.answer("Send the difficulty (easy/medium/hard):")
    await state.set_state(AdminStates.waiting_for_interview_difficulty)


@router.message(AdminStates.waiting_for_interview_difficulty)
async def process_interview_difficulty(message: Message, state: FSMContext):
    """Process interview question difficulty and create question."""
    if not is_admin(message.from_user.id):
        return
    
    difficulty = message.text.strip().lower()
    if difficulty not in ['easy', 'medium', 'hard']:
        await message.answer("❌ Invalid difficulty. Please send: easy, medium, or hard")
        return
    
    # Get all data and create question
    data = await state.get_data()
    
    question_id = await db.add_interview_question(
        category=data['category'],
        question=data['question'],
        answer=data['answer'],
        difficulty=difficulty
    )
    
    await message.answer(
        f"✅ Interview question created successfully!\nQuestion ID: {question_id}",
        reply_markup=get_admin_interview_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin_delete_interview_"))
async def confirm_delete_interview_question(callback: CallbackQuery):
    """Confirm interview question deletion."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    question_id = int(callback.data.split("_")[-1])
    
    text = f"⚠️ **Confirm Deletion**\n\nAre you sure you want to delete interview question #{question_id}?"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_keyboard("delete_interview", question_id),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm_delete_interview_"))
async def execute_delete_interview_question(callback: CallbackQuery):
    """Execute interview question deletion."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    question_id = int(callback.data.split("_")[-1])
    
    await db.delete_interview_question(question_id)
    await callback.answer("✅ Interview question deleted successfully.", show_alert=True)
    
    # Return to question list
    await show_interview_questions(callback)
