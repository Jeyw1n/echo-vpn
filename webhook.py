from datetime import timedelta, datetime
import logging
import ipaddress

from quart import Quart, request, jsonify, abort
from loguru import logger
from aiogram import Bot

import config as conf
import database

# Настройка логирования
logger.add("./logs/webhook.log", level='INFO')

app = Quart(__name__)


def is_trusted_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        logger.warning(f"Некорректный IP-адрес: {ip}")
        return False
    for trusted_ip in conf.TRUSTED_IP:
        if ip_obj in ipaddress.ip_network(trusted_ip):
            return True
    logger.warning(f"IP-адрес {ip} не является доверенным.")
    return False


API_TOKEN = conf.BOT_TOKEN
bot = Bot(token=API_TOKEN)


async def handle_successful_payment(payment_id: str):
    """Обрабатывает успешный платеж."""
    transaction = database.get_transaction(payment_id)
    logger.debug(transaction)
    if not transaction:
        logger.warning(f"Транзакция с payment_id {payment_id} не найдена.")
        return jsonify({"status": "transaction not found"}), 404

    telegram_id = transaction.telegram_id
    # message_id = transaction.message_id
    key_id = transaction.key_id
    months = transaction.months

    # Обновляем статус транзакции
    if database.mark_transaction_successful(payment_id):
        logger.info(f"Транзакция {payment_id} обновлена на успешный статус.")

        try:
            user = await bot.get_chat(chat_id=telegram_id)
            # Сообщение админам
            for admin_id in conf.ADMINS:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f'Транзакция ({payment_id}) прошла успешно.\n'
                    f'key_id: {key_id}\n'
                    f'months: {months}\n'
                    f'telegram_id: {telegram_id}\n'
                    f'user: @{user.username}'
                )
        except Exception as ex:
            logger.error(f'Ошибка отправки информации администратору: {ex}')

        # Удаляем сообщение с указанным message_id
        # await delete_message(telegram_id, message_id)

        # Продлеваем ключ или создаем новый
        if key_id == 'new':
            expiration_date = datetime.now() + timedelta(days=months * 30)
            database.add_key(telegram_id, expiration_date)
            success_message = "🎉 Поздравляем! Ваш новый ключ успешно создан! 🎉\n" \
                              f"Срок действия: *{months * 30} дней*."
            await bot.send_message(chat_id=telegram_id, text=success_message, parse_mode='Markdown')
        elif database.key_exists(int(key_id)):
            database.extend_key(int(key_id), months * 30)
            success_message = "🔄 Ваш ключ успешно продлен! 🔄\n" \
                              f"Срок действия увеличен на *{months * 30} дней*."
            await bot.send_message(chat_id=telegram_id, text=success_message, parse_mode='Markdown')

    return jsonify({"status": "success"}), 200


# async def delete_message(telegram_id: str, message_id: int):
#     """Удаляет сообщение в Telegram."""
#     try:
#         await bot.delete_message(chat_id=telegram_id, message_id=message_id)
#     except Exception as e:
#         logger.error(f"Ошибка при удалении сообщения: {e}")

@app.before_request
async def before_request():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    if not is_trusted_ip(ip):
        logger.warning(f"Недоверенный запрос от: {ip} к пути: {request.path}")
        return abort(403)


@app.route('/webhook', methods=['POST'])
async def notification_webhook():
    # # Фильтруем только IP адреса от ЮМани
    # ip = request.remote_addr
    # if not is_trusted_ip(ip):
    #     return abort(403)

    data = await request.get_json()
    logger.debug(f"Webhook получил данные: {data}")

    # Проверяем, что это событие успешного платежа
    if data.get("event") == "payment.succeeded":
        payment_id = data.get("object").get('id')
        logger.debug(payment_id)
        return await handle_successful_payment(payment_id)

    logger.warning(f"Получено неизвестное событие: {data.get('event')}")
    return jsonify({"status": "ignored"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
