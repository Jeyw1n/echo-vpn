from loguru import logger
from decouple import config, UndefinedValueError
import sys

#####################################################
#                   Базовый конфиг                  #
#####################################################

MONTH_PRICE = 80.00
TEXTS_PATH = 'texts.yaml'
BOT_URL = 'https://t.me/vendek_vpn_bot'
WEBHOOK_URL = ''
ADMINS = [361186618]

#####################################################
#               Ключи из ".env" файла               #
#####################################################
try:
    # Outline
    API_URL = config('API_URL')
    CERT_SHA = config('CERT_SHA')
    # Telegram
    BOT_TOKEN = config('BOT_TOKEN')
    # Yookassa
    ACCOUNT_ID = config('ACCOUNT_ID')
    SECRET_KEY = config('SECRET_KEY')

except UndefinedValueError:
    logger.error('Не все ключи найдены! Проверьте ".env" файл.')
    sys.exit(1)
