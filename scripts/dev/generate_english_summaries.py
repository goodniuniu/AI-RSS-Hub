#!/usr/bin/env python3
"""
为现有文章批量生成英文摘要

这个脚本会为数据库中所有缺少英文摘要的文章生成 summary_en 字段。
"""
import sys
import asyncio
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.summarizer import summarize_article_bilingual
from app.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_articles_without_en_summary(db_path: str, limit: int = None) -> List[Tuple[int, str, str]]:
    """
    获取没有英文摘要的文章列表

    Args:
        db_path: 数据库路径
        limit: 限制处理数量（用于测试）

    Returns:
        文章列表 [(id, title, content), ...]
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT id, title, link
        FROM article
        WHERE summary_en IS NULL
        ORDER BY published_at DESC
    """
    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query)
    articles = cursor.fetchall()
    conn.close()

    return articles


def update_article_summary(db_path: str, article_id: int, summary_en: str):
    """
    更新文章的英文摘要

    Args:
        db_path: 数据库路径
        article_id: 文章ID
        summary_en: 英文摘要
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE article SET summary_en = ? WHERE id = ?",
        (summary_en, article_id)
    )
    conn.commit()
    conn.close()


async def process_article(article_id: int, title: str, link: str, semaphore: asyncio.Semaphore) -> bool:
    """
    处理单篇文章，生成英文摘要

    Args:
        article_id: 文章ID
        title: 文章标题
        link: 文章链接
        semaphore: 并发控制信号量

    Returns:
        是否成功
    """
    try:
        # 使用标题和链接生成摘要
        # 注意：由于我们没有文章全文，使用链接作为内容
        zh_summary, en_summary = await summarize_article_bilingual(title, link, semaphore)

        if en_summary and len(en_summary) > 10:
            update_article_summary(settings.database_url.replace("sqlite:///", ""), article_id, en_summary)
            logger.info(f"✅ [{article_id}] {title[:50]}...")
            return True
        else:
            logger.warning(f"⚠️  [{article_id}] 摘要质量不佳: {title[:50]}...")
            return False

    except Exception as e:
        logger.error(f"❌ [{article_id}] 处理失败: {title[:50]}... - {e}")
        return False


async def generate_english_summaries(limit: int = None, batch_size: int = 5):
    """
    批量生成英文摘要

    Args:
        limit: 限制处理数量（用于测试），None 表示处理全部
        batch_size: 并发批处理大小
    """
    logger.info("=" * 60)
    logger.info("  批量生成英文摘要")
    logger.info("=" * 60)
    logger.info("")

    # 获取数据库路径
    db_path = settings.database_url.replace("sqlite:///", "")
    logger.info(f"数据库路径: {db_path}")
    logger.info("")

    # 获取需要处理的文章
    logger.info("⏳ 步骤1: 获取文章列表...")
    articles = get_articles_without_en_summary(db_path, limit)
    total_count = len(articles)

    if total_count == 0:
        logger.info("✅ 所有文章都已有英文摘要，无需处理")
        return

    logger.info(f"找到 {total_count} 篇需要处理的文章")
    logger.info("")

    # 创建并发控制信号量
    semaphore = asyncio.Semaphore(batch_size)

    # 批量处理
    logger.info(f"⏳ 步骤2: 开始批量处理（并发数: {batch_size}）...")
    logger.info("")

    start_time = datetime.now()
    success_count = 0
    failed_count = 0

    for i, (article_id, title, link) in enumerate(articles, 1):
        logger.info(f"[{i}/{total_count}] 处理中...")
        success = await process_article(article_id, title, link, semaphore)

        if success:
            success_count += 1
        else:
            failed_count += 1

        # 每处理 10 篇文章显示一次进度
        if i % 10 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            avg_time = elapsed / i
            remaining = (total_count - i) * avg_time
            logger.info(f"进度: {i}/{total_count} ({i*100//total_count}%), "
                       f"成功: {success_count}, 失败: {failed_count}, "
                       f"预计剩余: {remaining:.0f}秒")
            logger.info("")

    # 完成
    elapsed_time = (datetime.now() - start_time).total_seconds()

    logger.info("")
    logger.info("=" * 60)
    logger.info("  ✅ 批量处理完成")
    logger.info("=" * 60)
    logger.info(f"总文章数: {total_count}")
    logger.info(f"成功: {success_count}")
    logger.info(f"失败: {failed_count}")
    logger.info(f"总耗时: {elapsed_time:.1f} 秒")
    logger.info(f"平均每篇: {elapsed_time/total_count:.1f} 秒")
    logger.info("")

    # 验证结果
    logger.info("⏳ 步骤3: 验证结果...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM article WHERE summary_en IS NOT NULL")
    has_summary = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM article WHERE summary_en IS NULL")
    still_missing = cursor.fetchone()[0]
    conn.close()

    logger.info(f"已有英文摘要的文章: {has_summary}")
    logger.info(f"仍缺少英文摘要的文章: {still_missing}")
    logger.info("")

    if success_count > 0:
        logger.info("=" * 60)
        logger.info("  ✅ 任务完成！")
        logger.info("=" * 60)
        logger.info("")
        logger.info("下一步:")
        logger.info("  1. 测试 API 响应，确认 summary_en 字段有值")
        logger.info("  2. 查看 API 文档已更新")
        logger.info("  3. 继续 Phase 5: 配置和文档更新")
    else:
        logger.warning("=" * 60)
        logger.warning("  ⚠️  所有文章处理失败")
        logger.warning("=" * 60)
        logger.warning("")
        logger.warning("建议:")
        logger.warning("  1. 检查 API Key 配置")
        logger.warning("  2. 检查网络连接")
        logger.warning("  3. 查看详细错误日志")


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="为现有文章批量生成英文摘要")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="限制处理数量（用于测试），默认处理全部"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=3,
        help="并发批处理大小，默认 3"
    )

    args = parser.parse_args()

    if args.limit:
        logger.info(f"测试模式: 仅处理前 {args.limit} 篇文章")
        logger.info("")

    try:
        await generate_english_summaries(limit=args.limit, batch_size=args.batch_size)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"")
        logger.error(f"❌ 执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
