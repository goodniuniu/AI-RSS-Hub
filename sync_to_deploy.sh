#!/bin/bash

##############################################################################
# AI-RSS-Hub 开发到部署目录同步脚本
#
# 用途: 将开发目录的代码同步到部署目录
# 用法: ./sync_to_deploy.sh
##############################################################################

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 源目录（开发）
SOURCE_DIR="/home/sam/Github/get_news_api/AI-RSS-Hub"

# 目标目录（部署）
TARGET_DIR="/home/sam/Github/AI-RSS-Hub"

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ 错误: 源目录不存在: $SOURCE_DIR${NC}"
    exit 1
fi

# 检查目标目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}❌ 错误: 目标目录不存在: $TARGET_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   AI-RSS-Hub 代码同步工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}源目录:${NC} $SOURCE_DIR"
echo -e "${YELLOW}目标目录:${NC} $TARGET_DIR"
echo ""

# 询问是否继续
read -p "确认同步? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  同步已取消${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}📦 开始同步代码...${NC}"
echo ""

# 使用 rsync 同步
# -a: 归档模式，保留权限、时间戳等
# -v: 详细输出
# --delete: 删除目标中源没有的文件
# --exclude: 排除不需要同步的文件/目录
rsync -av --delete \
  --exclude='venv/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='*.pyd' \
  --exclude='.Python' \
  --exclude='.env' \
  --exclude='*.db' \
  --exclude='*.sqlite' \
  --exclude='*.sqlite3' \
  --exclude='*.log' \
  --exclude='*.swp' \
  --exclude='*.swo' \
  --exclude='*.swn' \
  --exclude='.DS_Store' \
  --exclude='.git/' \
  --exclude='.gitignore' \
  --exclude='.vscode/' \
  --exclude='.idea/' \
  --exclude='*.tmp' \
  "$SOURCE_DIR/" "$TARGET_DIR/"

# 检查同步结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 同步成功！${NC}"
    echo ""
    echo -e "${YELLOW}📋 同步的文件类型:${NC}"
    echo "   - Python 代码 (app/)"
    echo "   - 配置文件 (requirements.txt)"
    echo "   - 文档 (*.md, *.txt)"
    echo "   - 脚本 (*.sh)"
    echo ""
    echo -e "${YELLOW}⚠️  未同步的文件:${NC}"
    echo "   - 虚拟环境 (venv/)"
    echo "   - 环境配置 (.env)"
    echo "   - 数据库文件 (*.db)"
    echo "   - 临时文件 (__pycache__, *.log)"
    echo ""
    echo -e "${BLUE}💡 提示:${NC}"
    echo "   如果服务正在运行且使用了 --reload 参数，代码会自动重载"
    echo "   否则需要手动重启服务: Ctrl+C 停止后重新启动"
    echo ""
else
    echo ""
    echo -e "${RED}❌ 同步失败！${NC}"
    echo -e "${RED}请检查错误信息${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}同步完成！${NC}"
echo -e "${BLUE}========================================${NC}"
