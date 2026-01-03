"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session
from app.database import create_db_and_tables, init_default_feeds, engine
from app.api.routes import router
from app.scheduler import start_scheduler, stop_scheduler, get_scheduler_status
from app.config import settings
from app.security.logger import setup_secure_logging
from app.security.middleware import SecurityHeadersMiddleware
from app.security.rate_limiter import get_limiter, RateLimitExceeded
from fastapi import HTTPException
import logging

# 配置安全日志
setup_secure_logging()
logger = logging.getLogger(__name__)


def get_cors_origins():
    """
    从环境变量获取 CORS 允许的域名
    返回列表格式
    """
    cors_origins_str = settings.cors_origins.strip()

    # 如果未配置，默认允许本地开发
    if not cors_origins_str:
        logger.warning("CORS_ORIGINS 未配置，使用默认值: http://localhost:3000")
        return ["http://localhost:3000", "http://localhost:8000"]

    # 解析逗号分隔的域名列表
    origins = [origin.strip() for origin in cors_origins_str.split(",")]
    logger.info(f"CORS 允许的域名: {origins}")

    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库和调度器，关闭时清理资源
    """
    # 启动时执行
    logger.info("应用启动中...")

    # 创建数据库表
    create_db_and_tables()

    # 初始化默认 RSS 源
    with Session(engine) as session:
        init_default_feeds(session)

    # 启动定时任务调度器
    start_scheduler()

    logger.info("应用启动完成")

    yield

    # 关闭时执行
    logger.info("应用关闭中...")
    stop_scheduler()
    logger.info("应用已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI-RSS-Hub",
    description="基于 FastAPI 和 SQLModel 的 AI RSS 聚合系统",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS（从环境变量读取允许的域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 添加安全响应头中间件
app.add_middleware(SecurityHeadersMiddleware)

# 配置速率限制
limiter = get_limiter()
if limiter:
    app.state.limiter = limiter

    # 速率限制异常处理器
    async def rate_limit_exceeded_handler(request, exc):
        return HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试",
        )

    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# 注册路由
app.include_router(router, prefix="/api", tags=["RSS"])


@app.get("/")
def root():
    """根路径"""
    return {
        "name": "AI-RSS-Hub",
        "version": "1.0.0",
        "description": "AI RSS 聚合系统",
        "docs": "/docs",
    }


@app.get("/api/status")
def get_status():
    """
    获取系统状态
    """
    scheduler_status = get_scheduler_status()

    return {
        "status": "running",
        "scheduler": scheduler_status,
        "database": settings.database_url,
        "fetch_interval_hours": settings.fetch_interval_hours,
        "llm_configured": bool(settings.openai_api_key),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下启用热重载
    )
