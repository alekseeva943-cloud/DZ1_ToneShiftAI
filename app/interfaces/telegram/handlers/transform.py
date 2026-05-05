# Обработчик текста пользователя
# Этот файл отвечает за:
# - получение текста от пользователя
# - проверку сценария (выбрана ли цель)
# - вызов AI-движка
# - отправку результата обратно в Telegram

# Wizard-обработчик (пошаговый ввод данных)

# Обработчик текста пользователя (wizard + защита от мусора)

from telegram import Update
from telegram.ext import ContextTypes

import logging

from app.config.texts import (
    TEXT_NEED_MODE,
    TEXT_TOO_SHORT,
    TEXT_ERROR,
    TEXT_STEP_GOAL,
    TEXT_STEP_AUDIENCE,
    TEXT_STEP_TONE,
    TEXT_STEP_FORMALITY,
    TEXT_STEP_LENGTH,
    TEXT_STEP_SIMPLIFY,
)

from app.interfaces.telegram.keyboards.options import skip_kb

from app.core.models import TransformRequest
from app.core.prompt_builder import PromptBuilder
from app.services.llm_client import LLMClient
from app.core.ai_engine import AIEngine


logger = logging.getLogger(__name__)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[HANDLE_TEXT] RAW UPDATE: {update}")
    # ------------------------------
    # 🔥 защита от НЕ текста
    # ------------------------------
    if not update.message or not update.message.text:
        await update.message.reply_text("Пожалуйста, отправь текст 🙂")
        return

    user_text = update.message.text.strip()

    # ------------------------------
    # 🔥 защита от пустого текста
    # ------------------------------
    if not user_text:
        await update.message.reply_text("Текст пустой 🙂")
        return

    step = context.user_data.get("step")

    logger.info(f"STEP: {step} | TEXT: {user_text}")

    # ------------------------------
    # 🔹 ШАГ 1 — текст
    # ------------------------------
    if step is None:
        context.user_data["text"] = user_text
        context.user_data["step"] = "goal"

        await update.message.reply_text(TEXT_STEP_GOAL)
        return
        logger.info(f"[HANDLE_TEXT] TEXT: {user_text}")
        logger.info(f"[HANDLE_TEXT] STEP: {step}")

    # ------------------------------
    # 🔹 ШАГ 2 — цель
    # ------------------------------
    elif step == "goal":
        context.user_data["goal"] = user_text
        context.user_data["step"] = "audience"

        await update.message.reply_text(TEXT_STEP_AUDIENCE)
        return

    # ------------------------------
    # 🔹 ШАГ 3 — аудитория
    # ------------------------------
    elif step == "audience":
        context.user_data["audience"] = user_text
        context.user_data["step"] = "tone"

        await update.message.reply_text(TEXT_STEP_TONE)
        return

    # ------------------------------
    # 🔹 ШАГ 4 — тон
    # ------------------------------
    elif step == "tone":
        context.user_data["tone"] = user_text
        context.user_data["step"] = "formality"

        await update.message.reply_text(
            TEXT_STEP_FORMALITY,
            reply_markup=skip_kb("formality")
        )
        return

    # ------------------------------
    # 🔹 ШАГ 5 — формальность
    # ------------------------------
    elif step == "formality":
        context.user_data["formality"] = user_text
        context.user_data["step"] = "length"

        await update.message.reply_text(
            TEXT_STEP_LENGTH,
            reply_markup=skip_kb("length")
        )
        return

    # ------------------------------
    # 🔹 ШАГ 6 — длина
    # ------------------------------
    elif step == "length":
        context.user_data["length"] = user_text
        context.user_data["step"] = "simplify"

        await update.message.reply_text(
            TEXT_STEP_SIMPLIFY,
            reply_markup=skip_kb("simplify")
        )
        return

    # ------------------------------
    # 🔹 ШАГ 7 — simplify
    # ------------------------------
    elif step == "simplify":
        context.user_data["simplify"] = user_text

        await process_ai(update.message, context)
        return


# ------------------------------
# 🚀 AI обработка
# ------------------------------
async def process_ai(message, context):
    try:
        data = context.user_data

        logger.info(f"PROCESS AI: {data}")

        request = TransformRequest(
            text=data["text"],
            goal=data["goal"],
            audience=data["audience"],
            tone=data["tone"],
        )

        prompt_builder = PromptBuilder()
        llm_client = LLMClient()
        engine = AIEngine(prompt_builder, llm_client)

        response = engine.transform(request)

        await message.reply_text(response.adapted_text)

        context.user_data.clear()

    except Exception as e:
        logger.error(f"AI ERROR: {e}")
        await message.reply_text(TEXT_ERROR)
