import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup

from loguru import logger
from decouple import config, UndefinedValueError
import yaml

import sys

from database import database as db

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
    # Сохраняем пользователя в базу данных
    db_save_result = db.add_user(message.from_user.id)
    markup = keyboard_create(menu_buttons)
    if db_save_result or True:
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
    bot.send_message(message.chat.id, "Ключи и оплата бла бла бла...")


@bot.message_handler(func=lambda message: message.text == "💬 Поддержка")
def support(message):
    bot.send_message(message.chat.id, texts['support_message'], parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "ℹ️ Инфо")
def info(message):
    bot.send_message(message.chat.id, "инфо")


if __name__ == '__main__':
    logger.info("Запуск telegram бота...")
    bot.polling(none_stop=True)
