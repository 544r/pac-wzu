"""
邮件发送服务模块
"""
import requests
from src.config import RESEND_API_KEY, SYSTEM_STATUS
from src.utils.helpers import get_beijing_time


def send_email(to_email, subject, html_content):
    """发送邮件"""
    if not RESEND_API_KEY:
        return False, "未配置邮件服务"
    try:
        resp = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'from': 'WZU成绩助手 <onboarding@resend.dev>',
                'to': [to_email],
                'subject': subject,
                'html': html_content
            },
            timeout=30
        )
        if resp.status_code == 200:
            SYSTEM_STATUS['emails_sent'] += 1
            return True, "发送成功"
        return False, resp.text
    except Exception as e:
        return False, str(e)


def generate_grade_email(new_grades):
    """生成成绩通知邮件的HTML内容"""
    rows = ""
    for g in new_grades:
        score = g.get('cj', '-')
        try:
            color = '#059669' if float(score) >= 60 else '#dc2626'
        except:
            color = '#333'
        rows += f'''<tr>
            <td style="padding:12px;border-bottom:1px solid #eee;">{g.get("kcmc", "-")}</td>
            <td style="padding:12px;border-bottom:1px solid #eee;">{g.get("xf", "-")}</td>
            <td style="padding:12px;border-bottom:1px solid #eee;color:{color};font-weight:bold;">{score}</td>
            <td style="padding:12px;border-bottom:1px solid #eee;">{g.get("jd", "-")}</td>
        </tr>'''
    
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
    <body style="font-family:-apple-system,sans-serif;background:#f5f5f5;padding:20px;">
    <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.1);">
    <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:24px;text-align:center;">
    <h1 style="color:white;margin:0;">🎓 新成绩通知</h1></div>
    <div style="padding:24px;">
    <p style="font-size:16px;">你有 <strong>{len(new_grades)}</strong> 门新成绩！</p>
    <table style="width:100%;border-collapse:collapse;margin:20px 0;">
    <thead><tr style="background:#f8f9fa;">
        <th style="padding:12px;text-align:left;">课程</th>
        <th style="padding:12px;text-align:left;">学分</th>
        <th style="padding:12px;text-align:left;">成绩</th>
        <th style="padding:12px;text-align:left;">绩点</th>
    </tr></thead>
    <tbody>{rows}</tbody></table>
    <p style="color:#999;font-size:12px;text-align:center;">查询时间: {get_beijing_time().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div></div></body></html>'''
