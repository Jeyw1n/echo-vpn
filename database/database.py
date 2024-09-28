from datetime import datetime, timedelta
import os

from loguru import logger
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from .tables import Base, User, Key, Transaction
import keymaster

# Создание движка и соединения
db_path = os.path.join(os.path.dirname(__file__), 'sqlite.db')
engine = db.create_engine(f'sqlite:///{db_path}', echo=False)
connection = engine.connect()
# Создание таблиц
Base.metadata.create_all(engine)

# Конструктор сессий
Session = sessionmaker(engine)


def user_exists(telegram_id: int) -> bool:
    """Проверяет, существует ли пользователь с данным telegram_id."""
    telegram_id = str(telegram_id)
    session = Session()
    try:
        exists = session.query(User).filter(User.telegram_id == telegram_id).first() is not None
        return exists
    except Exception as e:
        logger.error(f"Ошибка при проверке существования пользователя с telegram_id {telegram_id}: {e}")
        return False
    finally:
        session.close()


def add_user(telegram_id: int, invited_by: str = None) -> bool:
    """Добавляет пользователя в таблицу Users"""
    telegram_id = str(telegram_id)
    session = Session()
    try:
        # Добавляем нового пользователя в таблицу
        if invited_by is None:
            session.add(User(telegram_id=telegram_id))
            logger.info(f'Новый пользователь с telegram_id: {telegram_id} - успешно добавлен')
        else:
            session.add(User(telegram_id=telegram_id, invited_by=invited_by))
            logger.info(
                f'Новый пользователь (telegram_id:{telegram_id}) был приглашен пользователем (telegram_id:{invited_by})')
        session.commit()

        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя с telegram_id {telegram_id}: {e}")
        return False
    finally:
        session.close()


def key_exists(key_id: int) -> bool:
    """Проверяет, существует ли переданный ключ."""
    session = Session()
    try:
        exists = session.query(Key).filter(Key.key_id == key_id).first() is not None
        return exists
    except Exception as e:
        logger.error(f"Ошибка при проверке существования ключа (key_id:{key_id}): {e}")
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


def get_user_keys(telegram_id: int) -> list:
    telegram_id = str(telegram_id)

    session = Session()
    try:
        return session.query(Key).filter(Key.telegram_id == telegram_id).all()
    except Exception as e:
        logger.error(f"Ошибка при получении ключей пользователя {telegram_id}: {e}")
        return []
    finally:
        session.close()


def get_remaining_time(key_id: int) -> str:
    session = Session()
    try:
        key = session.query(Key).filter(Key.key_id == key_id).first()
        now = datetime.now()

        if key is None:
            logger.error(f"Ключ с ID {key_id} не найден.")
            return "Ключ не найден."

        remaining_time = key.expiry_date - now

        # Проверяем, не истек ли срок действия
        if remaining_time.total_seconds() > 0:
            days, remainder = divmod(remaining_time.total_seconds(), 86400)  # 86400 секунд в дне
            hours, remainder = divmod(remainder, 3600)  # 3600 секунд в часе
            minutes, _ = divmod(remainder, 60)  # 60 секунд в минуте

            return f"{int(days)}д {int(hours)}ч {int(minutes)}м"
        else:
            return "Срок действия истек."
    except Exception as e:
        logger.error(f"Ошибка при получении оставшегося времени для ключа {key_id}: {e}")
        return "Ошибка при получении оставшегося времени."
    finally:
        session.close()


def delete_key(key_id: int) -> None:
    session = Session()
    try:
        to_delete = session.query(Key).filter(Key.key_id == key_id).first()
        session.delete(to_delete)
        session.commit()
        logger.info(f"Ключ {key_id} успешно удален в базе данных.")
    except Exception as e:
        logger.error(f"Ошибка при получении ключа {key_id}: {e}")
        session.rollback()
    finally:
        session.close()


def create_transaction(payment_id: str, telegram_id: str, message_id: str, key_id: str, months: int) -> bool:
    """Создает новую транзакцию."""
    session = Session()
    try:
        new_transaction = Transaction(payment_id=payment_id, telegram_id=telegram_id, message_id=message_id,
                                      key_id=key_id, months=months)
        session.add(new_transaction)
        session.commit()
        logger.info(f'Транзакция с payment_id: {payment_id} успешно создана.')
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании транзакции с payment_id {payment_id}: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def mark_transaction_successful(payment_id: str) -> bool:
    """Изменяет статус транзакции на успешный."""
    session = Session()
    try:
        transaction = session.query(Transaction).filter(Transaction.payment_id == payment_id).first()
        if transaction is None:
            logger.warning(f"Транзакция с payment_id {payment_id} не найдена.")
            return False

        transaction.status = 'Successful'
        session.commit()
        logger.info(f'Статус транзакции с payment_id: {payment_id} изменен на успешный.')
        return True
    except Exception as e:
        logger.error(f"Ошибка при изменении статуса транзакции с payment_id {payment_id}: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def transaction_exists(payment_id: str) -> bool:
    """Проверяет существование транзакции"""
    session = Session()
    try:
        transaction = session.query(Transaction).filter(Transaction.payment_id == payment_id).first()
        if transaction is None:
            logger.info(f"Транзакция с payment_id {payment_id} не найдена.")
            return False
        logger.info(f"Транзакция с payment_id {payment_id} существует")
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса транзакции с payment_id {payment_id}: {e}")
        return False
    finally:
        session.close()


def get_transaction(payment_id: str):
    """Получает транзакцию по payment_id."""
    session = Session()
    try:
        return session.query(Transaction).filter(Transaction.payment_id == payment_id).first()
    except Exception as e:
        logger.error(f"Ошибка при получении транзакции с payment_id {payment_id}: {e}")
        return None
    finally:
        session.close()


def extend_key(key_id: int, additional_days: int) -> bool:
    """Увеличивает срок действия ключа на указанное количество дней."""
    session = Session()
    try:
        key = session.query(Key).filter(Key.key_id == key_id).first()
        if key is None:
            logger.error(f"Ключ с ID {key_id} не найден.")
            return False

        # Увеличиваем срок действия ключа
        key.expiry_date += timedelta(days=additional_days)
        session.commit()
        logger.info(f"Срок действия ключа {key_id} успешно продлен на {additional_days} дней.")
        return True
    except Exception as e:
        logger.error(f"Ошибка при продлении срока действия ключа {key_id}: {e}")
        session.rollback()
        return False
    finally:
        session.close()
