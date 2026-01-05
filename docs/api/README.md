# API 文档中心

AI-RSS-Hub RESTful API 完整文档目录。

---

## 📖 核心文档

### [API 参考手册](API_GUIDE.md) ⭐ **必读**

**完整的 API 端点参考**

- 📋 所有端点详细说明
- 🔐 认证方式和安全机制
- 📦 请求/响应格式
- ⚠️ 错误处理
- 💻 代码示例（Python, JavaScript, cURL）
- 🎯 最佳实践

**适合**: 首次集成、日常查阅

**阅读时间**: 15-20 分钟

---

### [日期过滤指南](DATE_FILTERING_GUIDE.md) 🆕

**按日期查询文章**

- 📅 指定具体日期查询（YYYY-MM-DD）
- 📆 日期范围查询（start_date + end_date）
- ⏰ 相对时间查询（days 参数）
- 🎯 参数优先级说明
- 💻 Python/JS/cURL 完整示例
- ⚡ 性能优化建议
- ❌ 错误处理和验证

**适合**: 需要按日期获取文章的场景

**阅读时间**: 10-15 分钟

**新增时间**: 2026-01-05

---

### [API 监控指南](MONITORING_GUIDE.md) 🆕

**监控 API 使用情况**

- 📊 请求追踪和统计
- ⚡ 性能指标分析
- 🐌 慢查询识别（>1秒）
- 💾 数据库日志查询
- 🚨 告警配置建议
- 📈 可视化集成方案

**功能亮点**:
- 每个请求的唯一 ID 追踪
- 实时响应时间监控
- 24小时统计数据
- 端点性能排行
- 客户端访问统计

**适合**: 运维监控、性能优化

**阅读时间**: 15-20 分钟

**新增时间**: 2026-01-05

---

### [RSS 订阅源使用指南](RSS_USAGE_GUIDE.md) 🆕

**RSS 2.0 订阅源完整使用指南**

- 📡 RSS 订阅地址和格式
- 🌍 三种摘要语言（中文/英文/双语）
- 🎯 分类和时间过滤
- 📱 RSS 阅读器订阅教程
- 🔧 高级过滤和组合查询
- ⚙️ 技术规格和最佳实践

**功能亮点**:
- 标准 RSS 2.0 格式
- 支持所有主流 RSS 阅读器
- 灵活的过滤选项
- 中英文双语支持
- HTML 格式化摘要
- 来源和分类信息

**适合**: RSS 用户、内容聚合、自动化订阅

**阅读时间**: 10-15 分钟

**新增时间**: 2026-01-05

---

### [API 管理分析](ANALYSIS.md)

**技术分析和改进建议**

- 📊 当前功能现状分析
- 🎯 缺失功能识别
- 💡 改进建议（高/中/低优先级）
- 📅 实施路线图
- 🔧 技术选型建议

**适合**: 系统架构师、技术规划

**阅读时间**: 20-30 分钟

---

## 🚀 快速开始

### 第一步：测试 API 连接

```bash
curl http://localhost:8000/api/health
```

**预期响应**:
```json
{
  "status": "ok",
  "message": "AI-RSS-Hub is running"
}
```

### 第二步：获取文章列表

```bash
# 获取最新 10 篇文章
curl http://localhost:8000/api/articles?limit=10

# 获取今天的文章
curl "http://localhost:8000/api/articles?date=$(date +%Y-%m-%d)"
```

### 第三步：查看 API 统计

```bash
# 查看 24 小时 API 使用统计
curl http://localhost:8000/api/stats?hours=24
```

---

## 📊 API 端点一览

| 端点 | 方法 | 说明 | 认证 | 文档 |
|------|------|------|------|------|
| `/api/health` | GET | 健康检查 | ❌ 否 | [参考](API_GUIDE.md#1-健康检查) |
| `/api/status` | GET | 系统状态 | ❌ 否 | [参考](API_GUIDE.md#2-系统状态) |
| `/api/feeds` | GET | 获取 RSS 源列表 | ❌ 否 | [参考](API_GUIDE.md#3-获取-rss-源列表) |
| `/api/feeds` | POST | 添加 RSS 源 | ✅ 是 | [参考](API_GUIDE.md#4-添加-rss-源) |
| `/api/articles` | GET | 获取文章列表 | ❌ 否 | [日期过滤](DATE_FILTERING_GUIDE.md) |
| `/api/feeds/fetch` | POST | 手动触发抓取 | ✅ 是 | [参考](API_GUIDE.md#6-手动触发抓取) |
| `/api/stats` | GET | API 统计信息 | ❌ 否 | [监控](MONITORING_GUIDE.md) |

**Base URL**: `http://localhost:8000` (或您的服务器地址)

**认证方式**: `X-API-Token` 请求头

详见 [API 参考手册 - 认证方式](API_GUIDE.md#认证方式)

---

## 🎯 按使用场景查找

### 场景 1: 首次集成 API

**推荐文档**:
1. [API 参考手册](API_GUIDE.md) - 了解所有端点
2. [快速开始示例](API_GUIDE.md#代码示例) - 复制粘贴代码
3. [认证方式](API_GUIDE.md#认证方式) - 配置访问权限

**预计时间**: 30 分钟

### 场景 2: 使用日期过滤

**推荐文档**:
1. [日期过滤指南](DATE_FILTERING_GUIDE.md) - 完整使用说明
2. [Python 示例](DATE_FILTERING_GUIDE.md#python-示例) - 直接可用代码
3. [参数优先级](DATE_FILTERING_GUIDE.md#优先级规则) - 理解参数行为

**预计时间**: 15 分钟

### 场景 3: 监控和优化

**推荐文档**:
1. [API 监控指南](MONITORING_GUIDE.md) - 监控功能说明
2. [统计数据说明](MONITORING_GUIDE.md#指标说明) - 理解各项指标
3. [性能优化建议](MONITORING_GUIDE.md#性能优化) - 提升性能

**预计时间**: 20 分钟

### 场景 4: 系统规划和改进

**推荐文档**:
1. [API 管理分析](ANALYSIS.md) - 功能分析
2. [改进建议](ANALYSIS.md#改进建议按优先级) - 优化方向
3. [实施路线图](ANALYSIS.md#实施路线图) - 长期规划

**预计时间**: 30 分钟

---

## 💡 代码示例速查

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 获取文章
response = requests.get(f"{BASE_URL}/api/articles?limit=10")
articles = response.json()

# 按日期获取
today = datetime.now().strftime("%Y-%m-%d")
response = requests.get(f"{BASE_URL}/api/articles?date={today}")
articles = response.json()
```

完整示例见 [API 参考手册](API_GUIDE.md#代码示例)

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000";

// 获取文章
const response = await fetch(`${BASE_URL}/api/articles?limit=10`);
const articles = await response.json();
```

### cURL

```bash
# 健康检查
curl http://localhost:8000/api/health

# 获取文章
curl http://localhost:8000/api/articles?limit=10

# 日期过滤
curl "http://localhost:8000/api/articles?date=2026-01-05"
```

---

## 📈 功能特性

### ✅ 已实现

- 📡 RESTful API 设计
- 🔒 API Token 认证
- 📝 自动请求日志
- ⚡ 性能监控
- 📅 日期过滤查询
- 🌍 双语摘要支持
- 📊 统计分析

### 🚧 规划中

详见 [API 管理分析](ANALYSIS.md)

---

## 🔍 常见问题

### Q: 如何获取今天的文章？

```bash
curl "http://localhost:8000/api/articles?date=$(date +%Y-%m-%d)"
```

详见：[日期过滤指南](DATE_FILTERING_GUIDE.md)

### Q: 如何查看 API 使用统计？

```bash
curl http://localhost:8000/api/stats?hours=24
```

详见：[监控指南](MONITORING_GUIDE.md)

### Q: 如何认证 API 请求？

```bash
curl -X POST http://localhost:8000/api/feeds \
  -H "X-API-Token: your_token" \
  -d '{"name":"Example","url":"https://example.com/rss"}'
```

详见：[API 参考手册 - 认证](API_GUIDE.md#认证方式)

### Q: 如何按日期范围查询？

```bash
curl "http://localhost:8000/api/articles?start_date=2026-01-01&end_date=2026-01-05"
```

详见：[日期过滤指南](DATE_FILTERING_GUIDE.md)

---

## 📝 更新历史

- **2026-01-05**: 新增日期过滤功能
- **2026-01-05**: 新增 API 监控功能
- **2026-01-05**: 完善文档结构

---

## 🔗 相关资源

- [📚 文档中心](../README.md) - 返回文档首页
- [🚀 快速开始](../guides/QUICK_START_CLIENT.md) - 客户端快速上手
- [📮 Postman 指南](../guides/POSTMAN_GUIDE.md) - 使用 Postman 测试
- [🏠 项目主页](../../README.md) - 项目说明

---

**API 版本**: 1.0.0
**文档版本**: 2.0.0
**最后更新**: 2026-01-05
**维护者**: AI-RSS-Hub Team
