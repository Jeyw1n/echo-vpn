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

start_router = Router(name=__name__)


@start_router.message(Command('start'))
async def start_command(msg: Message) -> None:
    user_id: int = msg.from_user.id
    user_exists: bool = database.user_exists(user_id)

    # Сработает, если пользователь является новым
    if not user_exists:
        # Ищем referrer ID и сохраняем его в БД к новому пользователю, если referrer ID существует
        referrer_id = msg.text[7:]
        if referrer_id != '' and referrer_id != str(msg.from_user.id):
            database.add_user(user_id, referrer_id)
            await msg.bot.send_message(chat_id=referrer_id,
                                       text=f'Пользователь @{msg.from_user.username} перешел по вашей ссылке! 🎉')
        else:
            database.add_user(user_id)

        # Пользователь новый, поэтому даём 10ти дневный доступ
        # и создадим новый ключ.
        expiration_date = datetime.now() + timedelta(days=10)
        database.add_key(user_id, expiration_date)

        await msg.answer(texts['welcome_message'])
        await msg.answer(texts['menu'], reply_markup=menu_keyboard())

    else:
        await msg.answer(f'*Привет, {msg.from_user.first_name}!*\nЧем могу быть полезен сегодня?',
                         reply_markup=menu_keyboard())
        await msg.answer(texts['menu'], reply_markup=menu_keyboard())
