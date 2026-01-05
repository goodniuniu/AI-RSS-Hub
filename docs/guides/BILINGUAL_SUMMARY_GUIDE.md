# 双语摘要功能使用指南

## 📖 概述

AI-RSS-Hub 的双语摘要功能会为每篇文章自动生成**中文**和**英文**两个版本的摘要，帮助用户在获取资讯的同时提升英语能力。

### 核心优势

- ✨ **一次生成，双语呈现** - 单次 LLM API 调用生成中英文摘要，成本优化
- 🎯 **语言学习** - 对比阅读中英文摘要，提升英语理解能力
- 🚀 **高性能** - 平均每篇文章处理时间 4.4 秒
- 💰 **成本效益** - 使用优化的 prompt，减少 token 消耗
- 🔄 **向后兼容** - 旧客户端无需修改即可正常工作

---

## 📋 功能说明

### 1. 自动生成

新抓取的文章会自动生成双语摘要：

```python
# app/services/summarizer.py
async def summarize_article_bilingual(
    title: str,
    content: str,
    semaphore: asyncio.Semaphore = None
) -> tuple[str, str]:
    """
    生成中英文双语摘要

    Returns:
        (chinese_summary, english_summary)
    """
```

### 2. API 响应格式

获取文章列表时，每篇文章包含两个摘要字段：

```json
{
  "id": 1,
  "title": "AI Breakthrough in Language Models",
  "summary": "研究人员在语言模型领域取得重大突破，新的模型在多个基准测试中超越了以往的记录。",
  "summary_en": "Researchers have made a major breakthrough in language models, with new models surpassing previous records across multiple benchmarks.",
  "link": "https://example.com/article",
  "feed_name": "TechCrunch",
  "published_at": "2026-01-05T10:00:00"
}
```

**字段说明**：
- `summary`: 中文摘要（字符串或 null）
- `summary_en`: 英文摘要（字符串或 null，旧文章可能未生成）

### 3. 数据库结构

```sql
CREATE TABLE article (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    summary TEXT,           -- 中文摘要
    summary_en TEXT,        -- 英文摘要（新增字段）
    published_at TEXT,
    feed_id INTEGER,
    created_at TEXT
);
```

---

## 🎯 使用场景

### 场景 1: 客户端显示双语摘要

**前端代码示例**：

```typescript
// 显示双语摘要
function ArticleCard({ article }: { article: Article }) {
  return (
    <div className="article-card">
      <h3>{article.title}</h3>

      <div className="summary-cn">
        <h4>中文摘要</h4>
        <p>{article.summary}</p>
      </div>

      <div className="summary-en">
        <h4>English Summary</h4>
        <p>{article.summary_en}</p>
      </div>

      <a href={article.link} target="_blank">阅读全文</a>
    </div>
  );
}
```

### 场景 2: 语言学习模式

```typescript
// 先显示中文，点击后显示英文
function LanguageLearningCard({ article }: { article: Article }) {
  const [showEnglish, setShowEnglish] = useState(false);

  return (
    <div className="learning-card">
      <h3>{article.title}</h3>

      <div className="summary">
        <p>{showEnglish ? article.summary_en : article.summary}</p>
      </div>

      <button onClick={() => setShowEnglish(!showEnglish)}>
        {showEnglish ? '显示中文' : 'Show English'}
      </button>
    </div>
  );
}
```

### 场景 3: 仅显示英文摘要

```typescript
// 对于只想学习英语的用户
function EnglishOnlyCard({ article }: { article: Article }) {
  return (
    <div className="english-card">
      <h3>{article.title}</h3>
      <p className="summary-en">{article.summary_en}</p>
      <small className="hint">
        中文: {article.summary?.substring(0, 50)}...
      </small>
    </div>
  );
}
```

---

## 🔧 批量处理历史文章

如果你有旧的文章缺少英文摘要，可以使用批量处理脚本：

### 快速开始

```bash
# 1. 测试：处理前 5 篇文章
venv/bin/python scripts/dev/generate_english_summaries.py --limit=5

# 2. 处理所有文章
venv/bin/python scripts/dev/generate_english_summaries.py

# 3. 自定义并发数（默认 3）
venv/bin/python scripts/dev/generate_english_summaries.py --batch-size=5
```

### 脚本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--limit` | 限制处理数量（用于测试） | None（处理全部） |
| `--batch-size` | 并发批处理大小 | 3 |

### 性能参考

| 指标 | 数值 |
|------|------|
| 平均处理时间 | 4.4 秒/篇 |
| 成功率 | 99.6% |
| 并发数 | 3（可调整） |
| 242 篇文章总耗时 | 约 17.5 分钟 |

### 处理进度示例

```bash
$ venv/bin/python scripts/dev/generate_english_summaries.py

===========================================================
  批量生成英文摘要
===========================================================

数据库路径: ./ai_rss_hub.db

⏳ 步骤1: 获取文章列表...
找到 239 篇需要处理的文章

⏳ 步骤2: 开始批量处理（并发数: 3）...

[1/239] 处理中...
✅ [242] Millennium Challenge: A corrupted military exercise...
[2/239] 处理中...
✅ [241] Show HN: Quantum Tunnel...

进度: 10/239 (4%), 成功: 10, 失败: 0, 预计剩余: 998秒

...

===========================================================
  ✅ 批量处理完成
===========================================================
总文章数: 239
成功: 238
失败: 1
总耗时: 1047.2 秒
平均每篇: 4.4 秒

⏳ 步骤3: 验证结果...
已有英文摘要的文章: 241
仍缺少英文摘要的文章: 1
```

---

## 🔍 故障排查

### 问题 1: 摘要生成为 null

**可能原因**：
1. LLM API 调用失败
2. API Key 配置错误
3. 网络连接问题

**解决方案**：

```bash
# 1. 检查 API 配置
cat .env | grep LLM

# 2. 测试 LLM 连接
venv/bin/python tests/test_bilingual_summary.py

# 3. 查看应用日志
tail -f logs/ai-rss-hub.log | grep -i "summary\|error"
```

### 问题 2: 英文摘要质量不佳

**可能原因**：
1. 文章内容过短
2. LLM 返回格式不符合预期

**解决方案**：

```bash
# 手动重新生成特定文章的摘要
venv/bin/python scripts/dev/generate_english_summaries.py --limit=1
```

### 问题 3: 批量处理失败率高

**可能原因**：
1. 并发数过高导致 API 限流
2. 网络不稳定

**解决方案**：

```bash
# 降低并发数
venv/bin/python scripts/dev/generate_english_summaries.py --batch-size=1

# 分批处理
venv/bin/python scripts/dev/generate_english_summaries.py --limit=50
```

### 问题 4: 旧文章没有 summary_en 字段

**原因**：数据库 schema 更新前的文章

**解决方案**：

```bash
# 运行批量处理脚本
venv/bin/python scripts/dev/generate_english_summaries.py
```

---

## ⚡ 性能优化建议

### 1. 调整并发数

根据 API 速率限制调整并发数：

```bash
# API 限制严格
--batch-size=1

# API 限制宽松
--batch-size=5
```

### 2. 分批处理

对于大量文章，可以分批处理：

```bash
# 每次处理 100 篇
for i in {1..5}; do
  venv/bin/python scripts/dev/generate_english_summaries.py --limit=100
  sleep 10  # 休息 10 秒
done
```

### 3. 监控进度

处理过程中会显示实时进度：

```
进度: 100/239 (41%), 成功: 100, 失败: 0, 预计剩余: 612秒
```

---

## 📊 技术细节

### Prompt 优化

系统使用优化的 prompt 同时生成中英文摘要：

```python
prompt = f"""
请为以下文章生成双语摘要（中文和英文）。

文章标题：{title}
文章内容：{content[:2000]}

请按以下格式输出：

中文摘要：[100字左右的中文摘要]

English Summary: [Approximately 100 words in English]

要求：
1. 中文摘要简洁明了，突出核心内容
2. 英文摘要准确传达文章要点
3. 两个摘要内容应保持一致，不要添加新的信息
"""
```

### 正则提取

使用多个正则表达式模式提取摘要：

```python
# 中文提取模式
zh_patterns = [
    r"中文摘要[：:]\s*(.+?)(?:\n\n|英文|$)",
    r"中文[：:]\s*(.+?)(?:\n\n|English|$)",
    r"摘要[：:]\s*(.+?)(?:\n\n|$)",
]

# 英文提取模式
en_patterns = [
    r"English Summary[：:]\s*(.+?)(?:\n\n|$)",
    r"英文摘要[：:]\s*(.+?)(?:\n\n|$)",
    r"Summary[：:]\s*(.+?)(?:\n\n|$)",
]
```

### 错误处理

```python
try:
    zh_summary, en_summary = await summarize_article_bilingual(title, content)

    # 验证摘要质量
    if len(zh_summary) < 10 or len(en_summary.split()) < 5:
        logger.warning("摘要质量不佳")

except Exception as e:
    logger.error(f"摘要生成失败: {e}")
    # 失败时不保存，稍后重试
```

---

## 🌐 国际化支持

未来可能扩展到更多语言：

- 🇯🇵 日语 (Japanese)
- 🇰🇷 韩语 (Korean)
- 🇫🇷 法语 (French)
- 🇩🇪 德语 (German)
- 🇪🇸 西班牙语 (Spanish)

---

## 📞 获取帮助

- 📖 [API 文档](../api/API_GUIDE.md)
- 🐛 [报告问题](https://github.com/goodniuniu/AI-RSS-Hub/issues)
- 💬 [讨论区](https://github.com/goodniuniu/AI-RSS-Hub/discussions)

---

## 📝 更新日志

### 2026-01-05
- ✨ 新增双语摘要功能
- 🎯 生成中英文两个版本的摘要
- 📝 完成所有历史文章的英文摘要生成（241/242）
- 📚 更新 API 文档和使用指南
