"""
JSONBin 云存储模块
"""
import time
import logging
import requests
from src.config import JSONBIN_API_KEY, JSONBIN_BIN_ID, LOCAL_CACHE, DATA_LOCK

logger = logging.getLogger(__name__)


def jsonbin_read():
    """从 JSONBin 读取数据"""
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        return None
    try:
        resp = requests.get(
            f'https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest',
            headers={'X-Master-Key': JSONBIN_API_KEY},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get('record', {})
    except Exception as e:
        logger.error(f"JSONBin 读取失败: {e}")
    return None


def jsonbin_write(data):
    """写入数据到 JSONBin"""
    if not JSONBIN_API_KEY or not JSONBIN_BIN_ID:
        return False
    try:
        resp = requests.put(
            f'https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}',
            headers={
                'X-Master-Key': JSONBIN_API_KEY,
                'Content-Type': 'application/json'
            },
            json=data,
            timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"JSONBin 写入失败: {e}")
    return False


def sync_from_cloud():
    """从云端同步数据到本地"""
    global LOCAL_CACHE
    data = jsonbin_read()
    if data:
        with DATA_LOCK:
            LOCAL_CACHE['subscriptions'] = data.get('subscriptions', {})
            LOCAL_CACHE['pins'] = data.get('pins', {})
            LOCAL_CACHE['logs'] = data.get('logs', [])
            LOCAL_CACHE['last_sync'] = time.time()
        logger.info("从云端同步数据成功")
        return True
    return False


def sync_to_cloud():
    """同步本地数据到云端"""
    with DATA_LOCK:
        data = {
            'subscriptions': LOCAL_CACHE['subscriptions'],
            'pins': LOCAL_CACHE['pins'],
            'logs': LOCAL_CACHE['logs'][-100:]
        }
    if jsonbin_write(data):
        logger.info("同步数据到云端成功")
        return True
    return False
