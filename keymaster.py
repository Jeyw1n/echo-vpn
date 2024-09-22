from decouple import config
from outline_vpn.outline_vpn import OutlineVPN
from loguru import logger

api_url = config('API_URL')
cert_sha256 = config('CERT_SHA')

client = OutlineVPN(api_url=api_url, cert_sha256=cert_sha256)


def get_keys():
    return client.get_keys()


def create_new_key():
    new_key = client.create_key()
    logger.info('Создан ключ:', new_key.key_id)
    return new_key


def delete_key(key_id):
    result = client.delete_key(key_id)
    if result:
        logger.info(f"Ключ {key_id} успешно удален на сервере.")
    else:
        logger.warning(f"Ключ {key_id} не удалён на сервере.")
    return result
