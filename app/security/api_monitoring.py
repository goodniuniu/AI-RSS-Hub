"""
API 监控中间件

记录所有 API 请求的统计信息，包括：
- 请求路径和方法
- 响应状态码
- 处理时间
- 客户端信息
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class APIMonitoringMiddleware(BaseHTTPMiddleware):
    """
    API 监控中间件

    功能：
    1. 记录所有 API 请求的基本信息
    2. 计算响应时间
    3. 添加请求追踪 ID
    4. 记录慢请求
    """

    # 慢请求阈值（毫秒）
    SLOW_REQUEST_THRESHOLD = 1000

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        import uuid
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # 记录开始时间
        start_time = time.time()

        # 获取请求信息
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")[:100]

        # 处理请求
        status_code = 200
        error = None

        try:
            response = await call_next(request)
            status_code = response.status_code

            # 添加自定义响应头
            response.headers["X-Request-ID"] = request_id

            # 计算处理时间
            process_time = (time.time() - start_time) * 1000
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

            return response

        except Exception as e:
            status_code = 500
            error = str(e)
            logger.error(
                f"Request error: {method} {path}",
                extra={
                    "request_id": request_id,
                    "error": error,
                    "client_ip": client_ip
                }
            )
            raise

        finally:
            # 计算处理时间
            process_time = (time.time() - start_time) * 1000

            # 记录请求日志
            self._log_request(
                request_id=request_id,
                method=method,
                path=path,
                status_code=status_code,
                process_time=process_time,
                client_ip=client_ip,
                user_agent=user_agent,
                error=error
            )

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端 IP 地址"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _log_request(self, request_id, method, path, status_code,
                    process_time, client_ip, user_agent, error):
        """记录请求日志"""
        # 判断是否为慢请求
        is_slow = process_time > self.SLOW_REQUEST_THRESHOLD

        # 构建日志数据
        log_data = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "status": status_code,
            "time_ms": round(process_time, 2),
            "ip": client_ip,
            "slow": "YES" if is_slow else "NO"
        }

        # 根据状态码选择日志级别
        if status_code >= 500:
            logger.error(f"API Request: {log_data}", extra={"error": error})
        elif status_code >= 400:
            logger.warning(f"API Request: {log_data}")
        elif is_slow:
            logger.warning(f"Slow Request: {log_data}")
        else:
            logger.info(f"API Request: {log_data}")

        # 异步写入数据库（避免阻塞请求）
        self._save_to_database(request_id, method, path, status_code,
                              process_time, client_ip, user_agent, error)

    def _save_to_database(self, request_id, method, path, status_code,
                         process_time, client_ip, user_agent, error):
        """保存请求日志到数据库"""
        import sqlite3
        import threading
        from app.config import settings

        def db_write():
            try:
                db_path = settings.database_url.replace("sqlite:///", "")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO api_request_log
                    (request_id, method, path, status_code, response_time_ms,
                     client_ip, user_agent, error_msg)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request_id,
                    method,
                    path,
                    status_code,
                    round(process_time, 2),
                    client_ip,
                    user_agent,
                    error
                ))

                conn.commit()
                conn.close()
            except Exception as e:
                # 数据库写入失败不应影响请求处理
                logger.debug(f"Failed to save request log to database: {e}")

        # 在后台线程中执行数据库写入
        thread = threading.Thread(target=db_write)
        thread.start()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    请求 ID 中间件

    为每个请求生成唯一的追踪 ID
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import uuid

        # 生成请求 ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # 处理请求
        response = await call_next(request)

        # 添加响应头
        response.headers["X-Request-ID"] = request_id

        return response
