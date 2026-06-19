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
from app.services.summarizer import summarize_article_bilingual
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def regenerate_summaries(limit: int = None, force: bool = False, concurrency: int = 2, delay: float = 1.0):
    """
    重新生成文章摘要（中英文双语）

    Args:
        limit: 最多处理的文章数量（None 表示处理全部）
        force: 是否强制重新生成（包括已有摘要的文章）
        concurrency: 并发数量（默认 2，避免触发速率限制）
        delay: 每批之间的延迟秒数（默认 1 秒）
    """
    logger.info("=== 开始重新生成摘要（中英文双语） ===")

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
        skip_count = 0

        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"[{i}/{len(articles)}] 处理: {article.title[:50]}...")

                # 检查是否有内容
                if not article.content or len(article.content.strip()) < 10:
                    logger.warning(f"  ⏭️  内容过短，跳过")
                    article.summary = "内容过短，无需总结"
                    session.add(article)
                    session.commit()
                    skip_count += 1
                    continue

                # 生成双语摘要
                zh_summary, en_summary = await summarize_article_bilingual(
                    article.title, article.content, semaphore
                )

                # 判断生成是否成功（检查是否包含错误标记）
                is_success = (
                    zh_summary and
                    not zh_summary.startswith("未配置") and
                    not zh_summary.startswith("内容过短") and
                    not zh_summary.startswith("总结生成") and  # "总结生成超时/失败/异常"
                    not "生成超时" in zh_summary and
                    not "生成失败" in zh_summary and
                    not "生成异常" in zh_summary
                )

                if is_success:
                    article.summary = zh_summary
                    article.summary_en = en_summary
                    session.add(article)
                    session.commit()
                    success_count += 1
                    logger.info(f"  ✅ 成功 | 中文: {len(zh_summary)}字 | 英文: {len(en_summary)}词")
                    logger.debug(f"     中文: {zh_summary[:40]}...")
                    logger.debug(f"     英文: {en_summary[:40]}...")
                else:
                    logger.warning(f"  ⚠️  失败: {zh_summary[:50] if zh_summary else 'NULL'}")
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
        logger.info(f"跳过: {skip_count} 篇")
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
