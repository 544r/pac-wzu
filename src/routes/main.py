"""
主路由模块 - 页面路由
"""
from flask import Blueprint, session, redirect, url_for
from src.templates import LOGIN_HTML, DASHBOARD_HTML, ADMIN_HTML

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首页/登录页"""
    if 'wzu_cookies' in session:
        return redirect(url_for('main.dashboard'))
    return LOGIN_HTML


@main_bp.route('/dashboard')
def dashboard():
    """仪表盘页面"""
    if 'wzu_cookies' not in session:
        return redirect(url_for('main.index'))
    return DASHBOARD_HTML


@main_bp.route('/admin')
def admin():
    """管理后台页面"""
    return ADMIN_HTML


@main_bp.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('main.index'))
