from datetime import datetime
import pytz
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_moscow_time() -> datetime:
    """:return: Текущее время по МСК"""
    moscow_tz = pytz.timezone('Europe/Moscow')
    return datetime.now(moscow_tz)


class User(Base):
    __tablename__ = 'users'

    user_id = Column('user_id', Integer, primary_key=True, unique=True, autoincrement=True)
    telegram_id = Column('telegram_id', String, unique=True)
    registration_date = Column('registration_date', DateTime)
    invited_by = Column('invited_by', String)

    def __init__(self, telegram_id, registration_date=get_moscow_time(), invited_by=''):
        self.telegram_id = telegram_id
        self.registration_date = registration_date
        self.invited_by = invited_by

    def __repr__(self):
        return f'({self.user_id}) ({self.telegram_id}) ({self.registration_date}) ({self.invited_by})'


class Key(Base):
    __tablename__ = 'keys'

    key_id = Column('key_id', Integer, primary_key=True, unique=True, autoincrement=True)
    telegram_id = Column('telegram_id', String)
    access_url = Column('access_url', String, unique=True)
    expiry_date = Column('expiry_date', DateTime)

    def __repr__(self):
        return f"<Key(key_id={self.key_id}, telegram_id={self.telegram_id}, access_url={self.access_url}, expiry_date={self.expiry_date})>"
