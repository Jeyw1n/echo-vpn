from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery

from loguru import logger

from aiogram_bot.markups import choose_month_count

import database

payment_router = Router(name=__name__)


@payment_router.callback_query(F.data.startswith('pay_key_'))
async def handle_pay_key_cb(callback_query: CallbackQuery):
    key = callback_query.data.split('_')[2]

    await callback_query.answer()
    # Отправляем сообщение с текстом и клавиатурой
    await callback_query.message.answer(text=f'Выберите, на сколько хотите оплатить ключ *{key}*: ⌛\n_Доступные варианты:_',
                                        reply_markup=choose_month_count(key=key))
    # await callback_query.message.delete()


@payment_router.callback_query(F.data.startswith('month_'))
async def handle_month_selection(callback_query: CallbackQuery):
    month_data = callback_query.data.split('_')
    month = int(month_data[1])   # Получаем номер месяца
    key = month_data[2]          # Получаем ключ

    try:
        key_is_new = (key == 'new')
        key_exists = False
        if not key_is_new:
            key_exists = database.key_exists(int(key))  # Проверяем, существует ли ключ
    except Exception as ex:
        logger.error(ex)
        await callback_query.answer('Ошибка при проверке ключа!')
        return

    # Проверяем условия
    if month not in [1, 2, 3] or (not key_is_new and not key_exists):
        logger.error(f'Callback ошибка при отправке месяца и ключа! (month:{month}) (key:{key})')
        await callback_query.answer('Ошибка! Переданы неверные данные!')
        return


    await callback_query.answer()
    month_word = 'месяц' if month == 1 else 'месяца'
    await callback_query.message.answer(text=f'Вы выбрали оплату за *{month} {month_word}* для ключа: *{key}* ✅')
    await callback_query.message.delete()
