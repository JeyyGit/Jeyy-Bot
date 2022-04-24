import random
import secrets
import base64

def decode_base64(user_id):
    uid = str(user_id)
    bytes_uid = uid.encode('ascii')
    base64_bytes = base64.b64encode(bytes_uid)

    return base64_bytes.decode('ascii')

def create_key(user_id):
    return decode_base64(user_id) + secrets.token_urlsafe(4)

def get_uid_from_key(api_key):
    base64_bytes = api_key[:24].encode("ascii")
    bytes_uid = base64.b64decode(base64_bytes)
    return int(bytes_uid.decode("ascii"))
