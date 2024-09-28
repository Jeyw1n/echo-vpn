from datetime import timedelta, datetime

from flask import Flask, request, jsonify, abort
import database
from loguru import logger
from aiogram_bot.create_bot import bot
import config as conf

app = Flask(__name__)


async def handle_successful_payment(payment_id: str):
    """Обрабатывает успешный платеж."""
    # Фильтруем только IP адреса от ЮМани
    if request.remote_addr not in conf.TRUSTED_IP:
        return abort(403)

    transaction = database.get_transaction(payment_id)
    if not transaction:
        logger.warning(f"Транзакция с payment_id {payment_id} не найдена.")
        return jsonify({"status": "transaction not found"}), 404

    telegram_id = transaction.telegram_id
    message_id = transaction.message_id
    key_id = transaction.key_id
    months = transaction.months

    # Обновляем статус транзакции
    if database.mark_transaction_successful(payment_id):
        logger.info(f"Транзакция {payment_id} обновлена на успешный статус.")

        # Удаляем сообщение с указанным message_id
        await delete_message(telegram_id, message_id)

        # Продлеваем ключ или создаем новый
        if key_id == 'new':
            expiration_date = datetime.now() + timedelta(days=months * 30)
            database.add_key(telegram_id, expiration_date)
            success_message = "🎉 Поздравляем! Ваш новый ключ успешно создан! 🎉\n" \
                              f"Срок действия: *{months * 30} дней*."
            await bot.send_message(chat_id=telegram_id, text=success_message)
        elif database.key_exists(int(key_id)):
            database.extend_key(int(key_id), months * 30)
            success_message = "🔄 Ваш ключ успешно продлен! 🔄\n" \
                              f"Срок действия увеличен на *{months * 30} дней*."
            await bot.send_message(chat_id=telegram_id, text=success_message)

    return jsonify({"status": "success"}), 200


async def delete_message(telegram_id: str, message_id: int):
    """Удаляет сообщение в Telegram."""
    try:
        await bot.delete_message(chat_id=telegram_id, message_id=message_id)
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")


@app.route('/webhook', methods=['POST'])
async def notification_webhook():
    data = request.json
    logger.debug(f"Webhook получил данные: {data}")

    # Проверяем, что это событие успешного платежа
    if data.get("event") == "payment.succeeded":
        payment_id = data.get("id")
        return await handle_successful_payment(payment_id)

    logger.warning(f"Получено неизвестное событие: {data.get('event')}")
    return jsonify({"status": "ignored"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
