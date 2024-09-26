from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputFile,
    FSInputFile
)

from loguru import logger
from decouple import config, UndefinedValueError
import yaml
import database
from datetime import datetime, timedelta
import sys

import utils
import database

from aiogram_bot.markups import menu_keyboard
from aiogram_bot.texts_loader import texts

menu_router = Router()

photo_2 = FSInputFile('media/guide_2.png')
photo_3 = FSInputFile('media/guide_3.png')
photo_4 = FSInputFile('media/guide_4.png')
photo_support = FSInputFile('media/support.png')


@menu_router.message(F.text == "📖 Инструкция")
async def instruction(msg: Message):
    await msg.answer(texts['guide_1'], parse_mode='Markdown', disable_web_page_preview=True)
    await msg.answer_photo(photo=photo_2, caption=texts['guide_2'])
    await msg.answer_photo(photo=photo_3, caption=texts['guide_3'])
    await msg.answer_photo(photo=photo_4, caption=texts['guide_4'])


@menu_router.message(F.text == "🔑 Ключи")
async def show_keys(msg: Message):
    keys = database.get_user_keys(msg.from_user.id)
    if not keys:
        # Добавить кнопку "💳 Оплата"
        await msg.answer("У вас нет ключей. Необходимо произвести оплату.")
    for key in keys:
        remaining_time = database.get_remaining_time(key.key_id)
        formatted_time = utils.format_remaining_time(remaining_time)
        await msg.answer(f"*Сервер:* VendekVPN ► Netherlands 🇳🇱\n\n"
                         f"Ваш ключ: _#{key.key_id}_\n"
                         f"Истекает через: _{formatted_time}_"
                         f"```{key.access_url + texts['connection_name']}```")


@menu_router.message(F.text == "💬 Поддержка")
async def support(msg: Message):
    await msg.answer_photo(photo=photo_support, caption=texts['support_message'])


@menu_router.message(F.text == "ℹ️ Инфо")
async def info(msg: Message):
    await msg.answer(texts['about'])
