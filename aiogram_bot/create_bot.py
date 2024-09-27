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
import config as conf

API_TOKEN = conf.BOT_TOKEN

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

# Регистрация router'ов
dp.include_routers(
    start_router,
    menu_router,
    payment_router
)
