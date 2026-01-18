"""
本地缓存管理模块
"""
import time
import threading
from src.config import LOCAL_CACHE, DATA_LOCK
from src.utils.helpers import get_beijing_time
from .jsonbin import sync_from_cloud, sync_to_cloud


def load_subscriptions():
    """加载订阅数据"""
    if time.time() - LOCAL_CACHE['last_sync'] > 300:
        sync_from_cloud()
    return LOCAL_CACHE['subscriptions'].copy()


def save_subscriptions(data):
    """保存订阅数据"""
    with DATA_LOCK:
        LOCAL_CACHE['subscriptions'] = data
    threading.Thread(target=sync_to_cloud).start()


def load_pins():
    """加载密钥数据"""
    return LOCAL_CACHE['pins'].copy()


def save_pin(pin_code, user_data):
    """保存密钥"""
    with DATA_LOCK:
        LOCAL_CACHE['pins'][pin_code] = user_data
    threading.Thread(target=sync_to_cloud).start()


def delete_pin(pin_code):
    """删除密钥"""
    with DATA_LOCK:
        if pin_code in LOCAL_CACHE['pins']:
            del LOCAL_CACHE['pins'][pin_code]
    threading.Thread(target=sync_to_cloud).start()


def get_pin_by_user(user_id):
    """根据用户ID获取密钥"""
    for pin, data in LOCAL_CACHE['pins'].items():
        if data.get('user_id') == user_id:
            return pin
    return None


def add_log(level, message, user=None):
    """添加日志"""
    log_entry = {
        'time': get_beijing_time().strftime('%Y-%m-%d %H:%M:%S'),
        'level': level,
        'user': user,
        'message': message
    }
    with DATA_LOCK:
        LOCAL_CACHE['logs'].append(log_entry)
        LOCAL_CACHE['logs'] = LOCAL_CACHE['logs'][-200:]


def get_logs():
    """获取日志"""
    return LOCAL_CACHE['logs'].copy()
