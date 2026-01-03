"""
数据库连接和初始化模块
"""
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy import event
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建数据库引擎
# connect_args={"check_same_thread": False} 仅用于 SQLite
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False,  # 设置为 True 可以看到 SQL 语句
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    为 SQLite 连接设置 PRAGMA 选项
    开启 WAL 模式以提高并发性能
    """
    if "sqlite" in settings.database_url:
        cursor = dbapi_conn.cursor()

        # 开启 WAL 模式
        # WAL 模式允许读写并发，显著提高性能
        cursor.execute("PRAGMA journal_mode=WAL")

        # 设置同步模式为 NORMAL
        # WAL 模式下 NORMAL 更安全，牺牲少量性能换取数据安全
        cursor.execute("PRAGMA synchronous=NORMAL")

        # 设置 WAL 文件自动检查点
        # 当 WAL 文件达到 1000 页时自动执行检查点
        cursor.execute("PRAGMA wal_autocheckpoint=1000")

        # 启用内存映射 I/O（可选，进一步提速）
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB

        # 设置缓存大小（可选）
        # 增加缓存可以提高读取性能
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB

        cursor.close()

        logger.info("SQLite WAL 模式已启用，性能优化配置已应用")


def create_db_and_tables():
    """
    创建数据库表
    在应用启动时调用
    """
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise


def get_session():
    """
    获取数据库会话
    用于依赖注入
    """
    with Session(engine) as session:
        yield session


def init_default_feeds(session: Session):
    """
    初始化默认的 RSS 源
    如果数据库中没有 Feed 数据，则插入 3 个著名的科技类 RSS 源
    """
    from app.models import Feed
    from sqlmodel import select

    # 检查是否已有数据
    statement = select(Feed)
    results = session.exec(statement).first()

    if results is None:
        logger.info("数据库为空，插入默认 RSS 源...")

        default_feeds = [
            Feed(
                name="Hacker News",
                url="https://hnrss.org/frontpage",
                category="tech",
                is_active=True,
            ),
            Feed(
                name="TechCrunch",
                url="https://techcrunch.com/feed/",
                category="tech",
                is_active=True,
            ),
            Feed(
                name="Ars Technica",
                url="https://feeds.arstechnica.com/arstechnica/index",
                category="tech",
                is_active=True,
            ),
        ]

        for feed in default_feeds:
            session.add(feed)

        try:
            session.commit()
            logger.info(f"成功插入 {len(default_feeds)} 个默认 RSS 源")
        except Exception as e:
            session.rollback()
            logger.error(f"插入默认 RSS 源失败: {e}")
    else:
        logger.info("数据库已有数据，跳过默认 RSS 源初始化")
