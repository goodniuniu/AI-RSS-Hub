"""
API Token 认证模块

使用简单的 Token 验证保护管理接口
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# API Key Header 验证
api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)


async def verify_api_token(token: str = Security(api_key_header)) -> bool:
    """
    验证 API Token

    Args:
        token: 从请求头 X-API-Token 中获取的 Token

    Returns:
        验证成功返回 True

    Raises:
        HTTPException: Token 无效或缺失
    """
    # 如果没有配置 API Token，跳过验证（开发模式）
    if not settings.api_token:
        logger.warning("API Token 未配置，认证已跳过（不推荐用于生产环境）")
        return True

    if not token:
        logger.warning("API Token 缺失")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Token 缺失，请在请求头中提供 X-API-Token",
        )

    if token != settings.api_token:
        logger.warning(f"API Token 验证失败: {token[:8] if len(token) > 8 else token}...")  # 只记录前 8 位
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Token 无效",
        )

    logger.debug("API Token 验证成功")
    return True


async def optional_api_token(token: str = Security(api_key_header)) -> bool:
    """
    可选的 API Token 验证（用于未来扩展）
    如果提供了 Token 则验证，否则跳过
    """
    if not token or not settings.api_token:
        return True

    if token != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Token 无效",
        )

    return True
