from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from loguru import logger

from aiogram_bot.markups import choose_month_count
import database
from paymaster import create_payment
import config as conf

payment_router = Router(name=__name__)


def key_check(key: str) -> tuple[bool, bool]:
    """
    Проверяет ключ, что он новый, либо существующий.
    :param key: Ключ, полученный из callback data.
    :return: Кортеж булевых значений. Новый ли ключ и существует ли ключ.
    """
    try:
        key_is_new = (key == 'new')
        key_exists = False
        if not key_is_new:
            key_exists = database.key_exists(int(key))  # Проверяем, существует ли ключ
        return key_is_new, key_exists
    except Exception as ex:
        logger.error(ex)
        return False, False


@payment_router.callback_query(F.data.startswith('pay_key_'))
async def handle_pay_key_cb(callback_query: CallbackQuery):
    key = callback_query.data.split('_')[2]

    await callback_query.answer()
    if key == 'new':
        await callback_query.message.delete()
    # Отправляем сообщение с текстом и клавиатурой
    await callback_query.message.answer(
        text=f'Выберите, на сколько хотите оплатить ключ*{'' if key == 'new' else ' #' + key}*: ⌛\n_Доступные варианты:_',
        reply_markup=choose_month_count(key=key))


@payment_router.callback_query(F.data.startswith('month_'))
async def handle_month_selection(callback_query: CallbackQuery):
    month_data = callback_query.data.split('_')
    month = int(month_data[1])  # Получаем номер месяца
    key = month_data[2]  # Получаем ключ
    month_word = 'месяц' if month == 1 else 'месяца'  # Формы слова 'месяц'
    key_is_new, key_exists = key_check(key)

    # Проверяем условия
    if month not in [1, 2, 3] or (not key_is_new and not key_exists):
        logger.error(f'Callback ошибка при отправке месяца и ключа! (month:{month}) (key:{key})')
        await callback_query.answer('Ошибка! Переданы неверные данные!')
        return

    # Рассчитываем сумму платежа
    amount = month * conf.MONTH_PRICE
    description = f'Оплата за {month} {month_word} для ключа {'' if key == 'new' else '#' + key} | VendekNET'

    try:
        # Создаем платеж
        confirmation_url, payment_id = create_payment(amount=amount,description=description)

        # Создаем новую транзакцию в БД
        transaction_created = database.create_transaction(
            payment_id=payment_id,
            telegram_id=str(callback_query.from_user.id),
            message_id=str(callback_query.message.message_id),
            key_id=key,
            months=month
        )
        if not transaction_created:
            await callback_query.answer('Ошибка при создании транзакции!')
            logger.error(f'Ошибка при создании транзакции {payment_id}')
            return

        await callback_query.answer()
        await callback_query.message.delete()

        payment_message = (
            f'💳 Для активации ключа*{'' if key == 'new' else ' #' + key}* на {month} {month_word}, '
            f'необходимо произвести оплату в размере *{int(amount)}₽*.\n\n'
            f'⏳ Пожалуйста, оплатите в течение *10 минут*.\n\n'
            f'🔗 Для оплаты нажмите на кнопку ниже:'
        )
        button = InlineKeyboardButton(text='Оплатить', url=confirmation_url)
        await callback_query.message.answer(text=payment_message,
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[button]]))
    except Exception as e:
        await callback_query.answer('Ошибка при создании платежа!')
        logger.error(e)
