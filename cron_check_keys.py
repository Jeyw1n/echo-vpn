import database as db
from loguru import logger
import keymaster

logger.add("./logs/cron.log")

def main():
    expired_keys = db.get_expired_keys()
    if not expired_keys:
        logger.debug('Нет просроченных ключей.')
    for key in expired_keys:
        keymaster.delete_key(key.key_id)
        db.delete_key(key.key_id)


if __name__ == '__main__':
    main()
