# Клавиатура главного меню

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb():
    keyboard = [
        [InlineKeyboardButton("📩 Обработать текст",
                              callback_data="start_transform")]
    ]
    return InlineKeyboardMarkup(keyboard)
