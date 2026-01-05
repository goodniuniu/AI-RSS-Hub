"""
FastAPI 路由定义
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from app.database import get_session
from app.models import Feed, FeedCreate, FeedResponse, ArticleResponse
from app.crud import (
    create_feed,
    get_all_feeds,
    get_feed_by_url,
    get_articles,
)
from app.security.auth import verify_api_token
from app.security.validators import FeedCreateValidated
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/feeds", response_model=FeedResponse, status_code=201)
def add_feed(
    feed_data: FeedCreateValidated,
    session: Session = Depends(get_session),
    authenticated: bool = Depends(verify_api_token),
):
    """
    添加新的 RSS 源（需要认证）

    Args:
        feed_data: Feed 创建数据
        session: 数据库会话
        authenticated: 认证状态

    Returns:
        创建的 Feed 对象

    Raises:
        HTTPException: 如果 URL 已存在
    """
    # 检查 URL 是否已存在
    existing_feed = get_feed_by_url(session, feed_data.url)
    if existing_feed:
        raise HTTPException(
            status_code=400,
            detail=f"RSS 源已存在: {feed_data.url}",
        )

    # 创建新的 Feed
    feed = Feed(**feed_data.model_dump())

    try:
        created_feed = create_feed(session, feed)
        logger.info(f"成功添加 RSS 源: {created_feed.name}")
        return created_feed
    except Exception as e:
        logger.error(f"添加 RSS 源失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加 RSS 源失败: {str(e)}")


@router.get("/feeds", response_model=List[FeedResponse])
def list_feeds(
    active_only: bool = Query(False, description="仅返回活跃的源"),
    session: Session = Depends(get_session),
):
    """
    获取所有 RSS 源列表

    Args:
        active_only: 是否仅返回活跃的源
        session: 数据库会话

    Returns:
        Feed 对象列表
    """
    try:
        feeds = get_all_feeds(session, active_only=active_only)
        return feeds
    except Exception as e:
        logger.error(f"获取 RSS 源列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    days: Optional[int] = Query(None, ge=1, le=365, description="获取最近几天的文章"),
    session: Session = Depends(get_session),
):
    """
    获取文章列表

    Args:
        limit: 返回数量限制（1-200）
        category: 按分类筛选（可选）
        days: 获取最近几天的文章（可选）
        session: 数据库会话

    Returns:
        Article 对象列表（包含 Feed 名称）
    """
    try:
        articles = get_articles(
            session,
            limit=limit,
            category=category,
            days=days,
        )

        # 转换为响应模型，并添加 feed_name 和 summary_en
        response_articles = []
        for article in articles:
            article_dict = {
                "id": article.id,
                "title": article.title,
                "link": article.link,
                "summary": article.summary,
                "summary_en": article.summary_en,  # 英文摘要
                "published_at": article.published_at,
                "feed_id": article.feed_id,
                "feed_name": article.feed.name if article.feed else None,
                "created_at": article.created_at,
            }
            response_articles.append(ArticleResponse(**article_dict))

        return response_articles

    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文章失败: {str(e)}")


@router.post("/feeds/fetch")
def trigger_fetch(
    session: Session = Depends(get_session),
    authenticated: bool = Depends(verify_api_token),
):
    """
    手动触发 RSS 抓取（需要认证）

    Returns:
        抓取统计信息
    """
    try:
        from app.services.rss_fetcher import fetch_all_feeds

        logger.info("手动触发 RSS 抓取")
        stats = fetch_all_feeds(session)

        return {
            "status": "success",
            "message": f"成功抓取 {stats['total_feeds']} 个源，获取 {stats['total_articles']} 篇新文章",
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"手动抓取失败: {e}")
        raise HTTPException(status_code=500, detail=f"抓取失败: {str(e)}")


@router.get("/health")
def health_check():
    """
    健康检查接口
    """
    return {
        "status": "ok",
        "message": "AI-RSS-Hub is running",
    }
