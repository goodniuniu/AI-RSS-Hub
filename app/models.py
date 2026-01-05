"""
数据模型定义
使用 SQLModel 定义 Feed 和 Article 表
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Feed(SQLModel, table=True):
    """RSS 源数据模型"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="RSS 源名称")
    url: str = Field(unique=True, description="RSS 源 URL")
    category: str = Field(index=True, default="tech", description="分类")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 关联关系
    articles: List["Article"] = Relationship(back_populates="feed")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Hacker News",
                "url": "https://news.ycombinator.com/rss",
                "category": "tech",
                "is_active": True,
            }
        }


class Article(SQLModel, table=True):
    """文章数据模型"""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, description="文章标题")
    link: str = Field(unique=True, description="文章链接")
    content: Optional[str] = Field(default=None, description="原始内容")
    summary: Optional[str] = Field(default=None, description="AI 中文总结")
    summary_en: Optional[str] = Field(default=None, description="AI 英文总结")
    published_at: Optional[datetime] = Field(default=None, index=True, description="发布时间")
    feed_id: int = Field(foreign_key="feed.id", description="所属 RSS 源 ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    # 关联关系
    feed: Optional[Feed] = Relationship(back_populates="articles")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sample Article",
                "link": "https://example.com/article",
                "content": "Full article content...",
                "summary": "AI generated summary...",
                "published_at": "2025-12-25T10:00:00",
                "feed_id": 1,
            }
        }


# API 响应模型
class FeedCreate(SQLModel):
    """创建 Feed 的请求模型"""

    name: str
    url: str
    category: str = "tech"
    is_active: bool = True


class FeedResponse(SQLModel):
    """Feed 响应模型"""

    id: int
    name: str
    url: str
    category: str
    is_active: bool
    created_at: datetime


class ArticleResponse(SQLModel):
    """Article 响应模型"""

    id: int
    title: str
    link: str
    summary: Optional[str]
    summary_en: Optional[str] = None  # 英文摘要
    published_at: Optional[datetime]
    feed_id: int
    feed_name: Optional[str] = None  # 额外字段，用于显示源名称
    created_at: datetime
