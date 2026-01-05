"""
数据库 CRUD 操作
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
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
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Article]:
    """
    获取文章列表

    Args:
        session: 数据库会话
        limit: 返回数量限制
        category: 按分类筛选
        days: 获取最近几天的文章
        date: 指定具体日期（YYYY-MM-DD 格式）
        start_date: 开始日期（YYYY-MM-DD 格式）
        end_date: 结束日期（YYYY-MM-DD 格式）

    Returns:
        Article 对象列表

    日期过滤优先级:
        1. date - 如果指定，只返回该日期的文章
        2. start_date 和 end_date - 如果指定，返回该范围内的文章
        3. days - 返回最近 N 天的文章
        4. 无过滤 - 返回所有文章（受 limit 限制）
    """
    statement = select(Article).join(Feed).options(selectinload(Article.feed))

    # 按分类筛选
    if category:
        statement = statement.where(Feed.category == category)

    # 按日期筛选（优先级 1: 指定具体日期）
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            # 查询该日期的文章（从当天 00:00:00 到 23:59:59）
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            statement = statement.where(
                Article.published_at >= start_datetime,
                Article.published_at <= end_datetime
            )
            logger.info(f"按日期筛选: {date}")
        except ValueError as e:
            logger.error(f"日期格式错误: {date}, {e}")
            raise ValueError(f"日期格式错误，应为 YYYY-MM-DD 格式: {date}")

    # 按日期范围筛选（优先级 2: 日期范围）
    elif start_date or end_date:
        try:
            if start_date:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                # 设置为当天 00:00:00
                start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                statement = statement.where(Article.published_at >= start_datetime)

            if end_date:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
                # 设置为当天 23:59:59
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
                statement = statement.where(Article.published_at <= end_datetime)

            logger.info(f"按日期范围筛选: {start_date or '开始'} 至 {end_date or '结束'}")
        except ValueError as e:
            logger.error(f"日期格式错误: {e}")
            raise ValueError(f"日期格式错误，应为 YYYY-MM-DD 格式")

    # 按天数筛选（优先级 3: 最近 N 天）
    elif days and days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        statement = statement.where(Article.published_at >= cutoff_date)
        logger.info(f"按最近 {days} 天筛选")

    # 按发布时间降序排序
    statement = statement.order_by(Article.published_at.desc())

    # 限制数量
    statement = statement.limit(limit)

    results = session.exec(statement).all()
    logger.info(f"查询到 {len(results)} 篇文章")
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
