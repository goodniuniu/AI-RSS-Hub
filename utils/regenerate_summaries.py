#!/home/sam/Github/AI-RSS-Hub/venv/bin/python
"""
重新生成文章摘要
为所有 summary 为 null 的文章生成 AI 摘要
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select
from app.database import engine
from app.models import Article
from app.services.summarizer import summarize_text_async
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def regenerate_summaries(limit: int = None, force: bool = False, concurrency: int = 2, delay: float = 1.0):
    """
    重新生成文章摘要

    Args:
        limit: 最多处理的文章数量（None 表示处理全部）
        force: 是否强制重新生成（包括已有摘要的文章）
        concurrency: 并发数量（默认 2，避免触发速率限制）
        delay: 每批之间的延迟秒数（默认 1 秒）
    """
    logger.info("=== 开始重新生成摘要 ===")

    with Session(engine) as session:
        # 查询需要处理的文章
        query = select(Article)
        if not force:
            # 只查询 summary 为 null 的文章
            query = query.where(Article.summary.is_(None))

        # 按创建时间倒序，优先处理新文章
        query = query.order_by(Article.created_at.desc())

        if limit:
            query = query.limit(limit)

        result = session.exec(query)
        articles = result.all()

        if not articles:
            logger.info("没有需要处理的文章")
            return

        logger.info(f"找到 {len(articles)} 篇文章需要生成摘要")
        logger.info(f"并发数: {concurrency}, 批次延迟: {delay}秒")

        # 创建信号量控制并发数量（使用更保守的默认值）
        semaphore = asyncio.Semaphore(concurrency)

        success_count = 0
        failed_count = 0

        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"[{i}/{len(articles)}] 处理: {article.title[:50]}...")

                # 检查是否有内容
                if not article.content or len(article.content.strip()) < 10:
                    logger.warning(f"  内容过短，跳过")
                    article.summary = "内容过短，无需总结"
                    session.add(article)
                    session.commit()
                    continue

                # 生成摘要
                summary = await summarize_text_async(article.content, semaphore)

                if summary and "失败" not in summary and "异常" not in summary:
                    article.summary = summary
                    session.add(article)
                    session.commit()
                    success_count += 1
                    logger.info(f"  ✅ 成功: {summary[:50]}...")
                else:
                    logger.warning(f"  ⚠️  摘要生成失败: {summary}")
                    failed_count += 1

                # 添加延迟避免速率限制（每 N 篇暂停一次）
                if i % concurrency == 0 and i < len(articles):
                    logger.info(f"  ⏸️  暂停 {delay} 秒以避免速率限制...")
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"  ❌ 处理失败: {e}")
                failed_count += 1
                # 遇到错误时额外等待
                await asyncio.sleep(delay * 2)
                continue

        logger.info("=== 摘要生成完成 ===")
        logger.info(f"成功: {success_count} 篇")
        logger.info(f"失败: {failed_count} 篇")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="重新生成文章摘要")
    parser.add_argument(
        "--limit", "-l", type=int, help="最多处理的文章数量（默认处理全部）"
    )
    parser.add_argument(
        "--force", "-f", action="store_true", help="强制重新生成（包括已有摘要的文章）"
    )
    parser.add_argument(
        "--concurrency", "-c", type=int, default=2, help="并发请求数（默认 2，避免速率限制）"
    )
    parser.add_argument(
        "--delay", "-d", type=float, default=1.0, help="批次间延迟秒数（默认 1.0 秒）"
    )

    args = parser.parse_args()

    # 检查 API Key
    if not settings.openai_api_key:
        logger.error("❌ 未配置 OPENAI_API_KEY，请在 .env 文件中配置")
        sys.exit(1)

    # 运行
    asyncio.run(regenerate_summaries(
        limit=args.limit,
        force=args.force,
        concurrency=args.concurrency,
        delay=args.delay
    ))
