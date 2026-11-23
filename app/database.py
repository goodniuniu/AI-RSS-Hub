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
        # 调大到 5000 页（约 20MB）：降低自动 checkpoint 频率，把集中刷盘
        # 留给抓取任务结束后的 checkpoint_wal() 主动执行，避免随机时刻
        # 触发密集 IO 击穿 ESSD Entry 限额（106 MB/s / 2120 IOPS）
        cursor.execute("PRAGMA wal_autocheckpoint=5000")

        # 启用内存映射 I/O
        # 2GiB 内存实例：256MB mmap 会加剧内存压力触发 swap 换页 IO，
        # 控制在 64MB，与 cache_size 合计驻留上限约 128MB
        cursor.execute("PRAGMA mmap_size=67108864")  # 64MB

        # 设置缓存大小（可选）
        # 增加缓存可以提高读取性能
        cursor.execute("PRAGMA cache_size=-65536")  # 64MB

        cursor.close()

        logger.info("SQLite WAL 模式已启用，性能优化配置已应用")


def checkpoint_wal():
    """
    主动执行 WAL checkpoint（PASSIVE 模式）。

    PASSIVE 不阻塞并发读写：把 WAL 中已提交的内容尽量合并回主库，
    但若存在活跃读者则跳过部分页，失败/busy 也只是少合并一些页，
    不影响业务。在批量写入（抓取任务）结束后调用，把落盘时机
    控制在我们选择的时间点，避免运行期随机触发阻塞式自动 checkpoint。
    """
    try:
        with engine.connect() as conn:
            result = conn.exec_driver_sql("PRAGMA wal_checkpoint(PASSIVE)")
            row = result.mappings().first()
            # 返回 (busy, log_pages, checkpointed_pages)
            logger.debug(f"WAL checkpoint 完成: {dict(row) if row else 'no rows'}")
    except Exception as e:
        logger.warning(f"WAL checkpoint 执行失败（不影响业务）: {e}")


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
