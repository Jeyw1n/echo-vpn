import uuid
import sys
from decouple import config, UndefinedValueError
from loguru import logger
from yookassa import Configuration, Payment, Webhook

import config as conf

Configuration.account_id = conf.ACCOUNT_ID
Configuration.secret_key = conf.SECRET_KEY

# response = Webhook.add({
#     "event": "payment.succeeded",
#     "url": conf.WEBHOOK_URL
# })

def create_payment(amount: float, description: str) -> tuple[str, str]:
    """
    Создает платеж в системе ЮMoney.
    :param amount: Сумма платежа (в рублях).
    :param description: Описание платежа.
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
