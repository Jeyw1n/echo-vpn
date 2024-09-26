from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from loguru import logger
from decouple import config, UndefinedValueError
import yaml
import database
from datetime import datetime, timedelta
import sys

from aiogram_bot.markups import menu_keyboard
from aiogram_bot.texts_loader import texts

start_router = Router()


@start_router.message(Command('start'))
async def start_command(msg: Message) -> None:
    user_id: int = msg.from_user.id
    # Сохраняем пользователя в базу данных, если его еще там нет.
    # Сохраняем это в db_save_result (True - сохранился, False - уже есть в БД)
    db_save_result: bool = database.add_user(user_id)

    if db_save_result:
        # Если пользователь новый, то даём 10ти дневный доступ.
        expiration_date = datetime.now() + timedelta(days=10)
        database.add_key(user_id, expiration_date)

        await msg.answer(texts['welcome_message'])
        await msg.answer(texts['menu'], reply_markup=menu_keyboard())

    else:
        await msg.answer(f'*Привет, {msg.from_user.first_name}!*\nЧем могу быть полезен сегодня?', reply_markup=menu_keyboard())
        await msg.answer(texts['menu'], reply_markup=menu_keyboard())
