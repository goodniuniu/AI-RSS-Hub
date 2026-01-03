"""
日志安全模块

防止敏感信息泄露到日志
"""
import logging
import re


class SensitiveDataFilter(logging.Filter):
    """
    日志过滤器，移除敏感信息
    """

    # 敏感字段模式
    PATTERNS = [
        (r"(api[_-]?key[\"']?\s*[:=]\s*[\"']?)[^\"'}\s]+", r"\1***REDACTED***"),
        (r"(token[\"']?\s*[:=]\s*[\"']?)[^\"'}\s]+", r"\1***REDACTED***"),
        (r"(password[\"']?\s*[:=]\s*[\"']?)[^\"'}\s]+", r"\1***REDACTED***"),
        (r"(secret[\"']?\s*[:=]\s*[\"']?)[^\"'}\s]+", r"\1***REDACTED***"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录，移除敏感信息
        """
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)

        if hasattr(record, "args") and record.args:
            record.args = tuple(
                self._sanitize(arg) if isinstance(arg, str) else arg
                for arg in record.args
            )

        return True

    def _sanitize(self, text: str) -> str:
        """移除敏感信息"""
        for pattern, replacement in self.PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text


def setup_secure_logging():
    """
    配置安全的日志系统
    """
    # 创建过滤器
    sensitive_filter = SensitiveDataFilter()

    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 为所有处理器添加过滤器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(sensitive_filter)

    # 限制第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    logging.info("安全日志系统已初始化")


def sanitize_for_log(data):
    """
    清理包含敏感信息的数据，用于日志输出
    """
    if isinstance(data, str):
        return SensitiveDataFilter()._sanitize(data)
    elif isinstance(data, dict):
        return {
            k: (
                "***REDACTED***"
                if any(sensitive in k.lower() for sensitive in ["key", "token", "password", "secret"])
                else sanitize_for_log(v)
            )
            for k, v in data.items()
        }
    elif isinstance(data, (list, tuple)):
        return type(data)(sanitize_for_log(item) for item in data)
    else:
        return data
