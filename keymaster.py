from decouple import config
from outline_vpn.outline_vpn import OutlineVPN

api_url = config('API_URL')
cert_sha256 = config('CERT_SHA')

client = OutlineVPN(api_url=api_url, cert_sha256=cert_sha256)


def get_keys():
    return client.get_keys()


def create_new_key():
    return client.create_key()
# OutlineKey(key_id='3', name='Test', password='SFpjlnMy5OldOOTsR8CAVs', port=48430, method='chacha20-ietf-poly1305',
# access_url='ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpTRnBqbG5NeTVPbGRPT1RzUjhDQVZz@147.45.232.123:48430/?outline=1',
# used_bytes=0, data_limit=None)
