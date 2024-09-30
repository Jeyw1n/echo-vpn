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

import database

from aiogram_bot.markups import pay_new_markup, pay_exist_markup
from aiogram_bot.texts_loader import texts

menu_router = Router(name=__name__)

photo_2 = FSInputFile('media/guide_2.png')
photo_3 = FSInputFile('media/guide_3.png')
photo_4 = FSInputFile('media/guide_4.png')
photo_support = FSInputFile('media/support.png')


@menu_router.message(F.text == '📖 Инструкция')
async def instruction(msg: Message) -> None:
    await msg.answer(texts['guide_1'], parse_mode='Markdown', disable_web_page_preview=True)
    await msg.answer_photo(photo=photo_2, caption=texts['guide_2'])
    await msg.answer_photo(photo=photo_3, caption=texts['guide_3'])
    await msg.answer_photo(photo=photo_4, caption=texts['guide_4'])


@menu_router.message(F.text == '🔑 Ключи')
async def show_keys(msg: Message) -> None:
    keys = database.get_user_keys(msg.from_user.id)
    # Если ключи есть, то выводим их
    if keys:
        keys_count = len(keys)
        keys_word = 'ключ' if keys_count == 1 else 'ключа' if keys_count < 5 else 'ключей'
        # Если все-таки ключи есть
        await msg.answer(f'У вас {len(keys)} {keys_word}. 🔑\n*Список всех ваших ключей:*')
        for key in keys:
            remaining_time = database.get_remaining_time(key.key_id)
            await msg.answer(f'*Сервер:* VendekVPN ► Netherlands 🇳🇱\n'
                             f'Ваш ключ: _#{key.key_id}_\n'
                             f'Истекает через: _{remaining_time}_'
                             f'```{key.access_url + texts['connection_name']}```',
                             reply_markup=pay_exist_markup(key.key_id))
    # Кнопка покупки нового ключа
    await msg.answer(text='Вы можете купить новый ключ:', reply_markup=pay_new_markup())
    return


@menu_router.message(F.text == '💬 Поддержка')
async def support(msg: Message) -> None:
    await msg.answer_photo(photo=photo_support, caption=texts['support_message'])


@menu_router.message(F.text == 'ℹ️ Инфо')
async def info(msg: Message) -> None:
    await msg.answer(texts['about'])


@menu_router.message(F.text == '🤝 Рефералы')
async def info(msg: Message) -> None:
    await msg.answer(f'Пока-что в разработке, но ваши приглашения засчитываются.\n'
                     f'Ваша ссылка-приглашение:\nhttps://t.me/vendek\_vpn\_bot/?start={msg.from_user.id}')
