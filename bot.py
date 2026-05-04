# Точка запуска Telegram-бота

from app.interfaces.telegram.bot_app import run_bot
from app.config import settings, texts


def main():
    run_bot()


if __name__ == "__main__":
    main()
