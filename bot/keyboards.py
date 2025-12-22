"""Keyboard layouts for the bot."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional

from bot.utils.admin_utils import is_admin


def get_main_menu(user_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Get main menu keyboard with optional admin button."""
    buttons = [
        [InlineKeyboardButton(text="📝 Daily Challenge", callback_data="daily_challenge")],
        [InlineKeyboardButton(text="💻 Submit Code", callback_data="submit_code")],
        [InlineKeyboardButton(text="🎯 Interview Prep", callback_data="interview_prep")],
        [
            InlineKeyboardButton(text="👤 Profile", callback_data="profile"),
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")
        ]
    ]
    
    # Add admin panel button only for admins
    if user_id is not None and is_admin(user_id):
        buttons.append([InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_difficulty_keyboard() -> InlineKeyboardMarkup:
    """Get difficulty selection keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Easy", callback_data="difficulty_easy")],
        [InlineKeyboardButton(text="🟡 Medium", callback_data="difficulty_medium")],
        [InlineKeyboardButton(text="🔴 Hard", callback_data="difficulty_hard")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ])
    return keyboard


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get programming language selection keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐍 Python", callback_data="lang_python")],
        [InlineKeyboardButton(text="📜 JavaScript", callback_data="lang_javascript")],
        [InlineKeyboardButton(text="⚙️ C++", callback_data="lang_cpp")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ])
    return keyboard


def get_interview_categories_keyboard() -> InlineKeyboardMarkup:
    """Get interview categories keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔢 Algorithms", callback_data="interview_algorithms")],
        [InlineKeyboardButton(text="📊 Data Structures", callback_data="interview_data_structures")],
        [InlineKeyboardButton(text="🏗️ System Design", callback_data="interview_system_design")],
        [InlineKeyboardButton(text="🎨 OOP", callback_data="interview_oop")],
        [InlineKeyboardButton(text="🎲 Random Question", callback_data="interview_random")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ])
    return keyboard


def get_challenge_actions_keyboard(challenge_id: int) -> InlineKeyboardMarkup:
    """Get challenge action buttons."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Submit Solution", callback_data=f"submit_solution_{challenge_id}")],
        [InlineKeyboardButton(text="💡 Get Hint", callback_data=f"hint_{challenge_id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ])
    return keyboard


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Get simple back to menu keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Main Menu", callback_data="main_menu")]
    ])
    return keyboard


def get_leaderboard_keyboard() -> InlineKeyboardMarkup:
    """Get leaderboard navigation keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔝 Top 10", callback_data="leaderboard_10"),
            InlineKeyboardButton(text="📊 Top 50", callback_data="leaderboard_50")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ])
    return keyboard


def get_submission_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection for code submission."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐍 Python", callback_data="submit_lang_python")],
        [InlineKeyboardButton(text="📜 JavaScript", callback_data="submit_lang_javascript")],
        [InlineKeyboardButton(text="⚙️ C++", callback_data="submit_lang_cpp")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    return keyboard


# Admin keyboards
def get_admin_menu() -> InlineKeyboardMarkup:
    """Get admin panel main menu."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton(text="💻 Challenge Management", callback_data="admin_challenges")],
        [InlineKeyboardButton(text="🎯 Interview Questions", callback_data="admin_interview")],
        [InlineKeyboardButton(text="📢 Broadcast Message", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔙 Back to Main Menu", callback_data="main_menu")]
    ])
    return keyboard


def get_admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Get statistics navigation keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📈 Recent Activity", callback_data="admin_recent_activity")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel")]
    ])
    return keyboard


def get_admin_users_keyboard(page: int = 0, has_next: bool = False) -> InlineKeyboardMarkup:
    """Get user management keyboard with pagination."""
    buttons = []
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"admin_users_page_{page-1}"))
    if has_next:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"admin_users_page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.extend([
        [InlineKeyboardButton(text="🔍 Search User", callback_data="admin_search_user")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_user_actions_keyboard(user_id: int, is_banned: bool = False) -> InlineKeyboardMarkup:
    """Get actions keyboard for specific user."""
    buttons = []
    
    if is_banned:
        buttons.append([InlineKeyboardButton(text="✅ Unban User", callback_data=f"admin_unban_{user_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="🚫 Ban User", callback_data=f"admin_ban_{user_id}")])
    
    buttons.extend([
        [InlineKeyboardButton(text="📊 View Details", callback_data=f"admin_user_details_{user_id}")],
        [InlineKeyboardButton(text="🗑️ Delete User", callback_data=f"admin_delete_user_{user_id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_users")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_challenges_keyboard(page: int = 0, has_next: bool = False) -> InlineKeyboardMarkup:
    """Get challenge management keyboard with pagination."""
    buttons = []
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"admin_challenges_page_{page-1}"))
    if has_next:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"admin_challenges_page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.extend([
        [InlineKeyboardButton(text="➕ Add Challenge", callback_data="admin_add_challenge")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_challenge_actions_keyboard(challenge_id: int) -> InlineKeyboardMarkup:
    """Get actions keyboard for specific challenge."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Edit", callback_data=f"admin_edit_challenge_{challenge_id}")],
        [InlineKeyboardButton(text="🗑️ Delete", callback_data=f"admin_delete_challenge_{challenge_id}")],
        [InlineKeyboardButton(text="👁️ Preview", callback_data=f"admin_preview_challenge_{challenge_id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_challenges")]
    ])
    return keyboard


def get_admin_interview_keyboard(page: int = 0, has_next: bool = False) -> InlineKeyboardMarkup:
    """Get interview questions management keyboard."""
    buttons = []
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"admin_interview_page_{page-1}"))
    if has_next:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"admin_interview_page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.extend([
        [InlineKeyboardButton(text="➕ Add Question", callback_data="admin_add_interview_question")],
        [InlineKeyboardButton(text="🔍 Filter by Category", callback_data="admin_interview_filter")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_interview_question_actions_keyboard(question_id: int) -> InlineKeyboardMarkup:
    """Get actions keyboard for specific interview question."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Edit", callback_data=f"admin_edit_interview_{question_id}")],
        [InlineKeyboardButton(text="🗑️ Delete", callback_data=f"admin_delete_interview_{question_id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_interview")]
    ])
    return keyboard


def get_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Get broadcast options keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Send to All Users", callback_data="admin_broadcast_confirm")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_panel")]
    ])
    return keyboard


def get_confirm_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Get confirmation keyboard for destructive actions."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Confirm", callback_data=f"admin_confirm_{action}_{item_id}"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="admin_panel")
        ]
    ])
    return keyboard
