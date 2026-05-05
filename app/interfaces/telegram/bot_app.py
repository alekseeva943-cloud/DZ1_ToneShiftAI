# Основное приложение Telegram-бота

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from app.config import settings
from app.interfaces.telegram.handlers.start import start
from app.interfaces.telegram.handlers.transform import handle_text
from app.interfaces.telegram.handlers.common import handle_buttons


import logging

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def run_bot():
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_buttons))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started")

    application.run_polling()
