# PaytmChecksum.py

import base64
import string
import random
import hashlib
from Crypto.Cipher import AES

IV = '@@@@&&&&####$$$$'
BLOCK_SIZE = 16


def generate_checksum(param_dict, merchant_key, salt=None):
    params_string = __get_param_string__(param_dict)
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (params_string, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest() + salt

    return __encode__(hash_string, IV, merchant_key)


def generate_refund_checksum(param_dict, merchant_key, salt=None):
    for i in param_dict:
        if "|" in str(param_dict[i]):
            param_dict = {}
            exit()

    param_string = __get_param_string__(param_dict)
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (param_string, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest() + salt

    return __encode__(hash_string, IV, merchant_key)


def generate_checksum_by_str(param_str, merchant_key, salt=None):
    salt = salt if salt else __id_generator__(4)
    final_string = '%s|%s' % (param_str, salt)

    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest() + salt

    return __encode__(hash_string, IV, merchant_key)


def verify_checksum(param_dict, merchant_key, checksum):
    if 'CHECKSUMHASH' in param_dict:
        param_dict.pop('CHECKSUMHASH')

    paytm_hash = __decode__(checksum, IV, merchant_key)
    salt = paytm_hash[-4:]

    calculated_checksum = generate_checksum(param_dict, merchant_key, salt=salt)
    return calculated_checksum == checksum


def verify_checksum_by_str(param_str, checksum, merchant_key):
    paytm_hash = __decode__(checksum, IV, merchant_key)
    salt = paytm_hash[-4:]

    calculated_checksum = generate_checksum_by_str(param_str, merchant_key, salt=salt)
    return calculated_checksum == checksum


# 🔑 Utility functions
def __id_generator__(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


def __get_param_string__(params):
    params = {k: v for k, v in params.items() if v is not None and v != ""}
    params_string = '&'.join(['%s=%s' % (k, v) for k, v in sorted(params.items())])
    return params_string


def __pad__(s):
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)


def __unpad__(s):
    return s[0:-ord(s[-1])]


def __encode__(to_encode, iv, key):
    to_encode = __pad__(to_encode)
    c = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    crypted = c.encrypt(to_encode.encode("utf-8"))
    crypted = base64.b64encode(crypted)
    return crypted.decode("utf-8")


def __decode__(to_decode, iv, key):
    to_decode = base64.b64decode(to_decode)
    c = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    decoded = c.decrypt(to_decode)
    return __unpad__(decoded.decode("utf-8"))


# ✅ Example usage
if __name__ == "__main__":
    # Sample merchant details
    merchant_key = "1234567890123456"  # must be 16/24/32 chars
    params = {
        "MID": "WorldP64425807474247",
        "ORDER_ID": "ORDER0001",
        "CUST_ID": "CUST001",
        "TXN_AMOUNT": "100.00",
        "CHANNEL_ID": "WEB",
        "WEBSITE": "WEBSTAGING",
        "INDUSTRY_TYPE_ID": "Retail",
        "CALLBACK_URL": "http://127.0.0.1:8000/shop/handlerequest/",
    }

    print("🔹 Generating checksum...")
    checksum = generate_checksum(params, merchant_key)
    print("CHECKSUMHASH:", checksum)

    print("\n🔹 Verifying checksum...")
    is_valid = verify_checksum(params.copy(), merchant_key, checksum)
    print("Checksum Valid:", is_valid)
