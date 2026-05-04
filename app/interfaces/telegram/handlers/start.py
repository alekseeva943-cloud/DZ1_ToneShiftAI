# Обработчик команды /start

from app.config.texts import TEXT_GREETING
from app.interfaces.telegram.keyboards.main_menu import main_menu_kb


async def start(update, context):
    await update.message.reply_text(
        TEXT_GREETING,
        reply_markup=main_menu_kb()
    )
