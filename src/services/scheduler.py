"""
定时任务调度模块
"""
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from src.config import SYSTEM_STATUS
from src.utils.crypto import decrypt_password
from src.utils.helpers import get_beijing_time, get_grades_hash, find_new_grades
from src.storage.cache import load_subscriptions, save_subscriptions, add_log
from src.services.email import send_email, generate_grade_email
from src.services.wechat import send_wechat, generate_grade_wechat_content
from src.services.spider import WzuSpider

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = None


def check_grades_job():
    """定时检查成绩的任务"""
    global SYSTEM_STATUS
    now = get_beijing_time()
    current_hour = now.hour
    
    logger.info(f"[定时任务] 开始检查 - {now.strftime('%H:%M:%S')}")
    SYSTEM_STATUS['last_check_time'] = now.strftime('%Y-%m-%d %H:%M:%S')
    SYSTEM_STATUS['total_checks'] += 1
    
    subs = load_subscriptions()
    if not subs:
        logger.info("[定时任务] 无订阅用户")
        return
    
    checked = 0
    for user_id, data in list(subs.items()):
        try:
            start_hour = data.get('start_hour', 8)
            end_hour = data.get('end_hour', 22)
            if not (start_hour <= current_hour < end_hour):
                continue
            
            interval = data.get('interval', 30)
            last_check = data.get('last_check', 0)
            if time.time() - last_check < interval * 60:
                continue
            
            email = data.get('email', '')
            username = data.get('username', '')
            enc_password = data.get('password', '')
            
            if not username or not enc_password:
                logger.warning(f"[定时任务] 用户 {user_id[:8]} 缺少账号信息")
                continue
            
            password = decrypt_password(enc_password)
            if not password:
                logger.warning(f"[定时任务] 用户 {user_id[:8]} 密码解密失败")
                continue
            
            logger.info(f"[定时任务] 检查: {username[:4]}*** -> {email}")
            
            # 使用账号密码登录
            spider = WzuSpider()
            ok, msg = spider.login(username, password)
            
            if not ok:
                logger.warning(f"[定时任务] 用户 {username[:4]}*** 登录失败: {msg}")
                subs[user_id]['status'] = 'login_failed'
                subs[user_id]['last_check'] = time.time()
                add_log('warning', f'登录失败: {msg}', username[:4] + '***')
                continue
            
            ok, grades = spider.get_grades()
            subs[user_id]['last_check'] = time.time()
            
            if not ok:
                logger.warning(f"[定时任务] 获取成绩失败: {grades}")
                continue
            
            subs[user_id]['status'] = 'active'
            checked += 1
            
            new_hash = get_grades_hash(grades)
            old_hash = data.get('grades_hash', '')
            
            if old_hash and new_hash != old_hash:
                old_grades = data.get('last_grades', [])
                new_items = find_new_grades(old_grades, grades)
                
                if new_items:
                    logger.info(f"[定时任务] 发现 {len(new_items)} 门新成绩!")
                    add_log('success', f'发现 {len(new_items)} 门新成绩', username[:4] + '***')
                    
                    # 邮件通知
                    notify_email = data.get('notify_email', True)
                    if notify_email and email:
                        html = generate_grade_email(new_items)
                        ok, msg = send_email(email, f"🎓 你有 {len(new_items)} 门新成绩！", html)
                        if ok:
                            add_log('success', f'邮件发送成功 -> {email}', username[:4] + '***')
                        else:
                            add_log('error', f'邮件发送失败: {msg}', username[:4] + '***')
                    
                    # 微信通知
                    notify_wechat = data.get('notify_wechat', False)
                    user_wechat_key = data.get('wechat_key', '')
                    if notify_wechat and user_wechat_key:
                        wechat_content = generate_grade_wechat_content(new_items)
                        ok, msg = send_wechat(f"🎓 新成绩: {len(new_items)}门", wechat_content, user_wechat_key)
                        if ok:
                            add_log('success', '微信推送成功', username[:4] + '***')
                        else:
                            add_log('error', f'微信推送失败: {msg}', username[:4] + '***')
            
            subs[user_id]['grades_hash'] = new_hash
            subs[user_id]['last_grades'] = grades
            subs[user_id]['last_success'] = get_beijing_time().isoformat()
            
        except Exception as e:
            logger.error(f"[定时任务] 错误: {e}")
            SYSTEM_STATUS['last_error'] = str(e)
            add_log('error', str(e), user_id[:8] if user_id else None)
    
    save_subscriptions(subs)
    logger.info(f"[定时任务] 完成，检查了 {checked}/{len(subs)} 个用户")


def init_scheduler():
    """初始化调度器"""
    global scheduler
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(check_grades_job, 'interval', minutes=5, id='grade_check')
    scheduler.start()
    add_log('info', '系统启动')
    return scheduler


def get_scheduler():
    """获取调度器实例"""
    return scheduler
