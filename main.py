import asyncio
from loguru import logger
from aiogram_bot import bot, dp


async def main():
    logger.info("Бот успешно запущен!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('Бот остановлен.')
