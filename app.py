"""
温州大学成绩助手 - 主入口文件
WZU Grade Helper - Main Entry Point

模块化结构:
- src/config.py          配置和全局状态
- src/utils/             工具函数（加密、时间、哈希）
- src/storage/           数据存储（JSONBin、本地缓存）
- src/services/          业务服务（爬虫、邮件、定时任务）
- src/templates/         HTML模板（登录、仪表盘、管理后台）
- src/routes/            路由（主路由、API、管理后台）
"""

import logging
from flask import Flask

from src.config import SECRET_KEY, PERMANENT_SESSION_LIFETIME, RESEND_API_KEY, JSONBIN_API_KEY, JSONBIN_BIN_ID
from src.storage.jsonbin import sync_from_cloud
from src.storage.cache import add_log
from src.services.scheduler import init_scheduler
from src.routes import main_bp, api_bp, admin_bp

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 创建 Flask 应用 ====================
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = PERMANENT_SESSION_LIFETIME

# ==================== 注册蓝图 ====================
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)

# ==================== 初始化 ====================
def init_app():
    """初始化应用"""
    # 启动时同步云端数据
    if JSONBIN_API_KEY and JSONBIN_BIN_ID:
        sync_from_cloud()
        logger.info("✅ JSONBin 持久化已启用")
    else:
        logger.warning("⚠️ 未配置 JSONBin，数据不会持久化")
    
    # 初始化定时任务调度器
    init_scheduler()

# 在导入时初始化
init_app()

# ==================== 主程序入口 ====================
if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🎓 温大成绩助手启动")
    logger.info(f"📧 Resend: {'✅' if RESEND_API_KEY else '❌'}")
    logger.info(f"💾 JSONBin: {'✅' if JSONBIN_API_KEY and JSONBIN_BIN_ID else '❌'}")
    logger.info("=" * 50)
    app.run(host='0.0.0.0', port=7860)
