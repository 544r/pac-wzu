# 使用官方 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下的所有文件到容器中
COPY . .

# 暴露 Hugging Face 默认端口 7860
EXPOSE 7860

# 启动命令
CMD ["python", "app.py"]
