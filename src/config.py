"""
配置模块 - 包含所有配置项和全局状态
"""
import os
import threading
from datetime import datetime, timedelta, timezone

# Flask 配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'wzu-grade-helper-secret-key-2024')
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# API 密钥
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
JSONBIN_API_KEY = os.environ.get('JSONBIN_API_KEY', '')
JSONBIN_BIN_ID = os.environ.get('JSONBIN_BIN_ID', '')

# 微信推送 (Server酱) - 获取地址: https://sct.ftqq.com/
SERVERCHAN_KEY = os.environ.get('SERVERCHAN_KEY', '')

# 加密密钥（32字节）
ENCRYPT_KEY = os.environ.get('ENCRYPT_KEY', 'wzu-grade-helper-encrypt-key-32').encode()[:32].ljust(32, b'0')

# 北京时区
BEIJING_TZ = timezone(timedelta(hours=8))

# 本地缓存
LOCAL_CACHE = {
    'subscriptions': {},
    'pins': {},
    'logs': [],
    'last_sync': 0
}
DATA_LOCK = threading.Lock()

# 全局状态
SYSTEM_STATUS = {
    'start_time': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S'),
    'last_check_time': None,
    'total_checks': 0,
    'emails_sent': 0,
    'wechat_sent': 0,
    'last_error': None
}
