#!/usr/bin/env python3
"""
数据库迁移脚本：添加 summary_en 字段到 Article 表

此脚本将为 article 表添加 summary_en 字段用于存储英文摘要
"""
import sys
from pathlib import Path
import sqlite3
import logging

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_db_path() -> str:
    """从settings获取数据库文件路径"""
    # database_url格式: sqlite:///./ai_rss_hub.db
    db_url = settings.database_url or "sqlite:///./ai_rss_hub.db"
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "")
    return db_url


def check_field_exists(cursor: sqlite3.Cursor, table_name: str, field_name: str) -> bool:
    """检查字段是否已存在"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    return field_name in columns


def add_summary_en_field():
    """添加 summary_en 字段到 article 表"""
    db_path = get_db_path()

    logger.info("=" * 60)
    logger.info("  数据库迁移：添加 summary_en 字段")
    logger.info("=" * 60)
    logger.info(f"数据库路径: {db_path}")
    logger.info("")

    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查字段是否已存在
        logger.info("⏳ 检查字段状态...")
        if check_field_exists(cursor, 'article', 'summary_en'):
            logger.info("ℹ️  summary_en 字段已存在，无需添加")
            logger.info("")
            logger.info("✅ 迁移完成（字段已存在）")
            return

        logger.info("✓ summary_en 字段不存在，准备添加...")
        logger.info("")

        # 添加字段
        logger.info("⏳ 添加 summary_en 字段...")
        cursor.execute(
            "ALTER TABLE article ADD COLUMN summary_en TEXT"
        )
        conn.commit()
        logger.info("✓ 字段添加成功")
        logger.info("")

        # 验证字段已添加
        logger.info("⏳ 验证字段...")
        if check_field_exists(cursor, 'article', 'summary_en'):
            logger.info("✓ 验证成功：summary_en 字段已存在")
        else:
            raise Exception("字段添加失败")

        # 显示表结构
        logger.info("")
        logger.info("📋 Article 表结构（部分）：")
        cursor.execute("PRAGMA table_info(article)")
        columns = cursor.fetchall()
        for col in columns:
            if col[1] in ['id', 'title', 'summary', 'summary_en', 'created_at']:
                logger.info(f"   • {col[1]:15} {col[2]:10} {col[3]:10} {col[4] or ''}")

        conn.close()
        logger.info("")
        logger.info("=" * 60)
        logger.info("  ✅ 迁移成功完成！")
        logger.info("=" * 60)
        logger.info("")
        logger.info("下一步：")
        logger.info("  1. 重启应用使模型更新生效")
        logger.info("  2. 测试双语摘要生成功能")
        logger.info("")

    except Exception as e:
        logger.error("")
        logger.error("=" * 60)
        logger.error("  ❌ 迁移失败")
        logger.error("=" * 60)
        logger.error(f"错误信息: {e}")
        logger.error("")
        logger.error("建议：")
        logger.error("  1. 检查数据库文件是否存在")
        logger.error("  2. 检查文件权限")
        logger.error("  3. 查看详细错误日志")
        logger.error("")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)


if __name__ == "__main__":
    add_summary_en_field()
