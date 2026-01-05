"""
RSS 抓取服务
负责抓取 RSS 源并解析文章
"""
import feedparser
import asyncio
from datetime import datetime
from typing import List, Optional, Tuple
from sqlmodel import Session
from app.models import Feed, Article
from app.crud import get_all_feeds, article_exists, create_article
from app.services.summarizer import summarize_article_bilingual
from app.config import settings
import logging
import time
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)


def parse_published_date(entry) -> Optional[datetime]:
    """
    解析 RSS 条目的发布时间

    Args:
        entry: feedparser 解析的条目

    Returns:
        datetime 对象，如果解析失败则返回 None
    """
    # 尝试多个可能的时间字段
    for date_field in ["published_parsed", "updated_parsed", "created_parsed"]:
        if hasattr(entry, date_field) and getattr(entry, date_field):
            try:
                time_tuple = getattr(entry, date_field)
                return datetime(*time_tuple[:6])
            except Exception as e:
                logger.warning(f"解析时间字段 {date_field} 失败: {e}")

    # 尝试字符串格式的时间
    for date_field in ["published", "updated", "created"]:
        if hasattr(entry, date_field) and getattr(entry, date_field):
            try:
                return parsedate_to_datetime(getattr(entry, date_field))
            except Exception as e:
                logger.warning(f"解析时间字符串 {date_field} 失败: {e}")

    return None


async def fetch_feed(feed: Feed, session: Session) -> int:
    """
    抓取单个 RSS 源（异步版本）

    Args:
        feed: Feed 对象
        session: 数据库会话

    Returns:
        新增文章数量
    """
    logger.info(f"开始抓取 RSS 源: {feed.name} ({feed.url})")

    try:
        # 解析 RSS
        parsed = feedparser.parse(feed.url)

        # 检查是否解析成功
        if parsed.bozo:
            logger.warning(f"RSS 解析警告: {feed.name}, 错误: {parsed.bozo_exception}")

        if not hasattr(parsed, "entries") or not parsed.entries:
            logger.warning(f"RSS 源没有条目: {feed.name}")
            return 0

        # 用于存储需要生成摘要的文章
        articles_to_summarize: List[Tuple[Article, str]] = []
        new_articles_count = 0

        # 遍历所有条目，先保存文章
        for entry in parsed.entries:
            try:
                # 获取文章链接（用于去重）
                link = entry.get("link", "")
                if not link:
                    logger.warning(f"条目缺少链接，跳过: {entry.get('title', 'Unknown')}")
                    continue

                # 检查文章是否已存在
                if article_exists(session, link):
                    logger.debug(f"文章已存在，跳过: {link}")
                    continue

                # 提取文章信息
                title = entry.get("title", "无标题")

                # 提取内容（尝试多个字段）
                content = ""
                if hasattr(entry, "content") and entry.content:
                    content = entry.content[0].get("value", "")
                elif hasattr(entry, "summary"):
                    content = entry.summary
                elif hasattr(entry, "description"):
                    content = entry.description

                # 解析发布时间
                published_at = parse_published_date(entry) or datetime.now()

                # 创建文章对象
                article = Article(
                    title=title,
                    link=link,
                    content=content,
                    published_at=published_at,
                    feed_id=feed.id,
                )

                # 保存到数据库
                article = create_article(session, article)

                # 如果有内容且配置了 API Key，收集起来待生成摘要
                if settings.openai_api_key and content and len(content.strip()) >= 10:
                    articles_to_summarize.append((article, content))

                new_articles_count += 1
                logger.info(f"新增文章: {title[:50]}...")

            except Exception as e:
                logger.error(f"处理条目失败: {e}")
                continue

        # 并发生成所有文章的双语摘要
        if articles_to_summarize:
            logger.info(f"开始并发生成 {len(articles_to_summarize)} 篇文章的双语摘要（中英文）...")
            summary_start_time = time.time()

            # 创建信号量控制并发数量
            semaphore = asyncio.Semaphore(settings.max_concurrent_summaries)

            # 创建所有双语摘要任务
            tasks = []
            for article, content in articles_to_summarize:
                task = summarize_article_bilingual(article.title, content, semaphore)
                tasks.append((article, task))

            # 并发执行所有双语摘要任务
            summaries = await asyncio.gather(*[task for _, task in tasks])

            # 批量更新数据库（中英文摘要）
            for (article, _), (zh_summary, en_summary) in zip(tasks, summaries):
                if zh_summary and "失败" not in zh_summary and "异常" not in zh_summary:
                    article.summary = zh_summary          # 中文摘要
                    article.summary_en = en_summary      # 英文摘要
                    session.add(article)

            session.commit()

            summary_duration = time.time() - summary_start_time
            logger.info(
                f"双语摘要生成完成: {len(articles_to_summarize)} 篇, "
                f"耗时 {summary_duration:.2f} 秒, "
                f"平均 {summary_duration / len(articles_to_summarize):.2f} 秒/篇"
            )

        logger.info(f"RSS 源 {feed.name} 抓取完成，新增 {new_articles_count} 篇文章")
        return new_articles_count

    except Exception as e:
        logger.error(f"抓取 RSS 源失败: {feed.name}, 错误: {e}")
        return 0


async def fetch_all_feeds_async(session: Session) -> dict:
    """
    抓取所有活跃的 RSS 源（异步版本）

    Args:
        session: 数据库会话

    Returns:
        抓取统计信息
    """
    logger.info("开始批量抓取所有 RSS 源...")
    start_time = time.time()

    # 获取所有活跃的 Feed
    feeds = get_all_feeds(session, active_only=True)

    if not feeds:
        logger.warning("没有活跃的 RSS 源")
        return {"total_feeds": 0, "total_articles": 0, "duration": 0}

    # 串行抓取每个 Feed（避免同时解析多个 RSS 源）
    total_articles = 0
    for feed in feeds:
        try:
            count = await fetch_feed(feed, session)
            total_articles += count
        except Exception as e:
            logger.error(f"抓取 Feed {feed.name} 时发生异常: {e}")
            continue

    duration = time.time() - start_time

    stats = {
        "total_feeds": len(feeds),
        "total_articles": total_articles,
        "duration": round(duration, 2),
    }

    logger.info(
        f"批量抓取完成: {stats['total_feeds']} 个源, "
        f"{stats['total_articles']} 篇新文章, "
        f"耗时 {stats['duration']} 秒"
    )

    return stats


def fetch_all_feeds(session: Session) -> dict:
    """
    抓取所有活跃的 RSS 源（同步版本，用于兼容）

    Args:
        session: 数据库会话

    Returns:
        抓取统计信息
    """
    # 创建新的事件循环来运行异步版本
    # 这对于在 ThreadPoolExecutor 线程中运行是必需的（如 APScheduler）
    try:
        return asyncio.run(fetch_all_feeds_async(session))
    except Exception as e:
        logger.error(f"异步抓取失败，使用同步方式: {e}")
        # 降级到简单的同步处理（不生成摘要）
        logger.info("开始批量抓取所有 RSS 源（同步模式，不生成摘要）...")
        start_time = time.time()

        feeds = get_all_feeds(session, active_only=True)
        if not feeds:
            return {"total_feeds": 0, "total_articles": 0, "duration": 0}

        total_articles = 0
        for feed in feeds:
            try:
                parsed = feedparser.parse(feed.url)
                if not hasattr(parsed, "entries") or not parsed.entries:
                    continue

                for entry in parsed.entries:
                    link = entry.get("link", "")
                    if not link or article_exists(session, link):
                        continue

                    title = entry.get("title", "无标题")
                    content = ""
                    if hasattr(entry, "content") and entry.content:
                        content = entry.content[0].get("value", "")
                    elif hasattr(entry, "summary"):
                        content = entry.summary

                    published_at = parse_published_date(entry) or datetime.now()

                    article = Article(
                        title=title,
                        link=link,
                        content=content,
                        published_at=published_at,
                        feed_id=feed.id,
                    )
                    create_article(session, article)
                    total_articles += 1
            except Exception as e:
                logger.error(f"抓取 Feed {feed.name} 失败: {e}")

        duration = time.time() - start_time
        return {
            "total_feeds": len(feeds),
            "total_articles": total_articles,
            "duration": round(duration, 2),
        }
