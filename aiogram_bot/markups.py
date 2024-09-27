from aiogram.types import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def menu_keyboard() -> ReplyKeyboardMarkup:
    buttons_text: list[str] = ['📖 Инструкция', '🔑 Ключи', 'Рефералы 🤝', '💬 Поддержка', 'ℹ️ Инфо']
    buttons_row: list[KeyboardButton] = [KeyboardButton(text=i) for i in buttons_text]
    return ReplyKeyboardMarkup(keyboard=[buttons_row[:3], buttons_row[3:]], resize_keyboard=True)


def pay_new_markup() -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text='💳 Новый ключ', callback_data=f'pay_key_new')
    return InlineKeyboardMarkup(inline_keyboard=[[button]])

def pay_exist_markup(key: str) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text='💳 Продлить', callback_data=f'pay_key_{key}')
    return InlineKeyboardMarkup(inline_keyboard=[[button]])

def choose_month_count(key: str) -> InlineKeyboardMarkup:
    one_month = InlineKeyboardButton(text='1 месяц', callback_data=f'month_1_{key}')
    two_months = InlineKeyboardButton(text='2 месяца', callback_data=f'month_2_{key}')
    three_months = InlineKeyboardButton(text='3 месяца', callback_data=f'month_3_{key}')
    return InlineKeyboardMarkup(inline_keyboard=[[one_month, two_months], [three_months]])