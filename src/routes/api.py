"""
API 路由模块 - 用户相关接口
"""
import hashlib
from flask import Blueprint, request, jsonify, session

from src.config import RESEND_API_KEY, SYSTEM_STATUS
from src.utils.crypto import encrypt_password, decrypt_password
from src.utils.helpers import get_beijing_time
from src.storage.cache import (
    load_subscriptions, save_subscriptions,
    load_pins, save_pin, delete_pin, get_pin_by_user,
    add_log
)
from src.services.spider import WzuSpider
from src.services.email import send_email
from src.services.gpa import calculate_gpa, calculate_target_gpa, get_gpa_level
from src.services.wechat import send_wechat, generate_gpa_wechat_content
from src.services.scheduler import get_scheduler

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ==================== 健康检查 ====================

@api_bp.route('/health')
def health_check():
    """健康检查端点"""
    scheduler = get_scheduler()
    return jsonify({
        'status': 'healthy',
        'timestamp': get_beijing_time().isoformat(),
        'uptime': SYSTEM_STATUS['start_time'],
        'scheduler_running': scheduler.running if scheduler else False,
        'services': {
            'email': bool(RESEND_API_KEY)
        }
    })


# ==================== GPA 计算 ====================

@api_bp.route('/gpa/calculate', methods=['POST'])
def gpa_calculate():
    """计算 GPA"""
    if 'wzu_cookies' not in session:
        return jsonify({'status': 'error', 'msg': '未登录'}), 401
    
    d = request.json or {}
    grades = d.get('grades', [])
    
    if not grades:
        return jsonify({'status': 'error', 'msg': '成绩数据为空'})
    
    result = calculate_gpa(grades)
    level_info = get_gpa_level(result['gpa'])
    result['level'] = level_info
    
    return jsonify({'status': 'ok', 'data': result})


@api_bp.route('/gpa/target', methods=['POST'])
def gpa_target():
    """目标 GPA 分析"""
    if 'wzu_cookies' not in session:
        return jsonify({'status': 'error', 'msg': '未登录'}), 401
    
    d = request.json or {}
    grades = d.get('grades', [])
    target_gpa = d.get('target_gpa', 3.5)
    remaining_credits = d.get('remaining_credits', 30)
    
    try:
        target_gpa = float(target_gpa)
        remaining_credits = float(remaining_credits)
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'msg': '参数格式错误'})
    
    if target_gpa <= 0 or target_gpa > 5:
        return jsonify({'status': 'error', 'msg': '目标 GPA 应在 0-5 之间'})
    
    result = calculate_target_gpa(grades, target_gpa, remaining_credits)
    return jsonify({'status': 'ok', 'data': result})


@api_bp.route('/gpa/report', methods=['POST'])
def gpa_report():
    """发送 GPA 报告到微信"""
    if 'wzu_cookies' not in session:
        return jsonify({'status': 'error', 'msg': '未登录'}), 401
    
    d = request.json or {}
    grades = d.get('grades', [])
    wechat_key = d.get('wechat_key', '').strip()
    
    if not grades:
        return jsonify({'status': 'error', 'msg': '成绩数据为空'})
    
    if not wechat_key:
        return jsonify({'status': 'error', 'msg': '请填写你的 Server酱 SendKey'})
    
    gpa_info = calculate_gpa(grades)
    content = generate_gpa_wechat_content(gpa_info)
    
    ok, msg = send_wechat(f"📊 GPA报告: {gpa_info['gpa']:.3f}", content, wechat_key)
    
    if ok:
        add_log('info', 'GPA报告推送成功', session.get('username', '')[:4] + '***')
        return jsonify({'status': 'ok', 'msg': '已发送到微信'})
    return jsonify({'status': 'error', 'msg': f'发送失败: {msg}'})


# ==================== 微信推送测试 ====================

@api_bp.route('/test-wechat', methods=['POST'])
def test_wechat():
    """测试微信推送"""
    d = request.json or {}
    wechat_key = d.get('wechat_key', '').strip()
    
    if not wechat_key:
        return jsonify({'status': 'error', 'msg': '请填写你的 Server酱 SendKey'})
    
    content = f"""## 🎓 测试消息

微信推送功能正常！

---
📅 时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    ok, msg = send_wechat("🎓 温大成绩助手 - 测试", content, wechat_key, "这是一条测试消息")
    
    if ok:
        return jsonify({'status': 'ok', 'msg': '已发送，请查看微信'})
    return jsonify({'status': 'error', 'msg': f'发送失败: {msg}'})


@api_bp.route('/login', methods=['POST'])
def handle_login():
    """账号密码登录"""
    d = request.json or {}
    username, password = d.get('username', '').strip(), d.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'status': 'error', 'msg': '请输入学号和密码'})
    
    spider = WzuSpider()
    ok, msg = spider.login(username, password)
    
    if ok:
        session.permanent = True
        session['wzu_cookies'] = spider.get_cookies_for_storage()
        session['user_id'] = hashlib.md5(username.encode()).hexdigest()
        session['username'] = username
        session['password'] = password  # 临时保存，用于设置密钥
        add_log('info', '登录成功', username[:4] + '***')
        return jsonify({'status': 'ok'})
    
    return jsonify({'status': 'error', 'msg': msg})


@api_bp.route('/pin-login', methods=['POST'])
def pin_login():
    """密钥登录 - 使用存储的账号密码重新登录"""
    d = request.json or {}
    pin = d.get('pin', '').strip()
    
    if not pin:
        return jsonify({'status': 'error', 'msg': '请输入密钥'})
    
    pins = load_pins()
    if pin not in pins:
        return jsonify({'status': 'error', 'msg': '密钥不存在'})
    
    pin_data = pins[pin]
    username = pin_data.get('username', '')
    enc_password = pin_data.get('password', '')
    
    if not username or not enc_password:
        return jsonify({'status': 'error', 'msg': '密钥数据异常'})
    
    # 解密密码
    password = decrypt_password(enc_password)
    if not password:
        return jsonify({'status': 'error', 'msg': '密钥解密失败'})
    
    # 使用账号密码登录
    spider = WzuSpider()
    ok, msg = spider.login(username, password)
    
    if not ok:
        add_log('warning', f'密钥登录失败: {msg}', username[:4] + '***')
        if "密码错误" in msg or "账号或密码错误" in msg:
            return jsonify({'status': 'error', 'msg': '教务密码已修改，请用账号密码登录后重新设置密钥'})
        return jsonify({'status': 'error', 'msg': f'登录失败: {msg}'})
    
    # 登录成功
    session.permanent = True
    session['wzu_cookies'] = spider.get_cookies_for_storage()
    session['user_id'] = pin_data.get('user_id', '')
    session['username'] = username
    session['password'] = password
    
    add_log('info', '密钥登录成功', username[:4] + '***')
    return jsonify({'status': 'ok'})


@api_bp.route('/pin/set', methods=['POST'])
def set_pin():
    """设置密钥 - 保存加密的账号密码"""
    if 'username' not in session or 'password' not in session:
        return jsonify({'status': 'error', 'msg': '请先用账号密码登录'})
    
    d = request.json or {}
    pin = d.get('pin', '').strip()
    
    if len(pin) < 4 or len(pin) > 16:
        return jsonify({'status': 'error', 'msg': '密钥长度需要4-16位'})
    
    # 检查密钥是否被其他用户使用
    pins = load_pins()
    if pin in pins and pins[pin].get('user_id') != session.get('user_id'):
        return jsonify({'status': 'error', 'msg': '该密钥已被使用'})
    
    # 删除该用户的旧密钥
    old_pin = get_pin_by_user(session['user_id'])
    if old_pin and old_pin != pin:
        delete_pin(old_pin)
    
    # 加密密码
    enc_password = encrypt_password(session['password'])
    if not enc_password:
        return jsonify({'status': 'error', 'msg': '加密失败'})
    
    # 保存密钥
    save_pin(pin, {
        'user_id': session['user_id'],
        'username': session['username'],
        'password': enc_password,  # 加密存储
        'created': get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    add_log('info', '设置密钥', session['username'][:4] + '***')
    return jsonify({'status': 'ok'})


@api_bp.route('/pin/delete', methods=['POST'])
def delete_user_pin():
    """删除密钥"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'msg': '请先登录'})
    
    old_pin = get_pin_by_user(session['user_id'])
    if old_pin:
        delete_pin(old_pin)
        add_log('info', '删除密钥', session.get('username', '')[:4] + '***')
    
    return jsonify({'status': 'ok'})


@api_bp.route('/pin/status')
def pin_status():
    """获取密钥状态"""
    if 'user_id' not in session:
        return jsonify({'has_pin': False})
    return jsonify({'has_pin': bool(get_pin_by_user(session['user_id']))})


@api_bp.route('/grades', methods=['POST'])
def fetch_grades():
    """获取成绩"""
    if 'wzu_cookies' not in session:
        return jsonify({'status': 'error', 'msg': '未登录'}), 401
    
    spider = WzuSpider()
    spider.load_cookies_from_storage(session['wzu_cookies'])
    
    d = request.json or {}
    ok, res = spider.get_grades(d.get('xnm', ''), d.get('xqm', ''))
    
    if ok:
        return jsonify({'status': 'ok', 'data': res})
    
    session.pop('wzu_cookies', None)
    return jsonify({'status': 'error', 'msg': '会话过期'}), 401


@api_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """订阅 - 保存加密的账号密码用于定时任务"""
    if 'username' not in session or 'password' not in session:
        return jsonify({'status': 'error', 'msg': '请用账号密码登录后再订阅'})
    
    d = request.json or {}
    email = d.get('email', '').strip()
    notify_email = d.get('notify_email', True)  # 邮件通知
    notify_wechat = d.get('notify_wechat', False)  # 微信通知
    wechat_key = d.get('wechat_key', '').strip()  # 用户自己的 Server酱 Key
    
    # 至少选择一种通知方式
    if not notify_email and not notify_wechat:
        return jsonify({'status': 'error', 'msg': '请至少选择一种通知方式'})
    
    # 如果开启邮件通知，检查邮箱
    if notify_email and (not email or '@' not in email):
        return jsonify({'status': 'error', 'msg': '邮箱格式不正确'})
    
    # 如果开启微信通知，检查是否有 Key
    if notify_wechat and not wechat_key:
        return jsonify({'status': 'error', 'msg': '请填写你的 Server酱 SendKey'})
    
    enc_password = encrypt_password(session['password'])
    if not enc_password:
        return jsonify({'status': 'error', 'msg': '加密失败'})
    
    user_id = session['user_id']
    subs = load_subscriptions()
    subs[user_id] = {
        'email': email,
        'username': session['username'],
        'password': enc_password,  # 加密存储
        'interval': d.get('interval', 30),
        'start_hour': d.get('start_hour', 8),
        'end_hour': d.get('end_hour', 22),
        'notify_email': notify_email,
        'notify_wechat': notify_wechat,
        'wechat_key': wechat_key,  # 用户的 Server酱 Key
        'last_check': 0,
        'grades_hash': '',
        'last_grades': [],
        'status': 'active',
        'created': get_beijing_time().isoformat()
    }
    save_subscriptions(subs)
    
    notify_types = []
    if notify_email:
        notify_types.append('邮件')
    if notify_wechat:
        notify_types.append('微信')
    
    add_log('info', f'订阅: {"+".join(notify_types)}', session['username'][:4] + '***')
    return jsonify({'status': 'ok'})


@api_bp.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    """取消订阅"""
    user_id = session.get('user_id', '')
    if user_id:
        subs = load_subscriptions()
        if user_id in subs:
            del subs[user_id]
            save_subscriptions(subs)
            add_log('info', '取消订阅', session.get('username', '')[:4] + '***')
    return jsonify({'status': 'ok'})


@api_bp.route('/subscribe/status')
def subscribe_status():
    """获取订阅状态"""
    user_id = session.get('user_id', '')
    subs = load_subscriptions()
    
    if user_id and user_id in subs:
        d = subs[user_id]
        # 脱敏显示 wechat_key
        wechat_key = d.get('wechat_key', '')
        wechat_key_masked = ''
        if wechat_key:
            wechat_key_masked = wechat_key[:8] + '***' if len(wechat_key) > 8 else '***'
        
        return jsonify({
            'subscribed': True,
            'email': d.get('email'),
            'interval': d.get('interval', 30),
            'start_hour': d.get('start_hour', 8),
            'end_hour': d.get('end_hour', 22),
            'notify_email': d.get('notify_email', True),
            'notify_wechat': d.get('notify_wechat', False),
            'wechat_key_masked': wechat_key_masked,
            'status': d.get('status', 'active')
        })
    
    return jsonify({
        'subscribed': False
    })


@api_bp.route('/test-email', methods=['POST'])
def test_email():
    """测试邮件发送"""
    d = request.json or {}
    email = d.get('email', '').strip()
    
    if not email or '@' not in email:
        return jsonify({'status': 'error', 'msg': '请输入有效邮箱'})
    
    html = f'''<div style="font-family:sans-serif;padding:20px;">
        <h2 style="color:#667eea;">🎓 测试邮件</h2>
        <p>邮件推送功能正常！</p>
        <p style="color:#999;font-size:12px;">时间: {get_beijing_time().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>'''
    
    ok, msg = send_email(email, "🎓 温大成绩助手 - 测试", html)
    
    if ok:
        return jsonify({'status': 'ok', 'msg': '已发送，请检查收件箱'})
    return jsonify({'status': 'error', 'msg': f'失败: {msg}'})
