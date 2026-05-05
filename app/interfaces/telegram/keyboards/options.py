# Клавиатура выбора цели текста

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def goal_kb():
    keyboard = [
        [InlineKeyboardButton("📚 Объяснить", callback_data="goal_explain")],
        [InlineKeyboardButton("💰 Продать", callback_data="goal_sell")],
        [InlineKeyboardButton("✍️ Переписать", callback_data="goal_rewrite")],
    ]
    return InlineKeyboardMarkup(keyboard)


def skip_kb(step: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Пропустить", callback_data=f"skip_{step}")]
    ])
