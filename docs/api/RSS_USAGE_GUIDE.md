# RSS 订阅源使用指南

## 概述

AI-RSS-Hub 提供标准的 RSS 2.0 格式订阅源，支持多种摘要语言和过滤选项，可供任何 RSS 阅读器订阅。

## 快速开始

### 基础订阅地址

```
http://your-server:8000/api/rss
```

### 三种摘要语言

1. **中文摘要**（默认）:
   ```
   http://your-server:8000/api/rss
   ```

2. **英文摘要**:
   ```
   http://your-server:8000/api/rss/en
   ```

3. **双语混合**:
   ```
   http://your-server:8000/api/rss/bilingual
   ```

## 订阅方式

### Feedly

1. 打开 Feedly
2. 点击 "添加内容" (Add Content)
3. 输入订阅地址: `http://your-server:8000/api/rss`
4. 点击 "关注" (Follow)

### Inoreader

1. 打开 Inoreader
2. 点击 "订阅" (Subscribe)
3. 输入订阅地址: `http://your-server:8000/api/rss`
4. 点击 "订阅"

### NetNewsWire

1. 打开 NetNewsWire
2. 菜单选择 "文件" > "添加订阅"
3. 输入订阅地址: `http://your-server:8000/api/rss`
4. 点击 "订阅"

### 其他 RSS 阅读器

任何支持 RSS 2.0 标准的阅读器都可以订阅，只需添加上述 URL 即可。

## 高级过滤

### 按分类订阅

**可用分类**:
- `tech` - 科技资讯
- `tech-china` - 中国科技
- `science` - 科学
- `science-space` - 空间科学
- `development` - 开发

**示例**:
```
http://your-server:8000/api/rss?category=tech
http://your-server:8000/api/rss/en?category=science
```

### 按时间范围订阅

**最近 N 天**:
```
http://your-server:8000/api/rss?days=7
http://your-server:8000/api/rss?days=30
```

**限制文章数量**:
```
http://your-server:8000/api/rss?limit=100
```

### 组合过滤

可以组合多个过滤条件:
```
http://your-server:8000/api/rss?category=tech&days=7&limit=50
http://your-server:8000/api/rss/en?category=science&limit=20
```

## RSS 内容格式

### 文章条目包含

- **标题** (title): 文章标题
- **链接** (link): 原文链接
- **描述** (description): AI 生成的摘要（支持 HTML 格式）
  - 中文摘要或英文摘要
  - "阅读原文" 链接
  - 来源信息
- **发布时间** (pubDate): 文章发布时间
- **作者/来源** (author): RSS 源名称
- **分类** (category): 文章分类
- **唯一标识** (guid): 文章永久链接

### 描述示例

**中文摘要格式**:
```html
<strong>中文摘要：</strong><br/>
文章摘要内容...<br/><br/>
<a href="原文链接">阅读原文</a> | 来源: 36Kr
```

**双语摘要格式**:
```html
<strong>中文摘要：</strong><br/>
中文摘要内容...<br/><br/>
<strong>English Summary:</strong><br/>
English summary content...<br/><br/>
<a href="原文链接">阅读原文</a> | 来源: 36Kr
```

## API 参数详解

### 端点路径

- `/api/rss` - 默认（中文）
- `/api/rss/{summary_type}` - 指定摘要类型

### 路径参数

**summary_type**: 摘要类型
- `zh` - 中文摘要（默认）
- `en` - 英文摘要
- `bilingual` - 双语混合

### 查询参数

**category**: 按分类筛选（可选）
- 类型: `string`
- 示例: `?category=tech`

**days**: 最近几天的文章（可选）
- 类型: `integer`
- 范围: 1-30
- 示例: `?days=7`

**limit**: 返回数量限制（可选）
- 类型: `integer`
- 范围: 1-200
- 默认: 50
- 示例: `?limit=100`

## 常见用例

### 1. 订阅最新科技资讯（中文）
```
http://your-server:8000/api/rss?category=tech
```

### 2. 订阅最近 7 天的科学资讯（英文）
```
http://your-server:8000/api/rss/en?category=science&days=7
```

### 3. 订阅双语混合的资讯
```
http://your-server:8000/api/rss/bilingual
```

### 4. 订阅最新 100 篇文章
```
http://your-server:8000/api/rss?limit=100
```

### 5. 订阅最近 30 天的中国科技资讯
```
http://your-server:8000/api/rss?category=tech-china&days=30
```

## 技术规格

- **格式**: RSS 2.0
- **编码**: UTF-8
- **Content-Type**: application/rss+xml; charset=utf-8
- **更新频率**: 根据 RSS 源更新频率（默认每小时）
- **文章数量**: 默认最多 50 篇，可通过 `limit` 参数调整

## 验证 RSS 源

### 在线验证工具

- W3C Feed Validation Service: https://validator.w3.org/feed/
- RSS Board Validator: https://www.rssboard.org/rss-validator/

### 本地测试

使用 curl 测试:
```bash
curl "http://localhost:8000/api/rss?limit=3"
```

使用浏览器直接访问也可以查看 RSS 内容。

## 故障排除

### 问题 1: RSS 源无法加载

**检查**:
- 确认服务器地址正确
- 确认端口 8000 可访问
- 检查防火墙设置

### 问题 2: 没有文章显示

**可能原因**:
- 数据库中没有文章
- 所有文章都在时间范围外

**解决方案**:
- 不使用 `days` 参数限制
- 增大 `days` 值
- 增大 `limit` 值

### 问题 3: 特定分类无文章

**检查**:
- 确认分类名称正确（使用英文分类名）
- 使用 `/api/feeds` 查看所有可用分类

### 问题 4: 摘要显示不正常

**可能原因**:
- RSS 阅读器不支持 HTML 格式
- 摘要过长被截断

**解决方案**:
- 尝试其他 RSS 阅读器
- 切换到英文摘要（通常更短）

## 最佳实践

### 1. 选择合适的摘要语言

- **中文用户**: 使用默认或 `/rss`
- **英文用户**: 使用 `/rss/en`
- **双语环境**: 使用 `/rss/bilingual`

### 2. 合理设置过滤条件

- **最新资讯**: 不设置过滤，使用默认
- **特定主题**: 使用 `category` 过滤
- **时间敏感**: 使用 `days` 限制时间范围
- **信息过载**: 减少 `limit` 数量

### 3. 定期维护

- 定期检查 RSS 源是否正常更新
- 根据阅读习惯调整过滤条件
- 及时清理不活跃的订阅

## 相关文档

- [API 文档](./README.md) - 完整 API 参考
- [日期过滤指南](./DATE_FILTERING_GUIDE.md) - 详细日期过滤选项
- [主项目文档](../README.md) - 项目整体说明

## 更新日志

### 2026-01-05
- ✅ 实现 RSS 2.0 输出功能
- ✅ 支持三种摘要语言（中文/英文/双语）
- ✅ 支持分类过滤
- ✅ 支持时间范围过滤
- ✅ 支持自定义文章数量
- ✅ 标准化 RSS 格式

---

**提示**: 如有问题或建议，请在项目 GitHub 仓库提交 Issue。
