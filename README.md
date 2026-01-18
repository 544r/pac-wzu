# 🎓 温大成绩助手 (WZU Grade Helper)

一个温州大学教务系统成绩查询和推送工具，支持邮件和微信推送新成绩通知。

## ✨ 功能特点

- 🔐 **安全登录** - 支持学号密码登录和快捷密钥登录
- 📊 **成绩查询** - 按学年学期查询成绩，支持导出 Excel
- 🎯 **GPA 计算器** - 计算当前绩点，目标绩点分析
- 📧 **邮件推送** - 新成绩自动发送邮件通知
- 💬 **微信推送** - 通过 Server酱 推送到微信
- ⏰ **定时检查** - 后台自动检查成绩更新
- 🔑 **密钥登录** - 设置快捷密钥，无需每次输入密码

## 🚀 快速部署

### 方式一：Hugging Face Spaces（推荐）

1. Fork 本项目到你的 GitHub
2. 在 [Hugging Face Spaces](https://huggingface.co/spaces) 创建新 Space
3. 选择 Docker 类型，连接你的 GitHub 仓库
4. 设置环境变量（见下方配置）
5. 部署完成！

### 方式二：本地运行

```bash
# 克隆项目
git clone https://github.com/你的用户名/pac-wzu.git
cd pac-wzu

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export SECRET_KEY="your-secret-key"
export ENCRYPT_KEY="your-16-char-key"
export RESEND_API_KEY="your-resend-api-key"
export JSONBIN_API_KEY="your-jsonbin-api-key"
export JSONBIN_BIN_ID="your-bin-id"

# 运行
python app.py
```

### 方式三：Docker

```bash
docker build -t wzu-grade-helper .
docker run -p 7860:7860 \
  -e SECRET_KEY="your-secret-key" \
  -e ENCRYPT_KEY="your-16-char-key" \
  -e RESEND_API_KEY="your-resend-api-key" \
  wzu-grade-helper
```

## ⚙️ 环境变量配置

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `SECRET_KEY` | ✅ | Flask Session 密钥 |
| `ENCRYPT_KEY` | ✅ | 密码加密密钥（16位） |
| `RESEND_API_KEY` | ❌ | [Resend](https://resend.com) 邮件 API |
| `JSONBIN_API_KEY` | ❌ | [JSONBin](https://jsonbin.io) 存储 API |
| `JSONBIN_BIN_ID` | ❌ | JSONBin Bin ID |
| `ADMIN_PASSWORD` | ❌ | 管理后台密码，默认 `admin123` |

## 📱 微信推送配置

本项目使用 [Server酱](https://sct.ftqq.com/) 实现微信推送：

1. 访问 [Server酱官网](https://sct.ftqq.com/) 注册
2. 扫码绑定微信
3. 获取 SendKey
4. 在成绩推送设置中填入你的 SendKey

## 📁 项目结构

```
pac-wzu/
├── app.py                 # 应用入口
├── Dockerfile             # Docker 配置
├── requirements.txt       # Python 依赖
└── src/
    ├── config.py          # 配置文件
    ├── routes/            # 路由模块
    │   ├── main.py        # 主页路由
    │   ├── api.py         # API 接口
    │   └── admin.py       # 管理后台
    ├── services/          # 业务逻辑
    │   ├── spider.py      # 教务系统爬虫
    │   ├── email.py       # 邮件服务
    │   ├── wechat.py      # 微信推送
    │   ├── gpa.py         # GPA 计算
    │   └── scheduler.py   # 定时任务
    ├── storage/           # 数据存储
    │   ├── jsonbin.py     # JSONBin 云存储
    │   └── cache.py       # 本地缓存
    ├── templates/         # HTML 模板
    │   ├── login.py
    │   ├── dashboard.py
    │   └── admin.py
    └── utils/             # 工具函数
        ├── crypto.py      # 加密解密
        └── helpers.py     # 辅助函数
```

## 🔒 安全说明

- 所有密码使用 AES 加密存储
- 不存储明文密码
- Session 使用安全密钥签名
- 建议定期更换 ENCRYPT_KEY

## 📝 开源协议

MIT License

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Resend](https://resend.com/) - 邮件服务
- [Server酱](https://sct.ftqq.com/) - 微信推送
- [JSONBin](https://jsonbin.io/) - 云存储

## ⚠️ 免责声明

本项目仅供学习交流使用，请勿用于任何商业或非法用途。使用本项目产生的任何后果由用户自行承担。
