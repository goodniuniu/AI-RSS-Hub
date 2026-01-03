"""
AI 总结服务单元测试

使用 mock 模拟 OpenAI API 响应，避免消耗真实 Token
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from openai import APITimeoutError, APIError

# 导入被测试的模块
from app.services.summarizer import (
    summarize_text_async,
    _do_summarize,
    summarize_text,
    test_llm_connection_async,
    test_llm_connection,
)
from app.config import settings


class TestSummarizeTextAsync:
    """测试异步摘要生成函数"""

    @pytest.mark.asyncio
    async def test_summarize_success_with_mock(self):
        """测试：成功生成摘要（使用 mock）"""
        # Mock 摘要结果
        mock_summary = "这是一篇关于人工智能发展的文章，介绍了最新的技术进展和应用场景。"

        # 创建 mock 响应对象
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_summary

        # Mock AsyncOpenAI 客户端
        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            # 设置 mock 客户端实例
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # 设置 mock API 调用返回值
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            # 执行测试
            test_text = "这是一篇很长的文章内容..." * 100  # 超过 10 字符
            result = await summarize_text_async(test_text)

            # 验证结果
            assert result == mock_summary
            assert len(result) <= settings.summary_max_length

            # 验证 API 被正确调用
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args

            # 检查调用参数
            assert call_args.kwargs["model"] == settings.openai_model
            assert call_args.kwargs["temperature"] == 0.3
            assert call_args.kwargs["max_tokens"] == 200
            assert len(call_args.kwargs["messages"]) == 2
            assert call_args.kwargs["messages"][0]["role"] == "system"
            assert call_args.kwargs["messages"][1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_summarize_without_api_key(self):
        """测试：未配置 API Key"""
        with patch.object(settings, "openai_api_key", None):
            test_text = "这是一篇测试文章" * 10
            result = await summarize_text_async(test_text)

            assert result == "未配置 AI 服务"

    @pytest.mark.asyncio
    async def test_summarize_empty_text(self):
        """测试：空文本"""
        with patch.object(settings, "openai_api_key", "test-key"):
            result = await summarize_text_async("")

            assert result == "内容过短，无需总结"

    @pytest.mark.asyncio
    async def test_summarize_short_text(self):
        """测试：文本过短（小于 10 字符）"""
        with patch.object(settings, "openai_api_key", "test-key"):
            result = await summarize_text_async("短文本")

            assert result == "内容过短，无需总结"

    @pytest.mark.asyncio
    async def test_summarize_whitespace_only(self):
        """测试：只有空白字符"""
        with patch.object(settings, "openai_api_key", "test-key"):
            result = await summarize_text_async("   \n\t  ")

            assert result == "内容过短，无需总结"

    @pytest.mark.asyncio
    async def test_summarize_timeout_error(self):
        """测试：API 调用超时"""
        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # 模拟超时异常
            mock_client.chat.completions.create = AsyncMock(
                side_effect=APITimeoutError("Request timeout")
            )

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await _do_summarize("这是一篇测试文章" * 10)

                assert result == "总结生成超时"

    @pytest.mark.asyncio
    async def test_summarize_api_error(self):
        """测试：API 调用失败"""
        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # 创建 mock request 对象
            mock_request = Mock()
            mock_body = Mock()

            # 模拟 API 错误（需要传入 request、body 参数）
            mock_client.chat.completions.create = AsyncMock(
                side_effect=APIError(
                    message="Invalid API key",
                    request=mock_request,
                    body=mock_body
                )
            )

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await _do_summarize("这是一篇测试文章" * 10)

                assert result == "总结生成失败"

    @pytest.mark.asyncio
    async def test_summarize_unknown_exception(self):
        """测试：未知异常"""
        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # 模拟未知异常
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("Unknown error")
            )

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await _do_summarize("这是一篇测试文章" * 10)

                assert result == "总结生成异常"

    @pytest.mark.asyncio
    async def test_summarize_with_semaphore(self):
        """测试：使用信号量控制并发"""
        mock_summary = "测试摘要"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_summary

        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            # 创建信号量（最大并发数为 2）
            semaphore = asyncio.Semaphore(2)

            with patch.object(settings, "openai_api_key", "test-key"):
                # 并发调用 4 次
                tasks = [
                    summarize_text_async(f"测试文章 {i}" * 10, semaphore)
                    for i in range(4)
                ]

                results = await asyncio.gather(*tasks)

                # 验证所有结果
                assert all(r == mock_summary for r in results)
                assert len(results) == 4

    @pytest.mark.asyncio
    async def test_summarize_truncates_long_summary(self):
        """测试：摘要过长时自动截断"""
        # 创建一个超过限制长度的摘要
        long_summary = "A" * (settings.summary_max_length + 50)

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = long_summary

        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await summarize_text_async("这是一篇测试文章" * 10)

                # 验证被截断
                assert len(result) == settings.summary_max_length + 3  # +3 是 "..."
                assert result.endswith("...")

    @pytest.mark.asyncio
    async def test_summarize_truncates_input_text(self):
        """测试：输入文本过长时截断到 2000 字符"""
        # 创建一个超过 2000 字符的文本
        long_text = "A" * 3000

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "测试摘要"

        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch.object(settings, "openai_api_key", "test-key"):
                await summarize_text_async(long_text)

                # 验证传入 API 的文本被截断到 2000 字符
                call_args = mock_client.chat.completions.create.call_args
                prompt = call_args.kwargs["messages"][1]["content"]

                # 提示词中应该只包含前 2000 字符
                assert long_text[:2000] in prompt
                assert len([c for c in prompt if c == "A"]) == 2000


class TestSummarizeTextSync:
    """测试同步摘要生成函数"""

    def test_summarize_sync_success_with_mock(self):
        """测试：同步版本成功生成摘要"""
        mock_summary = "这是一篇关于测试的文章摘要。"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_summary

        # OpenAI 是在函数内部导入的，所以使用 "openai.OpenAI" 作为路径
        with patch("openai.OpenAI") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = Mock(return_value=mock_response)

            with patch.object(settings, "openai_api_key", "test-key"):
                result = summarize_text("这是一篇测试文章" * 10)

                assert result == mock_summary

    def test_summarize_sync_without_api_key(self):
        """测试：同步版本未配置 API Key"""
        with patch.object(settings, "openai_api_key", None):
            result = summarize_text("这是一篇测试文章" * 10)

            assert result == "未配置 AI 服务"

    def test_summarize_sync_short_text(self):
        """测试：同步版本文本过短"""
        with patch.object(settings, "openai_api_key", "test-key"):
            result = summarize_text("短文本")

            assert result == "内容过短，无需总结"

    def test_summarize_sync_exception_handling(self):
        """测试：同步版本异常处理"""
        with patch("openai.OpenAI") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = Mock(
                side_effect=Exception("Sync error")
            )

            with patch.object(settings, "openai_api_key", "test-key"):
                result = summarize_text("这是一篇测试文章" * 10)

                assert result == "总结生成失败"


class TestLLMConnection:
    """测试 LLM 连接测试函数"""

    @pytest.mark.asyncio
    async def test_test_llm_connection_async_success(self):
        """测试：异步连接测试成功"""
        with patch("app.services.summarizer.summarize_text_async") as mock_summarize:
            mock_summarize.return_value = "测试摘要"

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await test_llm_connection_async()

                assert result is True

    @pytest.mark.asyncio
    async def test_test_llm_connection_async_no_api_key(self):
        """测试：异步连接测试无 API Key"""
        with patch.object(settings, "openai_api_key", None):
            result = await test_llm_connection_async()

            assert result is False

    @pytest.mark.asyncio
    async def test_test_llm_connection_async_failure(self):
        """测试：异步连接测试失败"""
        with patch("app.services.summarizer.summarize_text_async") as mock_summarize:
            mock_summarize.return_value = "总结生成失败"

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await test_llm_connection_async()

                assert result is False

    @pytest.mark.asyncio
    async def test_test_llm_connection_async_exception(self):
        """测试：异步连接测试异常"""
        with patch("app.services.summarizer.summarize_text_async") as mock_summarize:
            mock_summarize.side_effect = Exception("Test error")

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await test_llm_connection_async()

                assert result is False

    def test_test_llm_connection_sync_success(self):
        """测试：同步连接测试成功"""
        with patch("app.services.summarizer.summarize_text") as mock_summarize:
            mock_summarize.return_value = "测试摘要"

            with patch.object(settings, "openai_api_key", "test-key"):
                result = test_llm_connection()

                assert result is True

    def test_test_llm_connection_sync_no_api_key(self):
        """测试：同步连接测试无 API Key"""
        with patch.object(settings, "openai_api_key", None):
            result = test_llm_connection()

            assert result is False

    def test_test_llm_connection_sync_failure(self):
        """测试：同步连接测试失败"""
        with patch("app.services.summarizer.summarize_text") as mock_summarize:
            mock_summarize.return_value = "总结生成失败"

            with patch.object(settings, "openai_api_key", "test-key"):
                result = test_llm_connection()

                assert result is False


class TestSummarizeEdgeCases:
    """测试边界情况"""

    @pytest.mark.asyncio
    async def test_exactly_10_characters(self):
        """测试：刚好 10 个字符"""
        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "摘要"

            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch.object(settings, "openai_api_key", "test-key"):
                # 10 个字符（不含空白）
                result = await summarize_text_async("1234567890")

                assert result == "摘要"

    @pytest.mark.asyncio
    async def test_9_characters(self):
        """测试：少于 10 个字符"""
        with patch.object(settings, "openai_api_key", "test-key"):
            result = await summarize_text_async("123456789")

            assert result == "内容过短，无需总结"

    @pytest.mark.asyncio
    async def test_unicode_text(self):
        """测试：Unicode 文本（中文）"""
        mock_summary = "这是一篇中文文章的摘要"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_summary

        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await summarize_text_async("这是一篇很长的中文文章内容..." * 10)

                assert result == mock_summary

    @pytest.mark.asyncio
    async def test_special_characters(self):
        """测试：特殊字符"""
        mock_summary = "包含特殊字符的摘要"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_summary

        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch.object(settings, "openai_api_key", "test-key"):
                result = await summarize_text_async("包含特殊字符的文章：!@#$%^&*()")

                assert result == mock_summary


class TestConcurrentSummaries:
    """测试并发摘要生成"""

    @pytest.mark.asyncio
    async def test_concurrent_without_semaphore(self):
        """测试：无信号量限制的并发"""
        mock_summary = "并发测试摘要"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_summary

        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            with patch.object(settings, "openai_api_key", "test-key"):
                # 并发调用 10 次，无信号量限制
                tasks = [
                    _do_summarize(f"测试文章 {i}" * 10) for i in range(10)
                ]

                results = await asyncio.gather(*tasks)

                assert all(r == mock_summary for r in results)
                assert len(results) == 10

    @pytest.mark.asyncio
    async def test_concurrent_with_limited_semaphore(self):
        """测试：有限制信号量的并发"""
        mock_summary = "受限并发测试摘要"

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_summary

        with patch("app.services.summarizer.AsyncOpenAI") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            # 限制并发数为 3
            semaphore = asyncio.Semaphore(3)

            with patch.object(settings, "openai_api_key", "test-key"):
                # 并发调用 10 次，最多 3 个同时执行
                tasks = [
                    summarize_text_async(f"测试文章 {i}" * 10, semaphore)
                    for i in range(10)
                ]

                results = await asyncio.gather(*tasks)

                assert all(r == mock_summary for r in results)
                assert len(results) == 10


# 运行测试的主函数
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
