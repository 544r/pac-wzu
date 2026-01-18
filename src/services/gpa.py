"""
GPA 计算器模块
"""


def calculate_gpa(grades):
    """
    计算加权平均绩点
    
    Args:
        grades: 成绩列表，每项包含 'xf'(学分) 和 'jd'(绩点)
    
    Returns:
        dict: 包含 GPA 统计信息
    """
    if not grades:
        return {
            'gpa': 0,
            'total_credits': 0,
            'course_count': 0,
            'passed_count': 0,
            'failed_count': 0,
            'excellent_count': 0,
            'grade_distribution': {}
        }
    
    total_credits = 0
    weighted_sum = 0
    passed_count = 0
    failed_count = 0
    excellent_count = 0  # 90分以上
    
    # 成绩分布
    distribution = {
        '优秀(90-100)': 0,
        '良好(80-89)': 0,
        '中等(70-79)': 0,
        '及格(60-69)': 0,
        '不及格(<60)': 0
    }
    
    for g in grades:
        try:
            xf = float(g.get('xf', 0) or 0)
            jd = float(g.get('jd', 0) or 0)
            cj_str = g.get('cj', '')
            
            # 尝试解析成绩
            try:
                cj = float(cj_str)
            except (ValueError, TypeError):
                # 可能是等级制成绩（优、良、中、及格、不及格）
                grade_map = {'优': 95, '优秀': 95, '良': 85, '良好': 85, 
                            '中': 75, '中等': 75, '及格': 65, '合格': 65,
                            '不及格': 50, '不合格': 50}
                cj = grade_map.get(cj_str, 0)
            
            if xf > 0:
                total_credits += xf
                weighted_sum += jd * xf
                
                # 统计及格/不及格
                if cj >= 60:
                    passed_count += 1
                else:
                    failed_count += 1
                
                # 统计优秀
                if cj >= 90:
                    excellent_count += 1
                
                # 成绩分布
                if cj >= 90:
                    distribution['优秀(90-100)'] += 1
                elif cj >= 80:
                    distribution['良好(80-89)'] += 1
                elif cj >= 70:
                    distribution['中等(70-79)'] += 1
                elif cj >= 60:
                    distribution['及格(60-69)'] += 1
                else:
                    distribution['不及格(<60)'] += 1
                    
        except (ValueError, TypeError):
            continue
    
    gpa = round(weighted_sum / total_credits, 4) if total_credits > 0 else 0
    
    return {
        'gpa': gpa,
        'total_credits': round(total_credits, 1),
        'course_count': len(grades),
        'passed_count': passed_count,
        'failed_count': failed_count,
        'excellent_count': excellent_count,
        'pass_rate': round(passed_count / len(grades) * 100, 1) if grades else 0,
        'excellent_rate': round(excellent_count / len(grades) * 100, 1) if grades else 0,
        'grade_distribution': distribution
    }


def calculate_target_gpa(current_grades, target_gpa, remaining_credits):
    """
    计算达到目标 GPA 需要的平均绩点
    
    Args:
        current_grades: 当前成绩列表
        target_gpa: 目标 GPA
        remaining_credits: 剩余学分
    
    Returns:
        dict: 目标分析结果
    """
    current = calculate_gpa(current_grades)
    current_gpa = current['gpa']
    current_credits = current['total_credits']
    
    if remaining_credits <= 0:
        return {
            'achievable': current_gpa >= target_gpa,
            'current_gpa': current_gpa,
            'target_gpa': target_gpa,
            'message': '无剩余学分' if current_gpa >= target_gpa else '已无法达到目标'
        }
    
    # 计算需要的总绩点
    total_credits = current_credits + remaining_credits
    needed_total_points = target_gpa * total_credits
    current_points = current_gpa * current_credits
    needed_points = needed_total_points - current_points
    needed_avg_gpa = needed_points / remaining_credits
    
    # 判断是否可实现（绩点最高5.0）
    achievable = needed_avg_gpa <= 5.0
    
    # 给出建议
    if needed_avg_gpa <= 0:
        message = f'🎉 你已经达到目标 GPA {target_gpa}！继续保持！'
    elif needed_avg_gpa <= 3.0:
        message = f'💪 目标可达！剩余课程平均绩点需要 {needed_avg_gpa:.2f}（相当于平均75分左右）'
    elif needed_avg_gpa <= 4.0:
        message = f'📚 需要努力！剩余课程平均绩点需要 {needed_avg_gpa:.2f}（相当于平均85分左右）'
    elif needed_avg_gpa <= 5.0:
        message = f'🔥 挑战较大！剩余课程平均绩点需要 {needed_avg_gpa:.2f}（需要大部分90分以上）'
    else:
        message = f'😢 目标 {target_gpa} 已无法达到，建议调整目标至 {current_gpa + 0.3:.2f}'
    
    return {
        'achievable': achievable,
        'current_gpa': round(current_gpa, 3),
        'target_gpa': target_gpa,
        'current_credits': current_credits,
        'remaining_credits': remaining_credits,
        'needed_avg_gpa': round(max(0, needed_avg_gpa), 3),
        'message': message
    }


def get_gpa_level(gpa):
    """
    获取 GPA 等级评价
    """
    if gpa >= 4.5:
        return {'level': '卓越', 'emoji': '🏆', 'color': '#FFD700'}
    elif gpa >= 4.0:
        return {'level': '优秀', 'emoji': '🌟', 'color': '#10b981'}
    elif gpa >= 3.5:
        return {'level': '良好', 'emoji': '👍', 'color': '#3b82f6'}
    elif gpa >= 3.0:
        return {'level': '中等', 'emoji': '📚', 'color': '#f59e0b'}
    elif gpa >= 2.0:
        return {'level': '及格', 'emoji': '💪', 'color': '#f97316'}
    else:
        return {'level': '需努力', 'emoji': '📖', 'color': '#ef4444'}
