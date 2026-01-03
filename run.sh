#!/bin/bash
# AI-RSS-Hub 快速启动脚本

echo "启动 AI-RSS-Hub..."

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "警告: .env 文件不存在，请先复制 .env.example 为 .env 并配置"
    echo "执行: cp .env.example .env"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "检查依赖..."
pip install -q -r requirements.txt

# 启动应用
echo "启动应用..."
python -m app.main
