#!/bin/bash
# AI-RSS-Hub 一键启动脚本

set -e  # 遇到错误立即退出

echo "================================"
echo "  AI-RSS-Hub 启动脚本"
echo "================================"
echo ""

# 1. 检查 Python 版本
echo "⏳ 检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"
echo ""

# 2. 检查/创建虚拟环境
if [ ! -d "venv" ]; then
    echo "⏳ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi
echo ""

# 3. 激活虚拟环境
echo "⏳ 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 4. 安装/更新依赖
echo "⏳ 检查并安装依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ 依赖安装完成"
echo ""

# 5. 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告：.env 文件不存在"
    echo "❌ 请先配置环境变量："
    echo "   1. 复制模板：cp .env.example .env"
    echo "   2. 编辑 .env 文件，填入你的 OPENAI_API_KEY"
    echo "   3. 重新运行此脚本"
    echo ""

    # 询问是否自动创建
    read -p "是否现在创建 .env 文件？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ .env 文件已创建，请编辑后再次运行此脚本"
        echo "📝 编辑命令：nano .env 或 vim .env"
    fi
    exit 1
else
    echo "✅ .env 文件已存在"
fi
echo ""

# 6. 检查 API Key 是否配置
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  警告：未检测到有效的 OPENAI_API_KEY"
    echo "📝 请编辑 .env 文件并填入你的 API Key"
    echo ""
fi

# 7. 显示配置信息
echo "================================"
echo "  当前配置"
echo "================================"
if grep -q "OPENAI_API_BASE" .env; then
    API_BASE=$(grep "OPENAI_API_BASE" .env | cut -d '=' -f2)
    echo "🔗 API Base: $API_BASE"
fi
if grep -q "OPENAI_MODEL" .env; then
    MODEL=$(grep "OPENAI_MODEL" .env | cut -d '=' -f2)
    echo "🤖 Model: $MODEL"
fi
echo ""

# 8. 启动应用
echo "================================"
echo "  启动应用"
echo "================================"
echo "🚀 启动 AI-RSS-Hub..."
echo "📖 API 文档: http://localhost:8000/docs"
echo "💚 健康检查: http://localhost:8000/api/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"
echo ""

# 启动服务（开发模式，支持热重载）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
