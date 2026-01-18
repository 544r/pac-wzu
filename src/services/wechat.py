"""
微信推送模块 (Server酱)

使用说明:
1. 访问 https://sct.ftqq.com/ 注册并获取 SendKey
2. 每个用户在订阅时填写自己的 SendKey
"""
import requests
import logging
from src.config import SERVERCHAN_KEY, SYSTEM_STATUS
from src.utils.helpers import get_beijing_time

logger = logging.getLogger(__name__)


def send_wechat(title, content, key=None, short=None):
    """
    发送微信推送 (Server酱)
    
    Args:
        title: 消息标题（必填）
        content: 消息内容，支持 Markdown 格式
        key: 用户的 Server酱 SendKey，如果不传则使用全局配置
        short: 消息卡片描述，会在微信消息卡片上显示
    
    Returns:
        tuple: (成功标志, 消息)
    """
    send_key = key or SERVERCHAN_KEY
    if not send_key:
        return False, "未配置微信推送 Key"
    
    try:
        url = f"https://sctapi.ftqq.com/{send_key}.send"
        
        data = {
            'title': title,
            'desp': content
        }
        
        if short:
            data['short'] = short
        
        resp = requests.post(url, data=data, timeout=10)
        result = resp.json()
        
        if result.get('code') == 0:
            SYSTEM_STATUS['wechat_sent'] += 1
            logger.info(f"微信推送成功: {title}")
            return True, "发送成功"
        else:
            error_msg = result.get('message', '未知错误')
            logger.error(f"微信推送失败: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        logger.error(f"微信推送异常: {e}")
        return False, str(e)


def generate_grade_wechat_content(new_grades):
    """
    生成成绩通知的微信消息内容（Markdown格式）
    
    Args:
        new_grades: 新成绩列表
    
    Returns:
        str: Markdown 格式的消息内容
    """
    content = f"## 🎓 新成绩通知\n\n"
    content += f"你有 **{len(new_grades)}** 门新成绩！\n\n"
    content += "| 课程 | 学分 | 成绩 | 绩点 |\n"
    content += "|------|------|------|------|\n"
    
    for g in new_grades:
        kcmc = g.get('kcmc', '-')
        xf = g.get('xf', '-')
        cj = g.get('cj', '-')
        jd = g.get('jd', '-')
        
        # 添加及格/不及格标记
        try:
            score = float(cj)
            status = "✅" if score >= 60 else "❌"
        except:
            status = ""
        
        content += f"| {kcmc} | {xf} | {cj} {status} | {jd} |\n"
    
    content += f"\n---\n"
    content += f"📅 查询时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return content


def generate_gpa_wechat_content(gpa_info):
    """
    生成 GPA 报告的微信消息内容
    
    Args:
        gpa_info: GPA 统计信息
    
    Returns:
        str: Markdown 格式的消息内容
    """
    content = f"## 📊 GPA 分析报告\n\n"
    content += f"### 当前 GPA: **{gpa_info['gpa']:.3f}**\n\n"
    content += f"- 📚 总课程数: {gpa_info['course_count']}\n"
    content += f"- 📝 总学分: {gpa_info['total_credits']}\n"
    content += f"- ✅ 及格: {gpa_info['passed_count']} 门 ({gpa_info['pass_rate']}%)\n"
    content += f"- ⭐ 优秀(90+): {gpa_info['excellent_count']} 门 ({gpa_info['excellent_rate']}%)\n"
    
    if gpa_info['failed_count'] > 0:
        content += f"- ❌ 不及格: {gpa_info['failed_count']} 门\n"
    
    content += f"\n### 成绩分布\n\n"
    for level, count in gpa_info['grade_distribution'].items():
        if count > 0:
            content += f"- {level}: {count} 门\n"
    
    content += f"\n---\n"
    content += f"📅 生成时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return content
