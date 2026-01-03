"""
数据库 CRUD 操作
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from app.models import Feed, Article
import logging

logger = logging.getLogger(__name__)


# Feed 相关操作
def create_feed(session: Session, feed: Feed) -> Feed:
    """创建新的 RSS 源"""
    session.add(feed)
    session.commit()
    session.refresh(feed)
    logger.info(f"创建 Feed: {feed.name}")
    return feed


def get_all_feeds(session: Session, active_only: bool = False) -> List[Feed]:
    """获取所有 RSS 源"""
    statement = select(Feed)
    if active_only:
        statement = statement.where(Feed.is_active == True)
    results = session.exec(statement).all()
    return list(results)


def get_feed_by_id(session: Session, feed_id: int) -> Optional[Feed]:
    """根据 ID 获取 RSS 源"""
    return session.get(Feed, feed_id)


def get_feed_by_url(session: Session, url: str) -> Optional[Feed]:
    """根据 URL 获取 RSS 源"""
    statement = select(Feed).where(Feed.url == url)
    return session.exec(statement).first()


def update_feed(session: Session, feed_id: int, **kwargs) -> Optional[Feed]:
    """更新 RSS 源"""
    feed = session.get(Feed, feed_id)
    if feed:
        for key, value in kwargs.items():
            setattr(feed, key, value)
        feed.updated_at = datetime.now()
        session.add(feed)
        session.commit()
        session.refresh(feed)
    return feed


# Article 相关操作
def create_article(session: Session, article: Article) -> Article:
    """创建新文章"""
    session.add(article)
    session.commit()
    session.refresh(article)
    logger.info(f"创建 Article: {article.title}")
    return article


def get_article_by_link(session: Session, link: str) -> Optional[Article]:
    """根据链接获取文章（用于去重）"""
    statement = select(Article).where(Article.link == link)
    return session.exec(statement).first()


def get_articles(
    session: Session,
    limit: int = 50,
    category: Optional[str] = None,
    days: Optional[int] = None,
) -> List[Article]:
    """
    获取文章列表

    Args:
        session: 数据库会话
        limit: 返回数量限制
        category: 按分类筛选
        days: 获取最近几天的文章
    """
    statement = select(Article).join(Feed)

    # 按分类筛选
    if category:
        statement = statement.where(Feed.category == category)

    # 按时间筛选
    if days and days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        statement = statement.where(Article.published_at >= cutoff_date)

    # 按发布时间降序排序
    statement = statement.order_by(Article.published_at.desc())

    # 限制数量
    statement = statement.limit(limit)

    results = session.exec(statement).all()
    return list(results)


def article_exists(session: Session, link: str) -> bool:
    """检查文章是否已存在"""
    article = get_article_by_link(session, link)
    return article is not None


def update_article_summary(session: Session, article_id: int, summary: str) -> Optional[Article]:
    """更新文章的 AI 总结"""
    article = session.get(Article, article_id)
    if article:
        article.summary = summary
        session.add(article)
        session.commit()
        session.refresh(article)
        logger.info(f"更新 Article 总结: {article.title}")
    return article
