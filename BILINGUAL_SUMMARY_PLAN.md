# 中英文双语摘要功能实施计划

## 📋 需求分析

### 当前状态
- 文章摘要字段：`summary` (中文)
- API返回：单一中文摘要

### 目标状态
- 文章摘要字段：`summary` (中文) + `summary_en` (英文)
- API返回：中英文双语摘要
- 用户价值：获取资讯的同时学习英语

---

## 🎯 功能设计

### 数据库设计

#### Article模型新增字段
```python
class Article(SQLModel, table=True):
    # ... 现有字段 ...
    summary: Optional[str] = Field(default=None, description="中文摘要")
    summary_en: Optional[str] = Field(default=None, description="英文摘要")  # 新增
```

### API响应设计

#### 方案选择：向后兼容的响应格式

```json
{
  "id": 1,
  "title": "Article Title",
  "summary": "这是中文摘要...",
  "summary_en": "This is the English summary...",
  "summary_bilingual": {
    "zh": "这是中文摘要...",
    "en": "This is the English summary..."
  }
}
```

**优点**：
- ✅ 向后兼容（保留原`summary`字段）
- ✅ 灵活查询（可单独查询中文或英文）
- ✅ 扩展性好（未来可添加更多语言）

---

## 🔧 技术实施步骤

### Phase 1: 数据库层改造 (30分钟)

#### 1.1 更新数据模型
**文件**: `app/models.py`

```python
class Article(SQLModel, table=True):
    # ... 现有字段 ...
    summary: Optional[str] = Field(default=None, description="中文摘要")
    summary_en: Optional[str] = Field(default=None, description="英文摘要")  # 新增
```

#### 1.2 创建数据库迁移脚本
**文件**: `scripts/migration/add_summary_en_field.py`

```python
#!/usr/bin/env python3
"""
添加 summary_en 字段到 Article 表
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import SQLModel, Session
from app.database import engine
from app.models import Article
import sqlite3

def migrate():
    """添加 summary_en 字段"""
    conn = sqlite3.connect('ai_rss_hub.db')
    cursor = conn.cursor()

    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(article)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'summary_en' not in columns:
            print("添加 summary_en 字段...")
            cursor.execute(
                "ALTER TABLE article ADD COLUMN summary_en TEXT"
            )
            conn.commit()
            print("✅ 字段添加成功")
        else:
            print("ℹ️  summary_en 字段已存在")

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
```

---

### Phase 2: AI摘要服务改造 (45分钟)

#### 2.1 更新summarizer生成双语摘要
**文件**: `app/services/summarizer.py`

**方案A：单次调用生成双语（推荐）**
```python
async def summarize_article_bilingual(
    title: str,
    content: str,
    max_length: int = 100
) -> tuple[str, str]:
    """
    生成中英文双语摘要

    Returns:
        (zh_summary, en_summary): 中文摘要和英文摘要
    """
    prompt = f"""Please summarize the following article in BOTH Chinese and English.

Title: {title}
Content: {content[:2000]}

Requirements:
1. Chinese summary: {max_length}字以内
2. English summary: {max_length * 2} words以内
3. Keep key information and main points

Please respond in the following format:
Chinese: [中文摘要]
English: [英文摘要]
"""

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a professional bilingual summarizer."},
                {"role": "user", "content": prompt}
            ],
            timeout=settings.llm_timeout
        )

        result = response.choices[0].message.content

        # 解析中英文摘要
        zh_summary = extract_chinese_summary(result)
        en_summary = extract_english_summary(result)

        return zh_summary, en_summary

    except Exception as e:
        logger.error(f"双语摘要生成失败: {e}")
        # 降级：只生成中文摘要
        zh_summary = await summarize_text(content)
        return zh_summary, ""

def extract_chinese_summary(text: str) -> str:
    """从LLM响应中提取中文摘要"""
    match = re.search(r'Chinese:\s*(.*?)(?=\nEnglish:|$)', text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_english_summary(text: str) -> str:
    """从LLM响应中提取英文摘要"""
    match = re.search(r'English:\s*(.*?)(?=$)', text, re.DOTALL)
    return match.group(1).strip() if match else ""
```

**方案B：两次独立调用（备选）**
```python
async def summarize_article_bilingual_v2(
    title: str,
    content: str,
    max_length: int = 100
) -> tuple[str, str]:
    """
    生成中英文双语摘要（两次调用方式）

    优点：质量更高，更可控
    缺点：API调用成本加倍
    """
    # 生成中文摘要
    zh_prompt = f"请用中文总结以下文章，{max_length}字以内：\n\n标题：{title}\n内容：{content[:2000]}"
    zh_summary = await summarize_text_with_prompt(zh_prompt)

    # 生成英文摘要
    en_prompt = f"Please summarize the following article in English, {max_length * 2} words max:\n\nTitle: {title}\nContent: {content[:2000]}"
    en_summary = await summarize_text_with_prompt(en_prompt)

    return zh_summary, en_summary
```

#### 2.2 更新RSS抓取逻辑
**文件**: `app/services/rss_fetcher.py`

```python
async def process_article(article_data, feed_id, session):
    """处理单篇文章，生成双语摘要"""
    # ... 现有逻辑 ...

    # 生成双语摘要
    zh_summary, en_summary = await summarize_article_bilingual(
        title=article_data.get('title', ''),
        content=article_data.get('content', article_data.get('summary', '')),
        max_length=100
    )

    # 创建文章记录
    article = Article(
        title=article_data.get('title'),
        link=article_data.get('link'),
        content=article_data.get('content'),
        summary=zh_summary,      # 中文
        summary_en=en_summary,   # 英文（新增）
        published_at=published_at,
        feed_id=feed_id
    )
```

---

### Phase 3: API层更新 (30分钟)

#### 3.1 更新响应模型
**文件**: `app/models.py`

```python
class ArticleResponse(SQLModel):
    """Article 响应模型（双语）"""
    id: int
    title: str
    link: str
    summary: Optional[str]
    summary_en: Optional[str]  # 新增
    summary_bilingual: Optional[Dict[str, str]] = None  # 新增：双语格式
    published_at: Optional[datetime]
    feed_id: int
    feed_name: Optional[str] = None
    created_at: datetime
```

#### 3.2 更新API路由
**文件**: `app/api/routes.py`

```python
@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    days: Optional[int] = None,
    language: Optional[str] = Query(None, description="语言偏好: zh, en, or both"),
    session: Session = Depends(get_session),
):
    """获取文章列表（支持双语）"""
    articles = get_articles(session, limit=limit, category=category, days=days)

    response_articles = []
    for article in articles:
        article_dict = {
            "id": article.id,
            "title": article.title,
            "link": article.link,
            "summary": article.summary,
            "summary_en": article.summary_en,  # 新增
            "summary_bilingual": {  # 新增
                "zh": article.summary,
                "en": article.summary_en or ""
            } if article.summary_en else None,
            "published_at": article.published_at,
            "feed_id": article.feed_id,
            "feed_name": article.feed.name if article.feed else None,
            "created_at": article.created_at
        }
        response_articles.append(ArticleResponse(**article_dict))

    return response_articles
```

---

### Phase 4: 历史数据处理 (20分钟)

#### 4.1 创建英文摘要生成脚本
**文件**: `utils/generate_english_summaries.py`

```python
#!/usr/bin/env python3
"""
为现有文章生成英文摘要
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.database import engine
from app.models import Article
from app.services.summarizer import summarize_article_bilingual
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_missing_summaries(limit: int = None):
    """为缺失英文摘要的文章生成英文摘要"""
    with Session(engine) as session:
        # 查询没有英文摘要的文章
        statement = select(Article).where(Article.summary_en.is_(None))
        if limit:
            statement = statement.limit(limit)

        results = session.exec(statement)
        articles = results.all()

        logger.info(f"找到 {len(articles)} 篇需要生成英文摘要的文章")

        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"[{i}/{len(articles)}] 处理: {article.title[:50]}...")

                # 生成英文摘要
                content = article.content or article.summary or ""
                zh_summary, en_summary = await summarize_article_bilingual(
                    title=article.title,
                    content=content,
                    max_length=100
                )

                # 更新数据库
                article.summary_en = en_summary
                session.add(article)
                session.commit()

                logger.info(f"  ✅ 完成: {en_summary[:50]}...")

                # 避免API限流
                if i < len(articles):
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"  ❌ 失败: {e}")
                session.rollback()

        logger.info(f"✅ 全部完成！处理了 {len(articles)} 篇文章")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="生成英文摘要")
    parser.add_argument("--limit", type=int, help="处理文章数量限制")
    args = parser.parse_args()

    asyncio.run(generate_missing_summaries(limit=args.limit))
```

**使用方法**：
```bash
# 处理所有缺失英文摘要的文章
python utils/generate_english_summaries.py

# 只处理前10篇（测试）
python utils/generate_english_summaries.py --limit 10
```

---

### Phase 5: 配置和文档 (15分钟)

#### 5.1 添加配置选项
**文件**: `app/config.py`

```python
class Settings(BaseSettings):
    # ... 现有配置 ...
    bilingual_summary: bool = Field(default=True, description="是否生成双语摘要")
    summary_language: str = Field(default="both", description="摘要语言: zh, en, or both")
```

#### 5.2 更新API文档
**文件**: `docs/api/API_GUIDE.md`

添加双语摘要示例：
```json
{
  "id": 1,
  "title": "AI Breakthrough in Language Models",
  "summary": "语言模型领域取得重大突破...",
  "summary_en": "Major breakthrough in language model field...",
  "summary_bilingual": {
    "zh": "语言模型领域取得重大突破...",
    "en": "Major breakthrough in language model field..."
  }
}
```

---

### Phase 6: 测试验证 (20分钟)

#### 6.1 单元测试
**文件**: `tests/test_bilingual_summary.py`

```python
import pytest
from app.services.summarizer import summarize_article_bilingual

@pytest.mark.asyncio
async def test_bilingual_summary_generation():
    """测试双语摘要生成"""
    title = "Test Article"
    content = "This is a test article content..."

    zh_summary, en_summary = await summarize_article_bilingual(
        title=title,
        content=content
    )

    assert zh_summary  # 中文摘要不为空
    assert en_summary  # 英文摘要不为空
    assert len(zh_summary) <= 100  # 长度限制
```

#### 6.2 集成测试
```bash
# 1. 测试数据库迁移
python scripts/migration/add_summary_en_field.py

# 2. 测试双语摘要生成
python utils/generate_english_summaries.py --limit 1

# 3. 测试API响应
curl http://localhost:8000/api/articles?limit=1

# 4. 验证响应格式
curl http://localhost:8000/api/articles?limit=1 | jq '.[0].summary_en'
```

---

## 📊 实施时间线

| 阶段 | 任务 | 预计时间 | 优先级 |
|------|------|----------|--------|
| Phase 1 | 数据库改造 | 30分钟 | 🔴 高 |
| Phase 2 | AI服务改造 | 45分钟 | 🔴 高 |
| Phase 3 | API层更新 | 30分钟 | 🟡 中 |
| Phase 4 | 历史数据处理 | 20分钟 | 🟢 低 |
| Phase 5 | 配置和文档 | 15分钟 | 🟢 低 |
| Phase 6 | 测试验证 | 20分钟 | 🟡 中 |
| **总计** | | **~2.5小时** | |

---

## 🎯 实施建议

### 推荐方案：渐进式部署

#### Step 1: 开发环境验证 (第1天)
1. 在开发环境实施所有改动
2. 测试双语摘要生成质量
3. 验证API响应格式
4. 性能测试（API调用耗时）

#### Step 2: 生产环境灰度 (第2天)
1. 先部署数据库和代码更新
2. **暂时禁用**双语摘要生成（通过配置）
3. 验证系统稳定性
4. 准备回滚方案

#### Step 3: 启用双语生成 (第3天)
1. 启用双语摘要功能
2. 监控API调用成本
3. 收集用户反馈
4. 优化prompt和生成质量

#### Step 4: 历史数据补充 (第4-5天)
1. 在低峰期为历史文章生成英文摘要
2. 分批处理，避免API限流
3. 监控处理进度和错误率

---

## 💡 优化建议

### 1. 性能优化
```python
# 使用缓存避免重复生成
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_summary(article_id: int) -> tuple[str, str]:
    """获取缓存的摘要"""
    # ...
```

### 2. 成本控制
```python
# 仅对热门文章生成英文摘要
async def should_generate_english(article: Article) -> bool:
    """判断是否需要生成英文摘要"""
    # 规则：最近7天的文章
    from datetime import datetime, timedelta
    return article.created_at > datetime.now() - timedelta(days=7)
```

### 3. 质量保证
```python
# 添加质量检查
def validate_summary_quality(summary: str, lang: str) -> bool:
    """验证摘要质量"""
    min_length = 20
    max_length = 500 if lang == "en" else 200

    return min_length <= len(summary) <= max_length
```

---

## 📈 预期效果

### 用户体验提升
- ✅ 获取资讯的同时学习英语
- ✅ 中英文对照，理解更准确
- ✅ 提升产品价值

### 技术指标
- API调用次数：**+100%** (每篇文章两次调用)
- 响应时间：**+3-5秒** (等待LLM生成)
- 存储空间：**+50%** (摘要字段增加)
- 开发成本：**~2.5小时**

---

## 🚀 后续扩展方向

1. **多语言支持**：日语、韩语等
2. **难度分级**：初级、中级、高级英语
3. **词汇高亮**：标注重点词汇
4. **发音功能**：提供音频朗读
5. **学习模式**：点击词汇显示释义

---

**文档创建时间**: 2026-01-04
**预计实施时间**: 2.5小时
**风险等级**: 🟢 低风险（向后兼容）
