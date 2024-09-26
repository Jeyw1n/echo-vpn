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
    return ReplyKeyboardMarkup(keyboard=[buttons_row], resize_keyboard=True)