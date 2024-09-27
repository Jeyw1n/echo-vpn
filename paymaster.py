import uuid
import sys
from decouple import config, UndefinedValueError
from loguru import logger
from yookassa import Configuration, Payment, Webhook

import config as conf

Configuration.account_id = ''
Configuration.secret_key = ''

# response = Webhook.add({
#     "event": "payment.succeeded",
#     "url": conf.WEBHOOK_URL

def create_payment(amount: float, description: str, key_id: str, telegram_id: str, message_id: int) -> tuple[str, str]:
    """
    Создает платеж в системе ЮMoney.
    :param message_id: ID сообщения.
    :param amount: Сумма платежа (в рублях).
    :param description: Описание платежа.
    :param key_id: ID ключа outline
    :param telegram_id: ID пользователя телеграм
    :return: Кортеж, содержащий URL для подтверждения платежа и идентификатор платежа.
    """
    try:
        payment = Payment.create({
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": conf.BOT_URL
            },
            'metadata': {
                'key_id': key_id,
                'telegram_id': telegram_id,
                'message_id': message_id
            },
            "capture": True,
            "description": description
        }, uuid.uuid4())

        confirmation_url = payment.confirmation.confirmation_url
        payment_id = payment.id

        logger.debug(confirmation_url + ' | ' + payment_id)
        return confirmation_url, payment_id
    except Exception as e:
        logger.error(f"Ошибка при создании платежа: {e}")
        raise
