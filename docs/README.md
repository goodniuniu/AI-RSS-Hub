# AI-RSS-Hub 文档中心

欢迎来到 AI-RSS-Hub 文档中心！

---

## 📚 快速导航

### 👨‍💻 对于客户端开发者

**新手上路**
- [🚀 快速开始](guides/QUICK_START_CLIENT.md) - 5 分钟快速集成
- [🔧 API 参考手册](api/README.md) - 完整的 API 文档
- [💻 客户端使用指南](guides/CLIENT_USAGE_GUIDE.md) - 详细使用说明

**功能特性**
- [📅 日期过滤功能](api/DATE_FILTERING_GUIDE.md) - 按日期查询文章
- [🌍 双语摘要功能](guides/BILINGUAL_SUMMARY_GUIDE.md) - 中英文摘要
- [📊 API 监控功能](api/MONITORING_GUIDE.md) - 性能监控和统计

**测试工具**
- [📮 Postman 测试指南](guides/POSTMAN_GUIDE.md) - 使用 Postman 测试 API

### 🔧 对于系统管理员

**安装部署**
- [📖 安装配置指南](guides/SETUP.md) - 完整安装步骤
- [🚀 自动启动配置](deployment/AUTO_START_GUIDE.md) - systemd 服务配置
- [✅ 重启测试指南](deployment/REBOOT_TEST_GUIDE.md) - 验证自动启动

**运维管理**
- [📊 API 监控指南](api/MONITORING_GUIDE.md) - 监控 API 使用情况
- [📅 更新日志](logs/RSS_SOURCES_UPDATE_LOG.md) - RSS 源更新记录

### 🔧 对于开发者

**架构设计**
- [📝 项目架构说明](development/PROJECT_UNDERSTANDING.md) - 系统设计
- [🔧 开发部署隔离方案](development/开发部署隔离方案.md) - 环境分离

**技术分析**
- [📊 API 管理分析](api/ANALYSIS.md) - 功能分析和改进建议
- [📋 文档整合方案](DOCS_CONSOLIDATION_PLAN.md) - 文档组织方案

---

## 📂 文档结构

```
docs/
├── README.md                          # 📚 文档总索引（本文件）
│
├── api/                              # 🔌 API 文档
│   ├── README.md                     #    API 文档索引
│   ├── API_GUIDE.md                  #    核心 API 参考手册
│   ├── DATE_FILTERING_GUIDE.md       #    日期过滤使用指南
│   ├── MONITORING_GUIDE.md           #    API 监控指南
│   └── ANALYSIS.md                   #    API 管理分析
│
├── guides/                           # 📖 用户指南
│   ├── README.md                     #    指南索引
│   ├── SETUP.md                      #    安装配置
│   ├── CLIENT_USAGE_GUIDE.md         #    客户端使用
│   ├── QUICK_START_CLIENT.md         #    快速开始
│   ├── POSTMAN_GUIDE.md              #    Postman 测试
│   └── BILINGUAL_SUMMARY_GUIDE.md    #    双语摘要功能
│
├── deployment/                       # 🚀 部署相关
│   ├── AUTO_START_GUIDE.md           #    自动启动配置
│   └── REBOOT_TEST_GUIDE.md          #    重启测试
│
├── development/                      # 🔧 开发文档
│   ├── PROJECT_UNDERSTANDING.md      #    项目架构
│   └── 开发部署隔离方案.md           #    隔离方案
│
└── logs/                             # 📝 更新日志
    └── RSS_SOURCES_UPDATE_LOG.md     #    RSS 源更新日志
```

---

## 🎯 按场景查找

### 场景 1: 我是客户端开发者，想快速接入 API

**推荐路径**:
1. [快速开始](guides/QUICK_START_CLIENT.md) - 了解基本概念
2. [API 参考手册](api/README.md) - 查看所有端点
3. [日期过滤指南](api/DATE_FILTERING_GUIDE.md) - 学习高级查询（可选）

**预计时间**: 15-30 分钟

---

### 场景 2: 我是运维人员，需要部署服务

**推荐路径**:
1. [安装配置指南](guides/SETUP.md) - 安装系统
2. [自动启动配置](deployment/AUTO_START_GUIDE.md) - 配置自启动
3. [重启测试指南](deployment/REBOOT_TEST_GUIDE.md) - 验证配置
4. [API 监控指南](api/MONITORING_GUIDE.md) - 设置监控（可选）

**预计时间**: 1-2 小时

---

### 场景 3: 我是开发者，想了解项目架构

**推荐路径**:
1. [项目架构说明](development/PROJECT_UNDERSTANDING.md) - 了解整体设计
2. [API 参考手册](api/API_GUIDE.md) - 查看 API 实现
3. [开发部署隔离方案](development/开发部署隔离方案.md) - 环境配置

**预计时间**: 2-4 小时

---

### 场景 4: 我想使用高级功能

**双语摘要**:
- [双语摘要功能指南](guides/BILINGUAL_SUMMARY_GUIDE.md)

**日期过滤**:
- [日期过滤使用指南](api/DATE_FILTERING_GUIDE.md)

**API 监控**:
- [API 监控指南](api/MONITORING_GUIDE.md)

---

## 📊 API 端点速查

| 端点 | 方法 | 说明 | 文档 |
|------|------|------|------|
| `/api/health` | GET | 健康检查 | [API 参考](api/API_GUIDE.md#1-健康检查) |
| `/api/status` | GET | 系统状态 | [API 参考](api/API_GUIDE.md#2-系统状态) |
| `/api/feeds` | GET | 获取 RSS 源列表 | [API 参考](api/API_GUIDE.md#3-获取-rss-源列表) |
| `/api/feeds` | POST | 添加 RSS 源 | [API 参考](api/API_GUIDE.md#4-添加-rss-源) |
| `/api/articles` | GET | 获取文章列表 | [日期过滤](api/DATE_FILTERING_GUIDE.md) |
| `/api/feeds/fetch` | POST | 手动触发抓取 | [API 参考](api/API_GUIDE.md#6-手动触发抓取) |
| `/api/stats` | GET | API 统计信息 | [监控指南](api/MONITORING_GUIDE.md) |

---

## 🔍 常见问题

### Q: 如何快速测试 API？

**A**: 使用以下命令：

```bash
# 健康检查
curl http://localhost:8000/api/health

# 获取最新文章
curl http://localhost:8000/api/articles?limit=5

# 查看系统状态
curl http://localhost:8000/api/status
```

详见 [快速开始](guides/QUICK_START_CLIENT.md)

### Q: 如何按日期获取文章？

**A**: 使用日期过滤参数：

```bash
# 获取今天的文章
curl "http://localhost:8000/api/articles?date=$(date +%Y-%m-%d)"

# 获取日期范围
curl "http://localhost:8000/api/articles?start_date=2026-01-01&end_date=2026-01-05"
```

详见 [日期过滤指南](api/DATE_FILTERING_GUIDE.md)

### Q: 如何监控系统性能？

**A**: 使用监控端点：

```bash
# 查看 API 统计
curl http://localhost:8000/api/stats?hours=24
```

详见 [API 监控指南](api/MONITORING_GUIDE.md)

### Q: 如何配置自动启动？

**A**: 使用 systemd 服务：

```bash
# 配置服务
bash scripts/service/install_service.sh

# 启用自启动
systemctl --user enable ai-rss-hub
```

详见 [自动启动配置](deployment/AUTO_START_GUIDE.md)

---

## 📝 更新日志

- **2026-01-05**: 文档整合，优化目录结构
- **2026-01-05**: 新增日期过滤功能文档
- **2026-01-05**: 新增 API 监控功能文档
- **2026-01-05**: 新增双语摘要功能文档

详细更新记录见 [更新日志](logs/RSS_SOURCES_UPDATE_LOG.md)

---

## 🔗 相关资源

- [项目主页](../README.md) - AI-RSS-Hub 项目说明
- [GitHub 仓库](https://github.com/goodniuniu/AI-RSS-Hub) - 源代码
- [Issue 追踪](https://github.com/goodniuniu/AI-RSS-Hub/issues) - 问题反馈

---

## 📧 获取帮助

如果文档未能解决您的问题：

1. 查看 [API 参考手册](api/API_GUIDE.md)
2. 搜索已有 [Issues](https://github.com/goodniuniu/AI-RSS-Hub/issues)
3. 提交新的 [Issue](https://github.com/goodniuniu/AI-RSS-Hub/issues/new)

---

**文档版本**: 2.0.0
**最后更新**: 2026-01-05
**维护者**: AI-RSS-Hub Team
