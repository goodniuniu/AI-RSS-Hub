"""
输入验证模块

增强 URL、字符串长度的验证，防止 XSS、SSRF 等攻击
"""
import html
import re
from typing import Optional
from fastapi import HTTPException, status
from pydantic import field_validator, BaseModel
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class URLValidator:
    """URL 验证器"""

    # 基本的 URL 正则表达式
    URL_PATTERN = re.compile(
        r"^https?://"  # http:// 或 https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # 域名
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP 地址
        r"(?::\d+)?"  # 端口
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    @classmethod
    def validate_url(cls, url: str, field_name: str = "URL") -> str:
        """
        验证 URL 格式和长度

        Args:
            url: 待验证的 URL
            field_name: 字段名称（用于错误消息）

        Returns:
            验证通过的 URL

        Raises:
            HTTPException: URL 无效
        """
        # 检查长度
        if len(url) > settings.max_url_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} 长度超过限制（最大 {settings.max_url_length} 字符）",
            )

        # 检查格式
        if not cls.URL_PATTERN.match(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} 格式无效，必须是合法的 HTTP/HTTPS URL",
            )

        # 防止 SSRF 攻击：拒绝内网地址
        if cls._is_private_url(url):
            logger.warning(f"检测到内网 URL 尝试: {url}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} 不能指向内网地址",
            )

        return url

    @classmethod
    def _is_private_url(cls, url: str) -> bool:
        """
        检查 URL 是否指向内网地址
        防止 SSRF 攻击
        """
        private_patterns = [
            "127.0.0.1",
            "localhost",
            "0.0.0.0",
            "192.168.",
            "10.",
            "172.16.",
            "169.254.",  # link-local
        ]

        url_lower = url.lower()
        return any(pattern in url_lower for pattern in private_patterns)


class FeedCreateValidated(BaseModel):
    """
    增强的 Feed 创建模型，带验证
    """
    name: str
    url: str
    category: str = "tech"
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证名称字段"""
        if not v or not v.strip():
            raise ValueError("名称不能为空")

        if len(v) > settings.max_name_length:
            raise ValueError(f"名称长度超过限制（最大 {settings.max_name_length} 字符）")

        # 防止 XSS：移除潜在的 HTML 标签
        v = html.escape(v.strip())

        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """验证分类字段"""
        if not v or not v.strip():
            raise ValueError("分类不能为空")

        if len(v) > settings.max_category_length:
            raise ValueError(f"分类长度超过限制（最大 {settings.max_category_length} 字符）")

        return v.strip()

    @field_validator("url")
    @classmethod
    def validate_url_field(cls, v: str) -> str:
        """验证 URL 字段"""
        return URLValidator.validate_url(v, "RSS 源 URL")
