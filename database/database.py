import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from .tables import Base, User, Key

from loguru import logger

# Создание движка и соединения
engine = db.create_engine('sqlite:///sqlite.db', echo=True)
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
