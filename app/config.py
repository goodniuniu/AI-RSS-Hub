"""
配置管理模块
从环境变量读取配置信息
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 数据库配置
    database_url: str = "sqlite:///./ai_rss_hub.db"

    # LLM API 配置
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"  # 可替换为 DeepSeek 或其他兼容接口
    openai_model: str = "gpt-3.5-turbo"

    # RSS 抓取配置
    fetch_interval_hours: int = 1  # 抓取间隔（小时）
    request_timeout: int = 30  # HTTP 请求超时时间（秒）

    # AI 总结配置
    summary_max_length: int = 100  # 总结最大长度
    llm_timeout: int = 30  # LLM API 超时时间（秒）
    max_concurrent_summaries: int = 2  # 并发生成摘要的最大数量（降低以避免速率限制）

    # ========== 安全配置 ==========
    # API Token - 用于管理操作认证
    api_token: Optional[str] = None

    # CORS 配置 - 允许的跨域源（逗号分隔）
    cors_origins: str = ""

    # 速率限制配置
    rate_limit_enabled: bool = True  # 是否启用速率限制
    rate_limit_times: int = 60  # 时间窗口内的最大请求数
    rate_limit_seconds: int = 60  # 时间窗口（秒）

    # 输入验证配置
    max_url_length: int = 2048  # URL 最大长度
    max_name_length: int = 200  # 名称最大长度
    max_category_length: int = 50  # 分类最大长度

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
