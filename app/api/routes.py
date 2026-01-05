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
from datetime import datetime, timedelta
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
    date: Optional[str] = Query(None, description="指定具体日期 (YYYY-MM-DD 格式，如 2026-01-05)"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD 格式)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD 格式)"),
    session: Session = Depends(get_session),
):
    """
    获取文章列表

    Args:
        limit: 返回数量限制（1-200）
        category: 按分类筛选（可选）
        days: 获取最近几天的文章（可选）
        date: 指定具体日期，格式 YYYY-MM-DD（可选，优先级最高）
        start_date: 开始日期，格式 YYYY-MM-DD（可选）
        end_date: 结束日期，格式 YYYY-MM-DD（可选）
        session: 数据库会话

    Returns:
        Article 对象列表（包含 Feed 名称和英文摘要）

    日期过滤说明:
        1. 使用 date 参数查询特定日期的文章:
           GET /api/articles?date=2026-01-05

        2. 使用 start_date 和 end_date 查询日期范围:
           GET /api/articles?start_date=2026-01-01&end_date=2026-01-05

        3. 只指定 start_date，查询从该日期到现在的文章:
           GET /api/articles?start_date=2026-01-01

        4. 只指定 end_date，查询到该日期为止的文章:
           GET /api/articles?end_date=2026-01-05

        5. 使用 days 查询最近 N 天的文章:
           GET /api/articles?days=7

    日期过滤优先级:
        date > (start_date + end_date) > days > 无过滤

    组合使用:
        可以与 category 和 limit 组合使用:
        GET /api/articles?date=2026-01-05&category=tech&limit=20
    """
    try:
        articles = get_articles(
            session,
            limit=limit,
            category=category,
            days=days,
            date=date,
            start_date=start_date,
            end_date=end_date,
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


@router.get("/stats")
def get_api_stats(
    hours: int = Query(24, ge=1, le=168, description="统计最近几小时的数据"),
    session: Session = Depends(get_session),
):
    """
    API 使用统计

    提供各端点的调用次数、响应时间、成功率等统计信息

    Args:
        hours: 统计最近几小时的数据（默认 24 小时，最大 168 小时）
        session: 数据库会话

    Returns:
        API 统计信息
    """
    try:
        # 使用原生 SQL 查询统计数据
        import sqlite3
        from app.config import settings

        db_path = settings.database_url.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 计算时间范围
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        # 1. 端点统计
        cursor.execute("""
            SELECT
                path,
                method,
                COUNT(*) as request_count,
                AVG(response_time_ms) as avg_response_time,
                MAX(response_time_ms) as max_response_time,
                MIN(response_time_ms) as min_response_time,
                SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
            FROM api_request_log
            WHERE created_at >= ?
            GROUP BY path, method
            ORDER BY request_count DESC
        """, (cutoff_time,))

        endpoints = []
        for row in cursor.fetchall():
            (path, method, count, avg_time, max_time, min_time, success_count, error_count) = row

            # 计算成功率
            success_rate = (success_count / count * 100) if count > 0 else 0

            endpoints.append({
                "path": path,
                "method": method,
                "requests_24h": count,
                "avg_response_time_ms": round(avg_time, 2) if avg_time else 0,
                "max_response_time_ms": round(max_time, 2) if max_time else 0,
                "min_response_time_ms": round(min_time, 2) if min_time else 0,
                "success_rate": round(success_rate, 2),
                "success_count": success_count,
                "error_count": error_count,
            })

        # 2. 总体统计
        cursor.execute("""
            SELECT
                COUNT(*) as total_requests,
                AVG(response_time_ms) as avg_response_time,
                SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as total_success,
                SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) as server_errors,
                SUM(CASE WHEN status_code >= 400 AND status_code < 500 THEN 1 ELSE 0 END) as client_errors
            FROM api_request_log
            WHERE created_at >= ?
        """, (cutoff_time,))

        total_requests, avg_response_time, total_success, server_errors, client_errors = cursor.fetchone()

        overall_success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0

        # 3. 状态码分布
        cursor.execute("""
            SELECT
                status_code,
                COUNT(*) as count
            FROM api_request_log
            WHERE created_at >= ?
            GROUP BY status_code
            ORDER BY count DESC
        """, (cutoff_time,))

        status_codes = [
            {"code": code, "count": count}
            for code, count in cursor.fetchall()
        ]

        # 4. 最慢的请求
        cursor.execute("""
            SELECT
                path,
                method,
                response_time_ms,
                status_code,
                created_at
            FROM api_request_log
            WHERE created_at >= ?
            ORDER BY response_time_ms DESC
            LIMIT 10
        """, (cutoff_time,))

        slowest_requests = [
            {
                "path": path,
                "method": method,
                "response_time_ms": round(time_ms, 2),
                "status_code": status_code,
                "created_at": created_at
            }
            for path, method, time_ms, status_code, created_at in cursor.fetchall()
        ]

        # 5. 客户端统计
        cursor.execute("""
            SELECT
                client_ip,
                COUNT(*) as request_count
            FROM api_request_log
            WHERE created_at >= ?
            GROUP BY client_ip
            ORDER BY request_count DESC
            LIMIT 10
        """, (cutoff_time,))

        top_clients = [
            {"ip": ip, "requests": count}
            for ip, count in cursor.fetchall()
        ]

        # 获取系统信息（使用同一连接）
        cursor.execute("SELECT COUNT(*) FROM feed")
        active_feeds = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM article")
        total_articles = cursor.fetchone()[0]

        conn.close()

        return {
            "period_hours": hours,
            "generated_at": datetime.now().isoformat(),
            "endpoints": endpoints,
            "overall": {
                "total_requests": total_requests,
                "avg_response_time_ms": round(avg_response_time, 2) if avg_response_time else 0,
                "success_rate": round(overall_success_rate, 2),
                "success_count": total_success,
                "server_errors": server_errors,
                "client_errors": client_errors,
            },
            "status_codes": status_codes,
            "slowest_requests": slowest_requests,
            "top_clients": top_clients,
            "system": {
                "active_feeds": active_feeds,
                "total_articles": total_articles,
            }
        }

    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


# ============================================================================
# RSS 输出端点
# ============================================================================

from fastapi import Response
from app.services.rss_generator import generate_rss_response, generate_category_rss


@router.get("/rss", response_class=Response)
@router.get("/rss/{summary_type}", response_class=Response)
def rss_feed(
    summary_type: str = "zh",
    category: Optional[str] = Query(None, description="按分类筛选"),
    days: Optional[int] = Query(None, ge=1, le=30, description="获取最近几天的文章"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    session: Session = Depends(get_session),
):
    """
    RSS 订阅源

    生成标准的 RSS 2.0 格式输出，可供任何 RSS 阅读器订阅。

    **基础用法**:
        GET /rss                    # 中文摘要
        GET /rss/en                 # 英文摘要
        GET /rss/bilingual          # 双语混合

    **过滤选项**:
        ?category=科技              # 按分类筛选
        &days=7                     # 最近 N 天
        &limit=50                   # 数量限制

    **示例**:
        GET /rss                    # 所有最新文章（中文）
        GET /rss/en                 # 所有最新文章（英文）
        GET /rss/bilingual          # 所有最新文章（双语）
        GET /rss?category=科技       # 科技分类（中文）
        GET /rss?days=7             # 最近 7 天
        GET /rss?limit=100          # 最多 100 篇

    **订阅方式**:
        Feedly/Inoreader 等:
        1. 添加订阅源
        2. 输入: http://your-server:8000/rss
        3. 完成

    Args:
        summary_type: 摘要类型 (zh/en/bilingual)
        category: 按分类筛选
        days: 获取最近几天的文章
        limit: 返回数量限制
        session: 数据库会话

    Returns:
        RSS XML (application/rss+xml)
    """
    try:
        # 验证 summary_type
        if summary_type not in ["zh", "en", "bilingual"]:
            summary_type = "zh"

        # 获取文章
        logger.info(f"RSS 请求: type={summary_type}, category={category}, days={days}, limit={limit}")
        articles = get_articles(
            session,
            limit=limit,
            category=category,
            days=days,
            date=None,
            start_date=None,
            end_date=None
        )
        logger.info(f"RSS: 从数据库获取了 {len(articles)} 篇文章")

        # 生成 RSS
        base_url = "http://localhost:8000"  # TODO: 从配置读取

        # 根据是否有分类自定义标题
        title = None
        description = None
        if category:
            title = f"AI-RSS-Hub - {category}"
            description = f"AI 智能聚合的 {category} 资讯"

        rss_xml = generate_rss_response(
            articles=articles,
            summary_type=summary_type,
            base_url=base_url,
            title=title,
            description=description
        )

        logger.info(
            f"生成 RSS: {len(articles)} 篇文章, "
            f"类型={summary_type}, 分类={category or '全部'}"
        )

        return Response(
            content=rss_xml,
            media_type="application/rss+xml; charset=utf-8"
        )

    except Exception as e:
        logger.error(f"生成 RSS 失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成 RSS 失败: {str(e)}")


@router.get("/rss/category/{category}", response_class=Response)
def rss_category_feed(
    category: str,
    summary_type: str = Query("zh", description="摘要类型 (zh/en/bilingual)"),
    days: Optional[int] = Query(None, ge=1, le=30, description="获取最近几天的文章"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    session: Session = Depends(get_session),
):
    """
    按分类订阅 RSS

    为特定分类的文章生成 RSS 订阅源。

    **示例**:
        GET /rss/category/tech        # 科技分类（中文）
        GET /rss/category/科技?summary_type=en    # 科技分类（英文）
        GET /rss/category/科技?days=7             # 最近 7 天

    Args:
        category: 分类名称
        summary_type: 摘要类型
        days: 获取最近几天的文章
        limit: 返回数量限制
        session: 数据库会话

    Returns:
        RSS XML
    """
    try:
        # 验证 summary_type
        if summary_type not in ["zh", "en", "bilingual"]:
            summary_type = "zh"

        # 获取文章
        articles = get_articles(
            session,
            limit=limit,
            category=category,
            days=days,
            date=None,
            start_date=None,
            end_date=None
        )

        # 生成 RSS
        base_url = "http://localhost:8000"
        rss_xml = generate_category_rss(
            articles=articles,
            category=category,
            summary_type=summary_type,
            base_url=base_url
        )

        logger.info(f"生成分类 RSS [{category}]: {len(articles)} 篇文章, 类型={summary_type}")

        return Response(
            content=rss_xml,
            media_type="application/rss+xml; charset=utf-8"
        )

    except Exception as e:
        logger.error(f"生成分类 RSS 失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成分类 RSS 失败: {str(e)}")

