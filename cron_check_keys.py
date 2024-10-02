from aiogram import Bot
from loguru import logger

import database as db
import keymaster
import config as conf

logger.add("./logs/cron.log", level='INFO')

# API_TOKEN = conf.BOT_TOKEN
# bot = Bot(token=API_TOKEN)


def main():
    expired_keys = db.get_expired_keys()
    if not expired_keys:
        logger.debug('Нет просроченных ключей.')
    for key in expired_keys:
        keymaster.delete_key(key.key_id)
        db.delete_key(key.key_id)


if __name__ == '__main__':
    main()
