"""
管理后台路由模块
"""
import threading
from flask import Blueprint, request, jsonify, session

from src.config import ADMIN_PASSWORD, RESEND_API_KEY, JSONBIN_API_KEY, JSONBIN_BIN_ID, SYSTEM_STATUS, SERVERCHAN_KEY
from src.storage.cache import load_subscriptions, load_pins, get_logs, add_log
from src.services.scheduler import check_grades_job, get_scheduler

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    d = request.json or {}
    if d.get('password') == ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error', 'msg': '密码错误'})


@admin_bp.route('/status')
def admin_status():
    """获取系统状态"""
    if not session.get('is_admin'):
        return jsonify({'error': '未授权'}), 401
    
    subs = load_subscriptions()
    pins = load_pins()
    scheduler = get_scheduler()
    
    return jsonify({
        'scheduler_running': scheduler.running if scheduler else False,
        'start_time': SYSTEM_STATUS['start_time'],
        'last_check_time': SYSTEM_STATUS['last_check_time'],
        'total_checks': SYSTEM_STATUS['total_checks'],
        'emails_sent': SYSTEM_STATUS['emails_sent'],
        'wechat_sent': SYSTEM_STATUS.get('wechat_sent', 0),
        'subscriber_count': len(subs),
        'pin_count': len(pins),
        'resend_configured': bool(RESEND_API_KEY),
        'wechat_configured': bool(SERVERCHAN_KEY),
        'persistent_storage': bool(JSONBIN_API_KEY and JSONBIN_BIN_ID)
    })


@admin_bp.route('/subscribers')
def admin_subscribers():
    """获取订阅用户列表"""
    if not session.get('is_admin'):
        return jsonify({'error': '未授权'}), 401
    
    subs = load_subscriptions()
    return jsonify([
        {
            'username': d.get('username', '')[:4] + '***',
            'email': d.get('email', ''),
            'interval': d.get('interval', 30),
            'start_hour': d.get('start_hour', 8),
            'end_hour': d.get('end_hour', 22),
            'notify_email': d.get('notify_email', True),
            'notify_wechat': d.get('notify_wechat', False),
            'status': d.get('status', '?'),
            'last_success': (d.get('last_success', '')[:16] if d.get('last_success') else None)
        }
        for uid, d in subs.items()
    ])


@admin_bp.route('/pins')
def admin_pins():
    """获取密钥用户列表"""
    if not session.get('is_admin'):
        return jsonify({'error': '未授权'}), 401
    
    pins = load_pins()
    return jsonify([
        {
            'username': d.get('username', '')[:4] + '***',
            'created': d.get('created', '')
        }
        for pin, d in pins.items()
    ])


@admin_bp.route('/logs')
def admin_logs():
    """获取系统日志"""
    if not session.get('is_admin'):
        return jsonify({'error': '未授权'}), 401
    return jsonify(get_logs())


@admin_bp.route('/run-now', methods=['POST'])
def admin_run_now():
    """立即执行检查任务"""
    if not session.get('is_admin'):
        return jsonify({'error': '未授权'}), 401
    
    threading.Thread(target=check_grades_job).start()
    add_log('info', '手动触发检查')
    return jsonify({'status': 'ok', 'msg': '已触发'})
