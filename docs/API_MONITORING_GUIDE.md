# API 监控使用指南

**版本**: 1.0.0
**更新日期**: 2026-01-05
**作者**: AI-RSS-Hub Team

---

## 📊 目录

1. [概述](#概述)
2. [监控功能](#监控功能)
3. [使用方法](#使用方法)
4. [指标说明](#指标说明)
5. [配置选项](#配置选项)
6. [最佳实践](#最佳实践)
7. [故障排除](#故障排除)

---

## 概述

AI-RSS-Hub 提供了完整的 API 监控系统，帮助您了解 API 使用情况、性能瓶颈和潜在问题。

### 核心特性

- ✅ **自动请求追踪**: 每个 API 请求自动分配唯一 ID
- ✅ **性能监控**: 记录每个端点的响应时间
- ✅ **详细统计**: 提供 24 小时到 7 天的使用统计
- ✅ **错误追踪**: 自动记录 4xx 和 5xx 错误
- ✅ **慢请求检测**: 识别超过 1 秒的慢请求
- ✅ **客户端分析**: 统计访问来源 IP

### 监控架构

```
API 请求
    ↓
[APIMonitoringMiddleware]
    ├─ 生成请求 ID
    ├─ 记录开始时间
    ├─ 获取客户端信息
    ↓
[业务逻辑处理]
    ↓
[APIMonitoringMiddleware]
    ├─ 计算响应时间
    ├─ 添加响应头
    ├─ 写入日志 (文件)
    └─ 写入数据库 (异步)
```

---

## 监控功能

### 1. 请求追踪

每个 API 请求都会获得一个 8 字符的唯一请求 ID：

```bash
$ curl -i http://localhost:8000/api/health

HTTP/1.1 200 OK
x-request-id: a3f2b1c4
x-process-time: 1.23ms
...
```

**请求 ID 用途**:
- 日志查询和问题追踪
- 分布式追踪关联
- 客户端问题诊断

### 2. 性能监控

自动记录每个请求的处理时间：

- **实时响应头**: `X-Process-Time` 显示每个请求的实际耗时
- **数据库日志**: 持久化存储所有请求的性能数据
- **统计分析**: 提供平均值、最大值、最小值等指标

### 3. 慢请求检测

自动识别响应时间超过 **1 秒** 的请求：

```
2026-01-05 15:30:00 - WARNING - Slow Request: {
    'request_id': 'd76a907b',
    'method': 'GET',
    'path': '/api/articles',
    'status': 200,
    'time_ms': 1250.50,
    'ip': '127.0.0.1',
    'slow': 'YES'
}
```

**慢请求阈值**: 可在 `app/security/api_monitoring.py` 中修改：

```python
class APIMonitoringMiddleware(BaseHTTPMiddleware):
    SLOW_REQUEST_THRESHOLD = 1000  # 毫秒
```

### 4. 统计端点

`GET /api/stats` 端点提供全面的 API 使用统计。

---

## 使用方法

### 查看统计数据

**基本请求**:

```bash
curl http://localhost:8000/api/stats
```

**指定时间范围**:

```bash
# 查看最近 24 小时（默认）
curl http://localhost:8000/api/stats?hours=24

# 查看最近 7 天
curl http://localhost:8000/api/stats?hours=168

# 查看最近 1 小时
curl http://localhost:8000/api/stats?hours=1
```

**使用 Python**:

```python
import requests

response = requests.get('http://localhost:8000/api/stats?hours=24')
stats = response.json()

print(f"总请求数: {stats['overall']['total_requests']}")
print(f"成功率: {stats['overall']['success_rate']}%")
print(f"平均响应时间: {stats['overall']['avg_response_time_ms']}ms")
```

### 查看数据库日志

**使用 Python**:

```python
import sqlite3

conn = sqlite3.connect('ai_rss_hub.db')
cursor = conn.cursor()

# 查询最近的请求
cursor.execute('''
    SELECT method, path, status_code, response_time_ms, created_at
    FROM api_request_log
    ORDER BY created_at DESC
    LIMIT 10
''')

for row in cursor.fetchall():
    print(f"{row[0]} {row[1]} - {row[2]} ({row[3]}ms) {row[4]}")

conn.close()
```

**查询特定端点**:

```python
# 查询 /api/articles 的统计
cursor.execute('''
    SELECT
        COUNT(*) as total,
        AVG(response_time_ms) as avg_time,
        MIN(response_time_ms) as min_time,
        MAX(response_time_ms) as max_time
    FROM api_request_log
    WHERE path = '/api/articles'
    AND created_at >= datetime('now', '-24 hours')
''')

total, avg, min_time, max_time = cursor.fetchone()
print(f"/api/articles (最近24小时)")
print(f"  请求总数: {total}")
print(f"  平均时间: {avg:.2f}ms")
print(f"  最快: {min_time:.2f}ms")
print(f"  最慢: {max_time:.2f}ms")
```

### 实时监控日志

**查看实时日志**:

```bash
# 如果使用 systemd
journalctl -u ai-rss-hub -f | grep "API Request"

# 如果使用 standalone
tail -f /tmp/ai-rss-test.log | grep "API Request"
```

**过滤慢请求**:

```bash
tail -f /tmp/ai-rss-test.log | grep "Slow Request"
```

**过滤错误**:

```bash
tail -f /tmp/ai-rss-test.log | grep "status.*5[0-9][0-9]"
```

---

## 指标说明

### 端点统计 (endpoints)

每个 API 端点的详细统计：

```json
{
  "path": "/api/articles",
  "method": "GET",
  "requests_24h": 1250,
  "avg_response_time_ms": 150.5,
  "max_response_time_ms": 850.2,
  "min_response_time_ms": 45.3,
  "success_rate": 99.2,
  "success_count": 1240,
  "error_count": 10
}
```

**字段说明**:
- `requests_24h`: 24 小时内的请求总数
- `avg_response_time_ms`: 平均响应时间（毫秒）
- `max_response_time_ms`: 最大响应时间
- `min_response_time_ms`: 最小响应时间
- `success_rate`: 成功率（百分比）
- `success_count`: 成功请求数（状态码 < 400）
- `error_count`: 错误请求数（状态码 >= 400）

### 总体统计 (overall)

全局性能指标：

```json
{
  "total_requests": 5420,
  "avg_response_time_ms": 145.5,
  "success_rate": 99.26,
  "success_count": 5380,
  "server_errors": 5,
  "client_errors": 35
}
```

**字段说明**:
- `total_requests`: 总请求数
- `avg_response_time_ms`: 所有请求的平均响应时间
- `success_rate`: 总体成功率
- `success_count`: 成功请求总数
- `server_errors`: 5xx 服务器错误数
- `client_errors`: 4xx 客户端错误数

### 状态码分布 (status_codes)

所有 HTTP 状态码的统计：

```json
{
  "code": 200,
  "count": 5380
}
```

### 慢请求排行 (slowest_requests)

响应时间最长的 10 个请求：

```json
{
  "path": "/api/articles",
  "method": "GET",
  "response_time_ms": 850.2,
  "status_code": 200,
  "created_at": "2026-01-05 15:30:00"
}
```

**用途**: 识别性能瓶颈，优化慢查询

### 客户端统计 (top_clients)

请求最多的前 10 个 IP 地址：

```json
{
  "ip": "127.0.0.1",
  "requests": 3200
}
```

**用途**:
- 识别主要用户
- 发现异常访问模式
- 安全审计

### 系统信息 (system)

```json
{
  "active_feeds": 7,
  "total_articles": 329
}
```

---

## 配置选项

### 调整慢请求阈值

**文件**: `app/security/api_monitoring.py`

```python
class APIMonitoringMiddleware(BaseHTTPMiddleware):
    # 慢请求阈值（毫秒）
    SLOW_REQUEST_THRESHOLD = 1000  # 1 秒
```

**建议值**:
- 快速 API: 500ms
- 普通 API: 1000ms
- 复杂查询: 2000ms

### 禁用数据库日志

如果不需要持久化存储，可以禁用数据库日志：

**文件**: `app/security/api_monitoring.py`

```python
def _log_request(self, request_id, method, path, status_code,
                process_time, client_ip, user_agent, error):
    """记录请求日志"""

    # ... 现有日志代码 ...

    # 注释掉数据库写入
    # self._save_to_database(...)
```

### 调整日志级别

**文件**: `app/security/logger.py`

```python
# 只记录错误和慢请求
logging.getLogger("app.security.api_monitoring").setLevel(logging.WARNING)
```

### 数据库索引优化

已有索引确保查询性能：

```sql
-- 按路径查询
CREATE INDEX idx_api_log_path ON api_request_log(path);

-- 按时间查询
CREATE INDEX idx_api_log_created ON api_request_log(created_at);

-- 按状态码查询
CREATE INDEX idx_api_log_status ON api_request_log(status_code);

-- 按请求 ID 查询
CREATE INDEX idx_api_log_request_id ON api_request_log(request_id);
```

### 数据保留策略

定期清理旧日志以控制数据库大小：

```python
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('ai_rss_hub.db')
cursor = conn.cursor()

# 删除 30 天前的日志
cutoff = (datetime.now() - timedelta(days=30)).isoformat()
cursor.execute('DELETE FROM api_request_log WHERE created_at < ?', (cutoff,))

conn.commit()
conn.close()
```

---

## 最佳实践

### 1. 定期检查统计数据

**建议**: 每周检查一次 API 统计

```bash
# 每周一早上 9 点自动检查
0 9 * * 1 curl http://localhost:8000/api/stats?hours=168 > /var/log/api-weekly-stats.json
```

### 2. 监控关键指标

**重点关注**:
- 成功率 < 95%
- 平均响应时间 > 500ms
- 5xx 错误数量增加
- 异常 IP 访问量

### 3. 设置告警阈值

**建议配置**:

```python
# 在监控脚本中
if stats['overall']['success_rate'] < 95:
    send_alert(f"成功率过低: {stats['overall']['success_rate']}%")

if stats['overall']['avg_response_time_ms'] > 500:
    send_alert(f"响应时间过长: {stats['overall']['avg_response_time_ms']}ms")

if stats['overall']['server_errors'] > 10:
    send_alert(f"服务器错误过多: {stats['overall']['server_errors']}")
```

### 4. 优化慢查询

**步骤**:
1. 查看 `slowest_requests` 找出慢端点
2. 分析该端点的代码逻辑
3. 优化数据库查询
4. 添加缓存（如果适用）
5. 重新测试

**示例**:

```bash
# 查看慢请求
curl http://localhost:8000/api/stats?hours=24 | jq '.slowest_requests'

# 假设发现 /api/articles 慢
# 检查是否缺少索引
# 检查 N+1 查询问题
# 考虑添加 Redis 缓存
```

### 5. 数据库维护

**定期任务**:

```python
# 每月清理旧数据
def cleanup_old_logs(days_to_keep=30):
    conn = sqlite3.connect('ai_rss_hub.db')
    cursor = conn.cursor()

    cutoff = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
    cursor.execute('DELETE FROM api_request_log WHERE created_at < ?', (cutoff,))

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    print(f"已删除 {deleted} 条旧日志")
```

### 6. 性能基准

**参考基准** (基于实际测试):

| 端点 | 平均响应时间 | 目标 |
|------|------------|------|
| `/api/health` | < 5ms | 健康检查应最快 |
| `/api/feeds` | < 50ms | 简单列表查询 |
| `/api/articles` | < 200ms | 可能涉及数据库连接 |
| `/api/stats` | < 500ms | 复杂聚合查询 |

---

## 故障排除

### 问题 1: 统计数据为空

**症状**: `/api/stats` 返回空数组

**原因**:
- 中间件未正确加载
- 数据库表未创建
- 时间范围设置不当

**解决**:

```bash
# 1. 检查中间件是否加载
curl -i http://localhost:8000/api/health | grep "x-request-id"

# 2. 检查数据库表是否存在
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('ai_rss_hub.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_request_log'")
print(f"表存在: {cursor.fetchone() is not None}")
conn.close()
EOF

# 3. 重新创建表（如果需要）
python3 scripts/migration/create_api_request_log_table.py
```

### 问题 2: 请求 ID 未显示

**症状**: 响应头中没有 `X-Request-ID`

**检查**:

```bash
# 查看应用日志
tail -f /tmp/ai-rss-test.log | grep "API Request"

# 检查中间件顺序
# app/main.py 中确保 APIMonitoringMiddleware 在其他中间件之后
```

### 问题 3: 数据库写入失败

**症状**: 统计数据少于实际请求数

**检查**:

```python
import sqlite3
conn = sqlite3.connect('ai_rss_hub.db')

# 检查数据库锁
cursor = conn.cursor()
cursor.execute('PRAGMA database_list')
print(cursor.fetchone())

conn.close()
```

**解决**:
- 确保 SQLite WAL 模式已启用
- 检查文件权限
- 查看应用日志中的数据库错误

### 问题 4: 性能影响

**症状**: API 响应变慢

**优化**:

1. **异步写入**: 已实现，不会阻塞请求

2. **数据库连接池**:
```python
# 在 app/config.py 中调整
SQLITE_POOL_SIZE = 5
```

3. **定期清理**:
```python
# 清理旧数据以保持性能
cleanup_old_logs(days_to_keep=7)
```

---

## 示例代码

### 完整的监控脚本

```python
#!/usr/bin/env python3
"""
API 监控脚本
定期检查 API 性能并发送告警
"""
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

ALERT_EMAIL = "admin@example.com"
API_URL = "http://localhost:8000/api/stats?hours=24"

def get_stats():
    """获取 API 统计"""
    response = requests.get(API_URL)
    return response.json()

def send_alert(subject, message):
    """发送邮件告警"""
    msg = MIMEText(message)
    msg['Subject'] = f"[API Alert] {subject}"
    msg['From'] = "api-monitor@example.com"
    msg['To'] = ALERT_EMAIL

    # 配置 SMTP 服务器
    with smtplib.SMTP('smtp.example.com') as server:
        server.send_message(msg)

def check_health(stats):
    """检查 API 健康状况"""
    issues = []

    # 检查成功率
    if stats['overall']['success_rate'] < 95:
        issues.append(f"成功率过低: {stats['overall']['success_rate']}%")

    # 检查响应时间
    if stats['overall']['avg_response_time_ms'] > 500:
        issues.append(f"响应时间过长: {stats['overall']['avg_response_time_ms']}ms")

    # 检查服务器错误
    if stats['overall']['server_errors'] > 10:
        issues.append(f"服务器错误过多: {stats['overall']['server_errors']}")

    return issues

def main():
    print(f"[{datetime.now()}] 开始 API 健康检查...")

    stats = get_stats()
    issues = check_health(stats)

    if issues:
        message = "\n".join(issues)
        print(f"发现问题:\n{message}")
        send_alert("API 健康检查失败", message)
    else:
        print("API 运行正常")

    print(f"总请求数: {stats['overall']['total_requests']}")
    print(f"平均响应时间: {stats['overall']['avg_response_time_ms']}ms")
    print(f"成功率: {stats['overall']['success_rate']}%")

if __name__ == "__main__":
    main()
```

### Grafana 集成示例

```python
import requests
import time

def export_to_prometheus(stats):
    """导出统计数据到 Prometheus"""

    # 端点请求计数
    for endpoint in stats['endpoints']:
        metric = f"""
api_requests_total{{path="{endpoint['path']}",method="{endpoint['method']}"}} {endpoint['requests_24h']}
api_response_time_ms{{path="{endpoint['path']}",method="{endpoint['method']}"}} {endpoint['avg_response_time_ms']}
api_success_rate{{path="{endpoint['path']}",method="{endpoint['method']}"}} {endpoint['success_rate']}
"""
        print(metric)

    # 发送到 Prometheus Pushgateway
    # requests.post('http://pushgateway:9091/metrics/job/api-monitor', data=metrics)

while True:
    stats = requests.get('http://localhost:8000/api/stats?hours=1').json()
    export_to_prometheus(stats)
    time.sleep(60)
```

---

## 总结

AI-RSS-Hub 的 API 监控系统提供了：

- ✅ **完整的请求追踪**: 从请求 ID 到响应时间的全链路监控
- ✅ **详细的性能指标**: 平均值、最大值、最小值、百分位数
- ✅ **智能告警**: 慢请求检测、错误统计
- ✅ **灵活的查询**: 支持 SQL 查询和 REST API
- ✅ **零性能影响**: 异步数据库写入

**下一步**:
1. 根据实际使用情况调整慢请求阈值
2. 设置定期统计报告
3. 配置告警通知
4. 优化发现的慢查询

**相关文档**:
- [API 使用指南](./API_USAGE_GUIDE.md)
- [安全指南](./SECURITY_GUIDE.md)
- [性能优化指南](./PERFORMANCE_GUIDE.md)

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-05
**维护者**: AI-RSS-Hub Team
