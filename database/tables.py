from datetime import datetime
from enum import unique
from importlib.metadata import requires

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column('user_id', Integer, primary_key=True, unique=True, autoincrement=True)
    telegram_id = Column('telegram_id', String, unique=True)
    registration_date = Column('registration_date', DateTime)
    invited_by = Column('invited_by', String)

    def __init__(self, telegram_id, registration_date=datetime.now(), invited_by=''):
        self.telegram_id = telegram_id
        self.registration_date = registration_date
        self.invited_by = invited_by

    def __repr__(self):
        return f'<User(user_id={self.user_id}, telegram_id={self.telegram_id}, registration_date={self.registration_date}, invited_by={self.invited_by})>'


class Key(Base):
    __tablename__ = 'keys'

    key_id = Column('key_id', Integer, primary_key=True, unique=True)
    telegram_id = Column('telegram_id', String)
    access_url = Column('access_url', String, unique=True)
    expiry_date = Column('expiry_date', DateTime)

    def __init__(self, key_id, telegram_id, access_url, expiry_date):
        self.key_id = key_id
        self.telegram_id = telegram_id
        self.access_url = access_url
        self.expiry_date = expiry_date

    def __repr__(self):
        return f"<Key(key_id={self.key_id}, telegram_id={self.telegram_id}, access_url={self.access_url}, expiry_date={self.expiry_date})>"


class Transaction(Base):
    __tablename__ = 'transaction'

    payment_id = Column('payment_id', String, unique=True)
    telegram_id = Column('telegram_id', String)
    message_id = Column('message_id', String)
    key_id = Column('key_id', String)
    months = Column('months', Integer)
    status = Column('status', String)

    def __init__(self, payment_id, telegram_id, message_id, key_id, months, status='Uncompleted'):
        self.payment_id = payment_id
        self.telegram_id = telegram_id
        self.message_id = message_id
        self.key_id = key_id
        self.months = months
        self.status = status
