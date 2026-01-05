#!/usr/bin/env python3
"""
创建 API 请求日志表

用于记录所有 API 请求的详细信息，支持后续的统计和分析
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import sqlite3
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def create_api_request_log_table():
    """创建 API 请求日志表"""

    # 获取数据库路径
    db_path = settings.database_url.replace("sqlite:///", "")
    logger.info(f"数据库路径: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 创建请求日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_request_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id VARCHAR(20),
                method VARCHAR(10),
                path VARCHAR(255),
                query_params TEXT,
                status_code INTEGER,
                response_time_ms REAL,
                client_ip VARCHAR(50),
                user_agent TEXT,
                error_msg TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ 表 api_request_log 创建成功")

        # 创建索引
        indexes = [
            ("idx_api_log_path", "CREATE INDEX IF NOT EXISTS idx_api_log_path ON api_request_log(path)"),
            ("idx_api_log_created", "CREATE INDEX IF NOT EXISTS idx_api_log_created ON api_request_log(created_at)"),
            ("idx_api_log_status", "CREATE INDEX IF NOT EXISTS idx_api_log_status ON api_request_log(status_code)"),
            ("idx_api_log_method", "CREATE INDEX IF NOT EXISTS idx_api_log_method ON api_request_log(method)"),
            ("idx_api_log_request_id", "CREATE INDEX IF NOT EXISTS idx_api_log_request_id ON api_request_log(request_id)"),
        ]

        for index_name, sql in indexes:
            cursor.execute(sql)
            logger.info(f"✅ 索引 {index_name} 创建成功")

        # 验证表结构
        cursor.execute("PRAGMA table_info(api_request_log)")
        columns = cursor.fetchall()

        logger.info("")
        logger.info("=" * 60)
        logger.info("  表结构验证")
        logger.info("=" * 60)
        for col in columns:
            logger.info(f"  {col[1]:<20} {col[2]:<15}")

        conn.commit()

        logger.info("")
        logger.info("=" * 60)
        logger.info("  ✅ 数据库表创建完成")
        logger.info("=" * 60)
        logger.info("")
        logger.info("下一步:")
        logger.info("  1. 重启应用以应用更改")
        logger.info("  2. 访问 /api/stats 查看统计信息")
        logger.info("  3. 查看 API 请求日志")

    except Exception as e:
        logger.error(f"❌ 创建表失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    create_api_request_log_table()
