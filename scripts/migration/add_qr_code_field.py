#!/usr/bin/env python3
"""
数据库迁移脚本：为 article 表添加 qr_code_url 字段

用法:
    python scripts/migration/add_qr_code_field.py
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import sqlite3
from app.config import settings

def migrate():
    """执行数据库迁移"""
    # 获取数据库路径
    db_path = settings.database_url.replace("sqlite:///", "")
    print(f"数据库路径: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(article)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if "qr_code_url" in column_names:
            print("✅ qr_code_url 字段已存在，无需迁移")
            return

        print("📝 添加 qr_code_url 字段...")

        # 添加 qr_code_url 字段
        cursor.execute("""
            ALTER TABLE article
            ADD COLUMN qr_code_url VARCHAR(255)
        """)

        conn.commit()
        print("✅ 迁移成功：qr_code_url 字段已添加")

        # 验证
        cursor.execute("PRAGMA table_info(article)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"当前字段: {', '.join(column_names)}")

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        sys.exit(1)
