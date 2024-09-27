import sys
from loguru import logger
from decouple import config, UndefinedValueError

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Импорт router'ов
from aiogram_bot.routers import (
    start_router,
    menu_router,
    payment_router
)

try:
    API_TOKEN = config('BOT_TOKEN')
except UndefinedValueError:
    logger.error('Не удалось обнаружить "BOT_TOKEN"! Проверьте конфигурационный файл.')
    sys.exit(1)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

# Регистрация router'ов
dp.include_routers(
    start_router,
    menu_router,
    payment_router
)