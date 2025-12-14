import asyncio
import logging
from aiogram import Bot, Dispatcher

from bot.handlers import router

from config.settings import settings

dp = Dispatcher()
dp.include_router(router)

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not settings.BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения!")

    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    