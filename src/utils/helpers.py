"""
通用工具函数
"""
import json
import hashlib
from datetime import datetime
from src.config import BEIJING_TZ


def get_beijing_time():
    """获取北京时间"""
    return datetime.now(BEIJING_TZ)


def get_grades_hash(grades):
    """计算成绩列表的哈希值"""
    if not grades:
        return ""
    sorted_grades = sorted(grades, key=lambda x: x.get('kcmc', ''))
    content = json.dumps(sorted_grades, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(content.encode()).hexdigest()


def find_new_grades(old_grades, new_grades):
    """找出新增的成绩"""
    if not old_grades:
        return []
    old_courses = {g.get('kcmc', '') for g in old_grades}
    return [g for g in new_grades if g.get('kcmc', '') not in old_courses]
