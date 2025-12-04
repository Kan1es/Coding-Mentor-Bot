"""Keyboard layouts for the bot."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Daily Challenge", callback_data="daily_challenge")],
        [InlineKeyboardButton(text="💻 Submit Code", callback_data="submit_code")],
        [InlineKeyboardButton(text="🎯 Interview Prep", callback_data="interview_prep")],
        [
            InlineKeyboardButton(text="👤 Profile", callback_data="profile"),
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")
        ]
    ])
    return keyboard


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
