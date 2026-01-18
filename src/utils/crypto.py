"""
加密解密工具模块
"""
import base64
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from src.config import ENCRYPT_KEY

logger = logging.getLogger(__name__)


def encrypt_password(password):
    """AES加密密码"""
    try:
        cipher = AES.new(ENCRYPT_KEY, AES.MODE_ECB)
        padded = pad(password.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"加密失败: {e}")
        return None


def decrypt_password(encrypted):
    """AES解密密码"""
    try:
        cipher = AES.new(ENCRYPT_KEY, AES.MODE_ECB)
        decrypted = cipher.decrypt(base64.b64decode(encrypted))
        return unpad(decrypted, AES.block_size).decode('utf-8')
    except Exception as e:
        logger.error(f"解密失败: {e}")
        return None
