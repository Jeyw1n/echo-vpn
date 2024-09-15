from datetime import datetime, timedelta
import sys

import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup

from loguru import logger
from decouple import config, UndefinedValueError
import yaml

from database import database as db
import utils

try:
    API_TOKEN = config('BOT_TOKEN')
except UndefinedValueError:
    logger.error('Не удалось обнаружить "BOT_TOKEN"! Проверьте конфигурационный файл.')
    sys.exit(1)

bot = telebot.TeleBot(API_TOKEN)


# Функция для загрузки текстов из YAML-файла
def load_texts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# Загрузка текстов
texts = load_texts('texts.yaml')

# Список с текстами для кнопок меню
menu_buttons = ['📖 Инструкция', '🔑 Ключи', '💬 Поддержка', 'ℹ️ Инфо']


def keyboard_create(buttons: list[str]) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру ReplyKeyboardMarkup из списка строк.
    :param buttons: Список кнопок
    :return: Markup клавиатура
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*buttons)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    # Сохраняем пользователя в базу данных, если его еще там нет.
    # Сохраняем это в db_save_result (True - сохранился, False - уже есть в БД)
    db_save_result = db.add_user(user_id)
    # Меню-клавиатура
    markup = keyboard_create(menu_buttons)

    if db_save_result:
        # Если пользователь новый, то даём 10ти дневный доступ.
        expiration_date = datetime.now() + timedelta(days=10)
        db.add_key(user_id, expiration_date)

        bot.send_message(message.chat.id, texts['welcome_message'], parse_mode='Markdown')
        bot.send_message(message.chat.id, texts['menu'], reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'ага да.', reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(commands=['menu'])
def menu(message):
    markup = keyboard_create(menu_buttons)
    bot.send_message(message.chat.id, texts['menu'], reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "📖 Инструкция")
def instruction(message):
    bot.send_message(message.chat.id, "Инструкция по настройке и бла бла бла...")


@bot.message_handler(func=lambda message: message.text == "🔑 Ключи")
def show_keys(message):
    keys = db.get_user_keys(message.from_user.id)
    if not keys:
        bot.send_message(message.chat.id, "Пока ключей нет =(")
    for key in keys:
        remaining_time = db.get_remaining_time(key.key_id)
        formated_time = utils.format_remaining_time(remaining_time)
        bot.send_message(message.chat.id, "*Сервер:* VendekVPN ► Netherlands 🇳🇱\n\n"
                                          f"Ваш ключ: _#{key.key_id}_\n"
                                          f"Истекает через: _{formated_time}_"
                                          f"```{key.access_url + texts['connection_name']}```", parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "💬 Поддержка")
def support(message):
    bot.send_message(message.chat.id, texts['support_message'], parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "ℹ️ Инфо")
def info(message):
    bot.send_message(message.chat.id, "инфо")


if __name__ == '__main__':
    logger.info("Запуск telegram бота...")
    bot.polling(none_stop=True)
