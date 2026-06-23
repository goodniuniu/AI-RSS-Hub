#!/usr/bin/env python3
"""
为现有文章批量生成二维码

用法:
    python utils/generate_qr_codes.py
    python utils/generate_qr_codes.py --limit 100
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.database import engine
from app.models import Article
from app.services.qr_generator import generate_qr_code_url
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_qr_codes(limit: int = None, force: bool = False):
    """
    为现有文章生成二维码

    Args:
        limit: 最多处理的文章数量
        force: 是否强制重新生成（包括已有二维码的文章）
    """
    logger.info("=== 开始批量生成二维码 ===")

    with Session(engine) as session:
        # 查询需要处理的文章
        query = select(Article)
        if not force:
            # 只查询没有二维码的文章
            query = query.where(Article.qr_code_url.is_(None))

        # 按创建时间倒序，优先处理新文章
        query = query.order_by(Article.created_at.desc())

        if limit:
            query = query.limit(limit)

        result = session.exec(query)
        articles = result.all()

        if not articles:
            logger.info("没有需要处理的文章")
            return

        logger.info(f"找到 {len(articles)} 篇文章需要生成二维码")

        success_count = 0
        failed_count = 0

        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"[{i}/{len(articles)}] 处理: {article.title[:50]}...")

                # 生成二维码
                qr_url = generate_qr_code_url(article.id, article.link)

                if qr_url:
                    article.qr_code_url = qr_url
                    session.add(article)
                    session.commit()
                    success_count += 1
                    logger.info(f"  ✅ 成功: {qr_url}")
                else:
                    failed_count += 1
                    logger.warning(f"  ⚠️  生成失败")

            except Exception as e:
                logger.error(f"  ❌ 处理失败: {e}")
                failed_count += 1
                continue

        logger.info("=== 批量生成完成 ===")
        logger.info(f"成功: {success_count} 篇")
        logger.info(f"失败: {failed_count} 篇")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="为现有文章批量生成二维码")
    parser.add_argument(
        "--limit", "-l", type=int, help="最多处理的文章数量（默认处理全部）"
    )
    parser.add_argument(
        "--force", "-f", action="store_true", help="强制重新生成（包括已有二维码的文章）"
    )

    args = parser.parse_args()

    try:
        generate_qr_codes(limit=args.limit, force=args.force)
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
