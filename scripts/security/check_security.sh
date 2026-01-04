#!/bin/bash
# 依赖安全检查脚本

echo "=== AI-RSS-Hub 依赖安全检查 ==="
echo ""

# 检查是否安装了 safety
if ! command -v safety &> /dev/null; then
    echo "正在安装 safety..."
    pip install safety
fi

# 检查是否安装了 bandit
if ! command -v bandit &> /dev/null; then
    echo "正在安装 bandit..."
    pip install bandit
fi

# 检查已知漏洞
echo "1. 检查依赖漏洞（safety）..."
safety check --file requirements.txt
echo ""

# 检查代码安全问题
echo "2. 检查代码安全问题（bandit）..."
bandit -r app/
echo ""

# 检查过期依赖
echo "3. 检查过期依赖..."
pip list --outdated
echo ""

echo "=== 检查完成 ==="
