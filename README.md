# 🎓 温大成绩助手 (WZU Grade Helper)

一个温州大学教务系统成绩查询和推送工具，支持邮件和微信推送新成绩通知。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌐 在线体验

**直接使用**：https://huggingface.co/spaces/544r/wzu-my-socres

## ✨ 功能特点

- 🔐 **安全登录** - 支持学号密码登录和快捷密钥登录
- 📊 **成绩查询** - 按学年学期查询成绩，支持导出 Excel
- 🎯 **GPA 计算器** - 计算当前绩点，目标绩点分析
- 📧 **邮件推送** - 新成绩自动发送邮件通知（Resend）
- 💬 **微信推送** - 通过 Server酱 推送到微信（每个用户独立配置）
- ⏰ **定时检查** - 后台每5分钟自动检查成绩更新
- 🔑 **密钥登录** - 设置快捷密钥，无需每次输入密码
- 📡 **健康检查** - 提供 API 健康检查端点
- 🛠️ **管理后台** - 查看系统状态、订阅用户、日志等

## 🚀 快速部署

### 方式一：复制我的 Space（最简单 ⭐）

1. 访问 https://huggingface.co/spaces/544r/wzu-my-socres
2. 点击右上角 **⋮** → **Duplicate this Space**
3. 填写你的 Space 名称
4. 设置环境变量（Settings → Variables and secrets）
5. 点击 **Duplicate Space**，完成！

### 方式二：本地运行

```bash
# 克隆项目
git clone https://github.com/你的用户名/wzu-grade-helper.git
cd wzu-grade-helper

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（Linux/Mac）
export SECRET_KEY="your-secret-key"
export ENCRYPT_KEY="your-16-char-key!"
export RESEND_API_KEY="re_xxxxxxxx"
export ADMIN_PASSWORD="your-admin-password"

# 设置环境变量（Windows PowerShell）
$env:SECRET_KEY="your-secret-key"
$env:ENCRYPT_KEY="your-16-char-key!"
$env:RESEND_API_KEY="re_xxxxxxxx"
$env:ADMIN_PASSWORD="your-admin-password"

# 运行
python app.py
```

访问 http://localhost:7860

### 方式三：Docker

```bash
docker build -t wzu-grade-helper .
docker run -p 7860:7860 \
  -e SECRET_KEY="your-secret-key" \
  -e ENCRYPT_KEY="your-16-char-key!" \
  -e RESEND_API_KEY="re_xxxxxxxx" \
  -e ADMIN_PASSWORD="your-admin-password" \
  wzu-grade-helper
```

## ⚙️ 环境变量配置

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `SECRET_KEY` | ✅ | `wzu-grade-helper-secret-key-2024` | Flask Session 密钥，建议修改为随机字符串 |
| `ENCRYPT_KEY` | ✅ | `wzu-grade-helper-encrypt-key-32` | 密码 AES 加密密钥，建议32位字符串 |
| `ADMIN_PASSWORD` | ❌ | `admin123` | 管理后台 `/admin` 登录密码 |
| `RESEND_API_KEY` | ❌ | - | [Resend](https://resend.com) 邮件服务 API Key |
| `JSONBIN_API_KEY` | ❌ | - | [JSONBin](https://jsonbin.io) 云存储 API Key |
| `JSONBIN_BIN_ID` | ❌ | - | JSONBin Bin ID，用于持久化存储订阅数据 |
| `SERVERCHAN_KEY` | ❌ | - | [Server酱](https://sct.ftqq.com/) 全局 SendKey（可选，用户可单独配置） |

### 获取 API Key 教程

1. **Resend（邮件服务）**
   - 访问 https://resend.com 注册
   - 创建 API Key，格式如 `re_xxxxxxxx`
   - 需要验证发送域名或使用 `onboarding@resend.dev` 测试

2. **JSONBin（数据持久化）**
   - 访问 https://jsonbin.io 注册
   - 创建一个 Bin，初始内容：`{"subscriptions": {}, "pins": {}, "logs": []}`
   - 复制 Bin ID 和 API Key

3. **Server酱（微信推送）**
   - 访问 https://sct.ftqq.com/ 注册
   - 微信扫码绑定
   - 获取 SendKey
   - **注意**：每个用户在前端填写自己的 SendKey，无需配置全局环境变量

## 🔗 API 接口

### 公开接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 登录页面 |
| `/dashboard` | GET | 成绩仪表盘（需登录） |
| `/admin` | GET | 管理后台 |
| `/api/health` | GET | 健康检查，返回系统状态 |

### 用户接口（需登录）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/login` | POST | 学号密码登录 |
| `/api/pin-login` | POST | 密钥登录 |
| `/api/grades` | POST | 查询成绩 |
| `/api/subscribe` | POST | 开启成绩推送 |
| `/api/unsubscribe` | POST | 取消推送 |
| `/api/subscribe/status` | GET | 获取订阅状态 |
| `/api/pin/set` | POST | 设置快捷密钥 |
| `/api/pin/delete` | POST | 删除密钥 |
| `/api/pin/status` | GET | 密钥状态 |
| `/api/test-email` | POST | 测试邮件发送 |
| `/api/test-wechat` | POST | 测试微信推送 |
| `/api/gpa/calculate` | POST | 计算 GPA |
| `/api/gpa/target` | POST | 目标绩点分析 |

### 管理接口（需管理员登录）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/admin/login` | POST | 管理员登录 |
| `/api/admin/status` | GET | 系统状态 |
| `/api/admin/subscribers` | GET | 订阅用户列表 |
| `/api/admin/pins` | GET | 密钥用户列表 |
| `/api/admin/logs` | GET | 系统日志 |
| `/api/admin/run-now` | POST | 立即执行检查任务 |

## 📱 微信推送配置

本项目使用 [Server酱](https://sct.ftqq.com/) 实现微信推送，**每个用户独立配置自己的 SendKey**：

1. 访问 [Server酱官网](https://sct.ftqq.com/) 注册
2. 微信扫码绑定
3. 复制你的 SendKey
4. 在成绩推送设置中填入 SendKey
5. 点击"测试微信"验证
6. 勾选"微信推送"并保存

## 📁 项目结构

```
wzu-grade-helper/
├── app.py                 # 应用入口
├── Dockerfile             # Docker 配置
├── requirements.txt       # Python 依赖
├── README.md              # 项目说明
├── LICENSE                # 开源协议
├── .gitignore             # Git 忽略文件
└── src/
    ├── __init__.py
    ├── config.py          # 配置文件
    ├── routes/            # 路由模块
    │   ├── __init__.py
    │   ├── main.py        # 主页路由
    │   ├── api.py         # 用户 API
    │   └── admin.py       # 管理后台 API
    ├── services/          # 业务逻辑
    │   ├── __init__.py
    │   ├── spider.py      # 教务系统爬虫
    │   ├── email.py       # 邮件服务
    │   ├── wechat.py      # 微信推送
    │   ├── gpa.py         # GPA 计算
    │   └── scheduler.py   # 定时任务调度
    ├── storage/           # 数据存储
    │   ├── __init__.py
    │   ├── jsonbin.py     # JSONBin 云存储
    │   └── cache.py       # 本地缓存
    ├── templates/         # HTML 模板
    │   ├── __init__.py
    │   ├── login.py       # 登录页
    │   ├── dashboard.py   # 仪表盘
    │   └── admin.py       # 管理后台
    └── utils/             # 工具函数
        ├── __init__.py
        ├── crypto.py      # AES 加密解密
        └── helpers.py     # 辅助函数
```

## 🔒 安全说明

- ✅ 所有密码使用 **AES-256 加密**存储
- ✅ 不存储明文密码
- ✅ Session 使用安全密钥签名
- ✅ 管理后台需要密码登录
- ✅ 微信 SendKey 脱敏显示
- ⚠️ 建议部署时修改默认的 `SECRET_KEY` 和 `ENCRYPT_KEY`
- ⚠️ 建议修改默认管理员密码 `ADMIN_PASSWORD`

## 📝 开源协议

MIT License - 可自由使用、修改、分发

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [APScheduler](https://apscheduler.readthedocs.io/) - 定时任务
- [Resend](https://resend.com/) - 邮件服务
- [Server酱](https://sct.ftqq.com/) - 微信推送
- [JSONBin](https://jsonbin.io/) - 云存储
- [PyCryptodome](https://pycryptodome.readthedocs.io/) - 加密库

## ⚠️ 免责声明

本项目仅供学习交流使用，请勿用于任何商业或非法用途。使用本项目需遵守温州大学相关规定，使用本项目产生的任何后果由用户自行承担。

---

**如果觉得有用，欢迎 ⭐ Star 支持！**
