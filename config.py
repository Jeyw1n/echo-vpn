from loguru import logger
from decouple import config, UndefinedValueError
import sys

#####################################################
#                   Базовый конфиг                  #
#####################################################

MONTH_PRICE = 65.00
TEXTS_PATH = 'texts.yaml'
BOT_URL = 'https://t.me/vendek_vpn_bot'

ADMINS = [361186618]

TRUSTED_IP = ['185.71.76.0/27','185.71.77.0/27','77.75.153.0/25','77.75.156.11','77.75.156.35','77.75.154.128/25','2a02:5180::/32']

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
