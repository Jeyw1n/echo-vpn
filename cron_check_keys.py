import database as db
from loguru import logger

def main():
    expired_keys = db.get_expired_keys()
    if not expired_keys:
        logger.debug('Нет просроченных ключей.')
    for key in expired_keys:
        print(key)

if __name__ == '__main__':
    main()