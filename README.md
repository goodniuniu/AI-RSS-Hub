# AI-RSS-Hub

基于 FastAPI 和 SQLModel 构建的智能 RSS 聚合系统，自动抓取 RSS 源并使用 AI 生成文章摘要。

## 功能特性

### 核心功能
- 📡 **自动抓取**：定期抓取配置的 RSS 源，默认每小时执行一次
- 🤖 **AI 总结**：使用 LLM API 自动生成文章摘要（100字以内）
- 💾 **数据持久化**：使用 SQLite 存储 Feed 和 Article 数据
- 🔌 **RESTful API**：提供完整的 API 接口用于管理和查询
- ⏰ **后台任务**：使用 APScheduler 实现非阻塞的定时任务
- 🌐 **兼容性强**：支持 OpenAI、DeepSeek、Gemini 等兼容接口

### 安全功能 🔒
- 🔑 **API Token 认证**：保护敏感操作（添加RSS源、手动抓取）
- 🚦 **速率限制**：防止 API 滥用，可配置请求频率限制
- 🛡️ **安全响应头**：包含 X-Content-Type-Options、X-Frame-Options 等安全头
- ✅ **输入验证**：严格的 URL 格式验证和数据清理
- 📝 **安全日志**：记录认证失败、速率限制等安全事件

### 生产环境 🚀
- 🔄 **系统服务**：支持 systemd 服务配置，开机自启动
- 🔧 **服务管理**：提供便捷的服务管理脚本
- 📊 **日志管理**：集成 journalctl 日志查看
- ⚡ **自动恢复**：服务异常时自动重启

## 技术栈

- **Web 框架**：FastAPI
- **ORM**：SQLModel + SQLAlchemy
- **数据库**：SQLite
- **RSS 解析**：feedparser
- **LLM 客户端**：openai（支持自定义 base_url）
- **任务调度**：APScheduler
- **安全认证**：Bearer Token
- **速率限制**：slowapi
- **系统服务**：systemd

## 项目结构

```
AI-RSS-Hub/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── models.py            # SQLModel 数据模型
│   ├── database.py          # 数据库配置
│   ├── crud.py              # 数据库操作
│   ├── config.py            # 配置管理
│   ├── scheduler.py         # APScheduler 调度器
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API 路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rss_fetcher.py   # RSS 抓取逻辑
│   │   └── summarizer.py    # AI 总结逻辑
│   └── security/            # 安全模块
│       ├── __init__.py
│       ├── auth.py          # API Token 认证
│       ├── rate_limiter.py  # 速率限制
│       ├── middleware.py    # 安全中间件
│       ├── validators.py    # 输入验证
│       └── logger.py        # 安全日志
├── scripts/                 # 工具脚本
│   ├── check_security.sh    # 安全检查脚本
│   └── generate_token.py    # Token 生成工具
├── tests/                   # 测试文件
├── install_service.sh       # 系统服务安装脚本
├── manage_service.sh        # 服务管理脚本
├── .env.example             # 环境变量示例
├── requirements.txt         # 依赖列表
└── README.md               # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
cd AI-RSS-Hub
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```bash
# 必填：LLM API Key
OPENAI_API_KEY=your_api_key_here

# 必填：API 认证 Token（用于保护敏感操作）
API_TOKEN=your_secure_token_here

# 可选：自定义 API Base URL
# OpenAI (默认)
OPENAI_API_BASE=https://api.openai.com/v1

# DeepSeek
# OPENAI_API_BASE=https://api.deepseek.com

# 可选：模型名称
OPENAI_MODEL=gpt-3.5-turbo

# 可选：CORS 允许的域名（逗号分隔）
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# 可选：其他配置
FETCH_INTERVAL_HOURS=1
DATABASE_URL=sqlite:///./ai_rss_hub.db
REQUEST_TIMEOUT=30
LLM_TIMEOUT=30
SUMMARY_MAX_LENGTH=100
```

**生成 API Token：**
```bash
python scripts/generate_token.py
```

### 3. 运行应用

```bash
# 方式 1：直接运行
python -m app.main

# 方式 2：使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

应用启动后：
- API 文档：http://localhost:8000/docs
- 系统状态：http://localhost:8000/api/status

## API 接口

### 1. 添加 RSS 源 ⚠️ 需要认证

```bash
POST /api/feeds
Content-Type: application/json
Authorization: Bearer YOUR_API_TOKEN

{
  "name": "Hacker News",
  "url": "https://hnrss.org/frontpage",
  "category": "tech",
  "is_active": true
}
```

### 2. 获取所有 RSS 源

```bash
GET /api/feeds?active_only=true
```

### 3. 获取文章列表

```bash
# 获取最近 50 篇文章
GET /api/articles?limit=50

# 按分类筛选
GET /api/articles?category=tech&limit=20

# 获取最近 7 天的文章
GET /api/articles?days=7&limit=100
```

### 4. 手动触发抓取 ⚠️ 需要认证

```bash
POST /api/feeds/fetch
Authorization: Bearer YOUR_API_TOKEN
```

### 5. 健康检查

```bash
GET /api/health
```

### 6. 系统状态

```bash
GET /api/status
```

**注意**：标有 ⚠️ 的接口需要在请求头中包含 `Authorization: Bearer YOUR_API_TOKEN`

## 初始数据

系统启动时会自动插入 3 个著名的科技类 RSS 源：

1. **Hacker News**：https://hnrss.org/frontpage
2. **TechCrunch**：https://techcrunch.com/feed/
3. **Ars Technica**：https://feeds.arstechnica.com/arstechnica/index

## 使用不同的 LLM 提供商

### DeepSeek

```bash
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_API_BASE=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

### Gemini（通过代理）

如果你有 Gemini 的 OpenAI 兼容代理：

```bash
OPENAI_API_KEY=your_gemini_api_key
OPENAI_API_BASE=https://your-gemini-proxy.com/v1
OPENAI_MODEL=gemini-pro
```

## 自定义配置

所有配置项都可以通过环境变量或 `.env` 文件设置：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `OPENAI_API_KEY` | LLM API Key（必填） | None |
| `API_TOKEN` | API 认证 Token（必填） | None |
| `OPENAI_API_BASE` | LLM API Base URL | https://api.openai.com/v1 |
| `OPENAI_MODEL` | LLM 模型名称 | gpt-3.5-turbo |
| `DATABASE_URL` | 数据库连接 URL | sqlite:///./ai_rss_hub.db |
| `FETCH_INTERVAL_HOURS` | RSS 抓取间隔（小时） | 1 |
| `REQUEST_TIMEOUT` | HTTP 请求超时（秒） | 30 |
| `LLM_TIMEOUT` | LLM API 超时（秒） | 30 |
| `SUMMARY_MAX_LENGTH` | 摘要最大长度（字符） | 100 |
| `CORS_ORIGINS` | CORS 允许的域名（逗号分隔） | http://localhost:3000 |
| `RATE_LIMIT_ENABLED` | 是否启用速率限制 | true |
| `RATE_LIMIT_PER_MINUTE` | 每分钟请求限制 | 60 |

## 错误处理

系统包含完善的错误处理机制：

- **RSS 解析失败**：记录警告日志，不影响其他源的抓取
- **LLM 调用超时**：返回默认提示，文章仍会保存
- **API 调用失败**：返回友好的错误信息
- **数据库操作异常**：自动回滚事务

## 日志

应用使用 Python 标准 logging 模块，日志格式：

```
2025-12-25 10:00:00 - app.scheduler - INFO - 定时任务开始执行
2025-12-25 10:00:05 - app.services.rss_fetcher - INFO - 新增文章: Sample Article...
2025-12-25 10:00:10 - app.services.summarizer - INFO - AI 总结成功
```

## 生产环境部署 🚀

### 使用 systemd 服务（推荐）

项目包含 systemd 服务配置，支持开机自启动和自动重启。

**快速安装：**

```bash
# 1. 安装服务
sudo bash install_service.sh

# 2. 检查服务状态
sudo systemctl status ai-rss-hub

# 3. 查看日志
sudo journalctl -u ai-rss-hub -f
```

**服务管理：**

```bash
# 使用管理脚本（推荐）
./manage_service.sh          # 交互式菜单
./manage_service.sh status   # 查看状态
./manage_service.sh start    # 启动服务
./manage_service.sh stop     # 停止服务
./manage_service.sh restart  # 重启服务
./manage_service.sh logs     # 查看日志

# 或使用 systemd 命令
sudo systemctl start ai-rss-hub
sudo systemctl stop ai-rss-hub
sudo systemctl restart ai-rss-hub
sudo systemctl enable ai-rss-hub    # 开机自启动
sudo systemctl disable ai-rss-hub   # 禁用自启动
```

**日志查看：**

```bash
# 实时查看日志
sudo journalctl -u ai-rss-hub -f

# 查看最近100行
sudo journalctl -u ai-rss-hub -n 100

# 查看今天的日志
sudo journalctl -u ai-rss-hub --since today
```

详细部署指南请参考：[AUTO_START_GUIDE.md](AUTO_START_GUIDE.md)

## 开发建议

1. **开发环境**：启动时使用 `--reload` 参数启用热重载
2. **生产环境**：修改 CORS 配置，限制允许的域名
3. **数据库迁移**：如需使用 PostgreSQL 等数据库，修改 `DATABASE_URL` 即可
4. **性能优化**：考虑使用 Redis 缓存文章列表
5. **扩展功能**：可以添加用户系统、订阅管理等功能
6. **安全配置**：
   - 生产环境务必设置强密码作为 API_TOKEN
   - 启用速率限制防止 API 滥用
   - 配置正确的 CORS_ORIGINS
   - 定期检查日志监控异常访问

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_security.py

# 查看测试覆盖率
pytest --cov=app tests/
```

## 工具脚本

```bash
# 生成安全的 API Token
python scripts/generate_token.py

# 安全检查
bash scripts/check_security.sh

# 重新生成所有文章摘要
python regenerate_summaries.py
```

## 详细文档

- 📖 [完整配置指南](SETUP.md) - 本地测试环境搭建
- 🚀 [生产部署指南](AUTO_START_GUIDE.md) - systemd 服务配置和自动启动
- 📝 [项目理解文档](PROJECT_UNDERSTANDING.md) - 深入了解项目架构
- 🔐 [安全文档](.env.security) - 安全配置建议
- 📤 [客户端使用指南](CLIENT_USAGE_GUIDE.md) - 如何使用 API
- 📮 [Postman 集合](POSTMAN_GUIDE.md) - API 测试集合
- ✅ [重启测试指南](REBOOT_TEST_GUIDE.md) - 验证服务自动启动

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

Built with ❤️ by [goodniuniu](https://github.com/goodniuniu)

---

**项目地址**：https://github.com/goodniuniu/AI-RSS-Hub
