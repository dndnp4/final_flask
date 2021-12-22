import os
import hashlib
import sys
from config import CommonConfig

def create_salt(length=CommonConfig.SALT_LENGTH):
    return os.urandom(length)

def encrypt_password(plaintext, salt):
    digest = hashlib.pbkdf2_hmac(CommonConfig.HASH_NAME, plaintext.encode(), salt, CommonConfig.SALT_LENGTH)
    return digest.hex()

