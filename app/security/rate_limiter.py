"""
速率限制模块

使用 slowapi 实现 API 调用频率限制
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.config import settings
import logging

# 导出异常供 main.py 使用
__all__ = ["get_limiter", "RateLimitExceeded"]

logger = logging.getLogger(__name__)


def get_identifier(request: Request) -> str:
    """
    获取请求标识符用于速率限制
    优先使用 API Token，否则使用 IP 地址
    """
    # 如果有 API Token，使用 Token 作为标识（每个 Token 独立计数）
    api_token = request.headers.get("X-API-Token")
    if api_token:
        return f"token:{api_token[:8]}"  # 使用 Token 前 8 位

    # 否则使用 IP 地址
    return get_remote_address(request)


def get_limiter():
    """
    获取速率限制器实例
    根据配置决定是否启用
    """
    if not settings.rate_limit_enabled:
        logger.info("速率限制已禁用")
        return None

    limiter = Limiter(
        key_func=get_identifier,
        default_limits=[f"{settings.rate_limit_times}/{settings.rate_limit_seconds}seconds"],
        storage_uri="memory://",  # 使用内存存储（单实例部署）
    )

    logger.info(
        f"速率限制已启用: {settings.rate_limit_times} 次 / "
        f"{settings.rate_limit_seconds} 秒"
    )

    return limiter
