"""
定时任务调度器
使用 APScheduler 定期抓取 RSS 源
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session
from app.database import engine
from app.services.rss_fetcher import fetch_all_feeds
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = BackgroundScheduler()


def scheduled_fetch_job():
    """
    定时任务：抓取所有 RSS 源
    """
    logger.info("=== 定时任务开始执行 ===")

    try:
        with Session(engine) as session:
            stats = fetch_all_feeds(session)
            logger.info(f"定时任务完成: {stats}")
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}")

    logger.info("=== 定时任务执行结束 ===")


def start_scheduler():
    """
    启动调度器
    """
    if scheduler.running:
        logger.warning("调度器已经在运行中")
        return

    try:
        # 添加定时任务
        scheduler.add_job(
            func=scheduled_fetch_job,
            trigger=IntervalTrigger(hours=settings.fetch_interval_hours),
            id="rss_fetch_job",
            name="RSS 抓取任务",
            replace_existing=True,
        )

        # 启动调度器
        scheduler.start()

        logger.info(
            f"调度器已启动，任务将每 {settings.fetch_interval_hours} 小时执行一次"
        )

        # 立即执行一次（可选）
        # scheduled_fetch_job()

    except Exception as e:
        logger.error(f"启动调度器失败: {e}")
        raise


def stop_scheduler():
    """
    停止调度器
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("调度器已停止")
    else:
        logger.warning("调度器未在运行")


def get_scheduler_status() -> dict:
    """
    获取调度器状态

    Returns:
        dict: 包含调度器运行状态和任务信息
    """
    if not scheduler.running:
        return {"running": False, "jobs": []}

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            }
        )

    return {"running": True, "jobs": jobs}
