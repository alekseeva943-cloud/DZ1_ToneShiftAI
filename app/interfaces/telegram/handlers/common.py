# Обработчик кнопок Telegram
# Отвечает за:
# - старт wizard
# - пропуск опциональных шагов
# - управление состоянием пользователя

from app.config.texts import (
    TEXT_SEND_TEXT,
    TEXT_STEP_LENGTH,
    TEXT_STEP_SIMPLIFY,
)

from app.interfaces.telegram.keyboards.options import skip_kb
from app.interfaces.telegram.handlers.transform import process_ai


async def handle_buttons(update, context):
    query = update.callback_query
    await query.answer()

    print(f"[BUTTON CLICK] {query.data}")
    print(f"[STATE BEFORE] {context.user_data}")

    # -------------------------------------------------
    # 🔹 СТАРТ wizard
    # -------------------------------------------------
    if query.data == "start_transform":
        context.user_data.clear()

        # 🔥 первый шаг — ввод текста
        context.user_data["step"] = None

        # ❗ используем edit_text чтобы не было дублей
        await query.message.edit_text(TEXT_SEND_TEXT)

    # -------------------------------------------------
    # 🔹 SKIP — обработка "Пропустить"
    # -------------------------------------------------
    elif query.data.startswith("skip_"):
        step = query.data.replace("skip_", "")

        # сохраняем None
        context.user_data[step] = None

        print(f"[SKIP] {step}")

        # ----- пропуск формальности -----
        if step == "formality":
            context.user_data["step"] = "length"

            await query.message.reply_text(
                TEXT_STEP_LENGTH,
                reply_markup=skip_kb("length")
            )

        # ----- пропуск длины -----
        elif step == "length":
            context.user_data["step"] = "simplify"

            await query.message.reply_text(
                TEXT_STEP_SIMPLIFY,
                reply_markup=skip_kb("simplify")
            )

        # ----- пропуск simplify → запуск AI -----
        elif step == "simplify":
            print("[PROCESS AI FROM SKIP]")
            await process_ai(query.message, context)

    print(f"[STATE AFTER] {context.user_data}")
