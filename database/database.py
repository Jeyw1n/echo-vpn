from datetime import datetime
import os

from loguru import logger
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from .tables import Base, User, Key
import keymaster

# Создание движка и соединения
db_path = os.path.join(os.path.dirname(__file__), 'sqlite.db')
engine = db.create_engine(f'sqlite:///{db_path}', echo=False)
connection = engine.connect()
# Создание таблиц
Base.metadata.create_all(engine)

# Конструктор сессий
Session = sessionmaker(engine)


def add_user(telegram_id: str) -> bool:
    # Создание сессии
    session = Session()
    try:
        # Выполнение запроса для проверки существования записи с этим telegram_id
        exists = session.query(User).filter(User.telegram_id == telegram_id).first() is not None
        if not exists:
            # Добавляем нового пользователя в таблицу
            session.add(User(telegram_id))
            session.commit()
            logger.info(f'Новый пользователь с telegram_id: {telegram_id} - успешно добавлен')
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке telegram_id: {e}")
        return False
    finally:
        session.close()


def add_key(telegram_id, expiry_date):
    # Создание сессии
    session = Session()
    try:
        # Создаем новый ключ
        new_key = keymaster.create_new_key()
        logger.debug(new_key)
        access_url = new_key.access_url
        key_id = new_key.key_id

        # Добавляем новый ключ в таблицу
        new_key = Key(key_id=key_id, telegram_id=telegram_id, access_url=access_url, expiry_date=expiry_date)
        session.add(new_key)
        session.commit()
        logger.info(f'Ключ (id:{key_id}) успешно добавлен для пользователя {telegram_id}')
    except Exception as e:
        logger.error(f"Ошибка при добавлении ключа: {e}")
    finally:
        session.close()


def get_expired_keys() -> list:
    # Создание сессии
    session = Session()
    try:
        # Получаем текущее время
        now = datetime.now()
        # Запрашиваем все записи, у которых expiry_date меньше текущего времени
        expired_keys = session.query(Key).filter(Key.expiry_date < now).all()
        return expired_keys
    except Exception as e:
        logger.error(f"Ошибка при получении истекших ключей: {e}")
        return []
    finally:
        session.close()


def get_user_keys(telegram_id: str) -> list:
    session = Session()
    try:
        return session.query(Key).filter(Key.telegram_id == telegram_id).all()
    except Exception as e:
        logger.error(f"Ошибка при получении ключей пользователя {telegram_id}: {e}")
        return []
    finally:
        session.close()


def get_remaining_time(key_id: int) -> int:
    session = Session()
    try:
        key = session.query(Key).filter(Key.key_id == key_id).first()
        now = datetime.now()
        remaining_time = key.expiry_date - now
        # Проверяем, не истек ли срок действия
        if remaining_time.total_seconds() > 0:
            return remaining_time
        else:
            return 0
    except Exception as e:
        logger.error(f"Ошибка при получении оставшегося времени для ключа {key_id}: {e}")
        return 0
    finally:
        session.close()