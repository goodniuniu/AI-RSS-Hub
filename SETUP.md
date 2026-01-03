# AI-RSS-Hub 本地测试环境搭建指南

## 📝 环境要求

- Python 3.10 或以上
- pip 包管理器

## 🚀 快速搭建步骤

### 1️⃣ 创建 Python 虚拟环境

在项目根目录 `AI-RSS-Hub/` 下执行：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate

# Windows:
# venv\Scripts\activate
```

激活成功后，终端提示符前会显示 `(venv)`。

### 2️⃣ 安装依赖包

```bash
# 确保 pip 是最新版本
pip install --upgrade pip

# 安装所有依赖
pip install -r requirements.txt
```

预计安装时间：1-3 分钟（取决于网络速度）

### 3️⃣ 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env
# 或使用你喜欢的编辑器：vim、code 等
```

**必填配置项：**

```bash
# LLM API Key（必填）
OPENAI_API_KEY=sk-your-api-key-here

# 如果使用 DeepSeek
# OPENAI_API_KEY=sk-your-deepseek-key
# OPENAI_API_BASE=https://api.deepseek.com
# OPENAI_MODEL=deepseek-chat
```

**可选配置项（使用默认值即可）：**

```bash
# 数据库路径（默认当前目录）
DATABASE_URL=sqlite:///./ai_rss_hub.db

# RSS 抓取间隔（小时）
FETCH_INTERVAL_HOURS=1

# 超时设置（秒）
REQUEST_TIMEOUT=30
LLM_TIMEOUT=30

# 摘要长度限制
SUMMARY_MAX_LENGTH=100
```

### 4️⃣ 启动应用

```bash
# 方式 1：直接运行
python -m app.main

# 方式 2：使用 uvicorn（推荐开发环境）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 3：使用启动脚本
./run.sh
```

### 5️⃣ 验证运行

启动成功后，你会看到：

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
应用启动中...
数据库表创建成功
成功插入 3 个默认 RSS 源
调度器已启动，任务将每 1 小时执行一次
应用启动完成
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

访问以下 URL 验证：

- 🏠 根路径：http://localhost:8000/
- 📖 API 文档：http://localhost:8000/docs
- 💚 健康检查：http://localhost:8000/api/health
- 📊 系统状态：http://localhost:8000/api/status

### 6️⃣ 测试 API

**获取 Feed 列表：**
```bash
curl http://localhost:8000/api/feeds
```

**获取文章列表：**
```bash
curl http://localhost:8000/api/articles?limit=10
```

**添加新的 RSS 源：**
```bash
curl -X POST http://localhost:8000/api/feeds \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub Blog",
    "url": "https://github.blog/feed/",
    "category": "tech",
    "is_active": true
  }'
```

## 🔧 常见问题

### Q1: 虚拟环境激活失败？

**Windows PowerShell 执行策略问题：**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q2: 依赖安装失败？

尝试使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: LLM API 调用失败？

检查 .env 配置：
```bash
# 确保 API Key 正确
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows

# 测试 API 连接（使用 curl）
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Q4: 数据库文件在哪里？

默认位置：`AI-RSS-Hub/ai_rss_hub.db`

查看数据库内容（需要安装 sqlite3）：
```bash
sqlite3 ai_rss_hub.db
# 在 sqlite 提示符下：
.tables           # 查看所有表
SELECT * FROM feed;     # 查看 Feed 数据
SELECT * FROM article;  # 查看 Article 数据
.quit            # 退出
```

### Q5: 如何手动触发一次 RSS 抓取？

方法 1：重启应用（启动时会执行一次）

方法 2：调用内部函数（Python Shell）：
```bash
python
>>> from sqlmodel import Session
>>> from app.database import engine
>>> from app.services.rss_fetcher import fetch_all_feeds
>>> with Session(engine) as session:
...     stats = fetch_all_feeds(session)
...     print(stats)
```

## 🛑 停止应用

在终端按 `Ctrl + C` 停止服务。

## 🧹 清理环境

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境（如需重建）
rm -rf venv

# 删除数据库（清空数据）
rm ai_rss_hub.db
```

## 📚 下一步

1. 在 http://localhost:8000/docs 体验交互式 API 文档
2. 添加更多 RSS 源
3. 查看 AI 生成的文章摘要
4. 根据需求修改定时任务间隔

## 💡 开发提示

- 使用 `--reload` 参数可以在代码修改后自动重启服务
- 查看 logs 了解定时任务执行情况
- 修改 `app/config.py` 中的日志级别为 `DEBUG` 查看更详细的信息
