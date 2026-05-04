# Обработчик текста пользователя

from telegram import Update
from telegram.ext import ContextTypes

from app.config.texts import TEXT_NEED_MODE, TEXT_TOO_SHORT, TEXT_ERROR

from app.core.models import TransformRequest
from app.core.prompt_builder import PromptBuilder
from app.services.llm_client import LLMClient
from app.core.ai_engine import AIEngine


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Проверка: выбран ли режим
    if context.user_data.get("mode") != "transform":
        await update.message.reply_text(TEXT_NEED_MODE)
        return

    # Проверка: текст нормальный
    if len(user_text.strip()) < 10:
        await update.message.reply_text(TEXT_TOO_SHORT)
        return

    try:
        request = TransformRequest(
            text=user_text,
            goal="объяснить",
            audience="новичок",
            tone="дружелюбный"
        )

        prompt_builder = PromptBuilder()
        llm_client = LLMClient()
        engine = AIEngine(prompt_builder, llm_client)

        response = engine.transform(request)

        await update.message.reply_text(response.adapted_text)

    except Exception as e:
        print(e)
        await update.message.reply_text(TEXT_ERROR)
