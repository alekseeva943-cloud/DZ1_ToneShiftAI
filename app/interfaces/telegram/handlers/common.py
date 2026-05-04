# Обработчик кнопок Telegram

from app.config.texts import TEXT_SEND_TEXT


async def handle_buttons(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "start_transform":
        context.user_data["mode"] = "transform"

        await query.message.reply_text(TEXT_SEND_TEXT)
