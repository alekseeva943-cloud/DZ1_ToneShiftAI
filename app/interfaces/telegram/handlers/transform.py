# -------------------------------------------------
# 📩 ОБРАБОТЧИК ТЕКСТА (WIZARD)
# -------------------------------------------------
# Этот файл отвечает за:
# - пошаговый ввод данных (text → goal → audience → tone → ...)
# - защиту от мусора (пустые сообщения, не текст)
# - запуск AI
# - отправку результата
# -------------------------------------------------

from telegram import Update
from telegram.ext import ContextTypes

import logging

from app.config.texts import (
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


# -------------------------------------------------
# 🧠 ОСНОВНОЙ ОБРАБОТЧИК ТЕКСТА
# -------------------------------------------------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info(f"[HANDLE_TEXT] UPDATE: {update}")

    # 🔹 защита от НЕ текста
    if not update.message or not update.message.text:
        await update.message.reply_text("Пожалуйста, отправь текст 🙂")
        return

    user_text = update.message.text.strip()

    # 🔹 защита от пустого текста
    if not user_text:
        await update.message.reply_text("Текст пустой 🙂")
        return

    step = context.user_data.get("step")

    logger.info(f"[HANDLE_TEXT] STEP: {step} | TEXT: {user_text}")

    # ------------------------------
    # 🔹 ШАГ 1 — текст
    # ------------------------------
    if step is None:
        context.user_data["text"] = user_text
        context.user_data["step"] = "goal"

        await update.message.reply_text(TEXT_STEP_GOAL)
        return

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


# -------------------------------------------------
# 🔧 РАЗБИВКА ДЛИННЫХ СООБЩЕНИЙ
# -------------------------------------------------
async def send_long_message(message, text: str):
    MAX_LENGTH = 4000

    for i in range(0, len(text), MAX_LENGTH):
        await message.reply_text(text[i:i + MAX_LENGTH])


# -------------------------------------------------
# 🚀 AI ОБРАБОТКА
# -------------------------------------------------
async def process_ai(message, context):

    # 🔥 статус "думаю"
    processing_msg = await message.reply_text("⏳ Обрабатываю текст...")

    try:
        data = context.user_data
        logger.info(f"[PROCESS AI] DATA: {data}")

        # 🔹 создаем запрос
        request = TransformRequest(
            text=data.get("text"),
            goal=data.get("goal"),
            audience=data.get("audience"),
            tone=data.get("tone"),
            formality=data.get("formality"),
            length=data.get("length"),
            simplify=data.get("simplify"),
        )

        # 🔹 AI
        engine = AIEngine(PromptBuilder(), LLMClient())
        response = engine.transform(request)

        # 🔥 меняем статус
        await processing_msg.edit_text("✅ Готово! Вот результат 👇")

        # ------------------------------
        # 🔹 ОТПРАВКА ПО БЛОКАМ (ВАЖНО)
        # ------------------------------
        await send_long_message(
            message,
            f"🔹 Адаптированный текст:\n\n{response.adapted_text}"
        )

        await send_long_message(
            message,
            f"🔹 Нейтральная версия:\n\n{response.neutral_text}"
        )

        await send_long_message(
            message,
            f"🔹 Оригинал:\n\n{data.get('text')}"
        )

        await send_long_message(
            message,
            f"🔹 Объяснение:\n\n{response.explanation}"
        )

        logger.info("[PROCESS AI] SUCCESS")

        # 🔹 очищаем состояние
        context.user_data.clear()

    except Exception as e:
        print("\n🔥 AI ERROR:", e, "\n")

        import traceback
        traceback.print_exc()

        logger.error(f"[PROCESS AI ERROR] {e}")

        await processing_msg.edit_text("❌ Ошибка обработки")

        await message.reply_text(TEXT_ERROR)
