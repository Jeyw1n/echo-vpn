from flask import Flask, request, jsonify
from aiogram_bot.create_bot import bot

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def notification_webhook():
    data = request.json


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
