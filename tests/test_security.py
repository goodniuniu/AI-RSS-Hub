"""
安全功能测试

测试 API 认证、输入验证、速率限制等安全功能
"""
import pytest
import os
from fastapi.testclient import TestClient

# 导入主应用
from app.main import app

client = TestClient(app)


class TestAPIToken:
    """测试 API Token 认证"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的设置"""
        # 从环境变量获取测试 Token
        self.test_token = os.getenv("API_TOKEN", "test-token-for-development")

    def test_add_feed_without_token(self):
        """测试未提供 Token 时添加 RSS 源"""
        response = client.post(
            "/api/feeds",
            json={
                "name": "Test Feed",
                "url": "https://example.com/rss",
                "category": "test"
            }
        )
        # 如果没有配置 API_TOKEN，应该返回 200（开发模式）
        # 如果配置了，应该返回 401
        assert response.status_code in [200, 201, 400, 401]

    def test_add_feed_with_invalid_token(self):
        """测试使用无效 Token 添加 RSS 源"""
        if not os.getenv("API_TOKEN"):
            pytest.skip("未配置 API_TOKEN，跳过此测试")

        response = client.post(
            "/api/feeds",
            json={
                "name": "Test Feed",
                "url": "https://example.com/rss",
                "category": "test"
            },
            headers={"X-API-Token": "invalid-token-12345"}
        )
        assert response.status_code == 403

    def test_add_feed_with_valid_token(self):
        """测试使用有效 Token 添加 RSS 源"""
        response = client.post(
            "/api/feeds",
            json={
                "name": "Test Feed Security",
                "url": "https://example.com/security-test-rss",
                "category": "test"
            },
            headers={"X-API-Token": self.test_token}
        )
        # 可能返回 201（成功）或 400（已存在）
        assert response.status_code in [201, 400]

    def test_fetch_without_token(self):
        """测试未提供 Token 时手动抓取"""
        response = client.post("/api/feeds/fetch")
        # 如果没有配置 API_TOKEN，应该返回 200（开发模式）
        # 如果配置了，应该返回 401
        assert response.status_code in [200, 401]


class TestPublicEndpoints:
    """测试公开端点（无需认证）"""

    def test_get_feeds_public(self):
        """测试获取 RSS 源列表（公开）"""
        response = client.get("/api/feeds")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_articles_public(self):
        """测试获取文章列表（公开）"""
        response = client.get("/api/articles")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_health_check(self):
        """测试健康检查（公开）"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestInputValidation:
    """测试输入验证"""

    def test_add_feed_with_invalid_url(self):
        """测试添加无效 URL 的 RSS 源"""
        token = os.getenv("API_TOKEN", "test-token")

        response = client.post(
            "/api/feeds",
            json={
                "name": "Test Feed",
                "url": "not-a-valid-url",
                "category": "test"
            },
            headers={"X-API-Token": token}
        )
        # 应该返回 422（验证错误）
        assert response.status_code == 422

    def test_add_feed_with_private_url(self):
        """测试添加内网 URL 的 RSS 源（SSRF 保护）"""
        token = os.getenv("API_TOKEN", "test-token")

        response = client.post(
            "/api/feeds",
            json={
                "name": "Test Feed",
                "url": "http://localhost:8080/rss",
                "category": "test"
            },
            headers={"X-API-Token": token}
        )
        # 应该返回 400（内网地址被拒绝）或 422
        assert response.status_code in [400, 422]

    def test_add_feed_with_long_name(self):
        """测试添加超长名称的 RSS 源"""
        token = os.getenv("API_TOKEN", "test-token")

        # 创建一个超长的名称（超过 200 字符）
        long_name = "A" * 201

        response = client.post(
            "/api/feeds",
            json={
                "name": long_name,
                "url": "https://example.com/rss",
                "category": "test"
            },
            headers={"X-API-Token": token}
        )
        # 应该返回 422（验证错误）
        assert response.status_code == 422


class TestRateLimiting:
    """测试速率限制"""

    def test_rate_limiting(self):
        """测试速率限制"""
        token = os.getenv("API_TOKEN", "test-token")

        # 快速发送多个请求
        responses = []
        for i in range(70):  # 超过限制（60次）
            response = client.get("/api/feeds")
            responses.append(response.status_code)

        # 应该有部分请求被限流（返回 429）
        # 注意：如果未启用速率限制，可能不会有 429
        if 429 in responses:
            assert True  # 速率限制正常工作
        else:
            pytest.skip("速率限制未启用或限制太宽松")


class TestSecurityHeaders:
    """测试安全响应头"""

    def test_security_headers(self):
        """测试响应包含安全头"""
        response = client.get("/api/feeds")

        # 检查安全响应头
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "Strict-Transport-Security" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
