"""
AI 总结服务
使用 OpenAI 兼容接口进行文本总结
可以轻松替换为 DeepSeek、Gemini 等其他提供商
"""
from openai import AsyncOpenAI, APITimeoutError, APIError
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)


async def summarize_text_async(text: str, semaphore: asyncio.Semaphore = None) -> str:
    """
    对文本进行 AI 总结（异步版本）

    Args:
        text: 原始文本内容
        semaphore: 并发控制信号量（可选）

    Returns:
        总结后的文本（100字以内）
    """
    # 检查 API Key
    if not settings.openai_api_key:
        logger.warning("未配置 OPENAI_API_KEY，跳过 AI 总结")
        return "未配置 AI 服务"

    # 如果文本为空或太短，直接返回
    if not text or len(text.strip()) < 10:
        return "内容过短，无需总结"

    # 使用信号量控制并发
    if semaphore:
        async with semaphore:
            return await _do_summarize(text)
    else:
        return await _do_summarize(text)


async def _do_summarize(text: str) -> str:
    """
    实际执行 AI 总结的内部函数
    """
    try:
        # 初始化异步 OpenAI 客户端
        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
            timeout=settings.llm_timeout,
        )

        # 构建提示词
        prompt = f"""请用中文对以下文章内容进行简短总结，不超过{settings.summary_max_length}字：

{text[:2000]}  # 限制输入长度，避免超出 token 限制

请直接输出总结内容，不要添加其他说明。"""

        # 调用 API
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "你是一个专业的文章摘要助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,  # 较低的温度值，使输出更加确定
            max_tokens=200,  # 限制输出长度
        )

        # 提取总结内容
        summary = response.choices[0].message.content.strip()

        # 确保长度不超过限制
        if len(summary) > settings.summary_max_length:
            summary = summary[: settings.summary_max_length] + "..."

        logger.info(f"AI 总结成功，原文长度: {len(text)}, 总结长度: {len(summary)}")
        return summary

    except APITimeoutError:
        error_msg = f"LLM API 调用超时（超过 {settings.llm_timeout} 秒）"
        logger.error(error_msg)
        return "总结生成超时"

    except APIError as e:
        error_msg = f"LLM API 调用失败: {e}"
        logger.error(error_msg)
        return "总结生成失败"

    except Exception as e:
        error_msg = f"AI 总结发生未知错误: {e}"
        logger.error(error_msg)
        return "总结生成异常"


def summarize_text(text: str) -> str:
    """
    对文本进行 AI 总结（同步版本，用于兼容旧代码）

    Args:
        text: 原始文本内容

    Returns:
        总结后的文本（100字以内）
    """
    # 检查 API Key
    if not settings.openai_api_key:
        logger.warning("未配置 OPENAI_API_KEY，跳过 AI 总结")
        return "未配置 AI 服务"

    # 如果文本为空或太短，直接返回
    if not text or len(text.strip()) < 10:
        return "内容过短，无需总结"

    try:
        # 初始化同步 OpenAI 客户端
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
            timeout=settings.llm_timeout,
        )

        # 构建提示词
        prompt = f"""请用中文对以下文章内容进行简短总结，不超过{settings.summary_max_length}字：

{text[:2000]}  # 限制输入长度，避免超出 token 限制

请直接输出总结内容，不要添加其他说明。"""

        # 调用 API
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "你是一个专业的文章摘要助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=200,
        )

        # 提取总结内容
        summary = response.choices[0].message.content.strip()

        # 确保长度不超过限制
        if len(summary) > settings.summary_max_length:
            summary = summary[: settings.summary_max_length] + "..."

        logger.info(f"AI 总结成功，原文长度: {len(text)}, 总结长度: {len(summary)}")
        return summary

    except Exception as e:
        error_msg = f"AI 总结失败: {e}"
        logger.error(error_msg)
        return "总结生成失败"


async def test_llm_connection_async() -> bool:
    """
    测试 LLM API 连接是否正常（异步版本）

    Returns:
        bool: 连接正常返回 True，否则返回 False
    """
    if not settings.openai_api_key:
        logger.warning("未配置 OPENAI_API_KEY")
        return False

    try:
        summary = await summarize_text_async("这是一个测试文本，用于验证 LLM API 是否正常工作。")
        return bool(summary) and "失败" not in summary and "异常" not in summary
    except Exception as e:
        logger.error(f"LLM 连接测试失败: {e}")
        return False


def test_llm_connection() -> bool:
    """
    测试 LLM API 连接是否正常（同步版本）

    Returns:
        bool: 连接正常返回 True，否则返回 False
    """
    if not settings.openai_api_key:
        logger.warning("未配置 OPENAI_API_KEY")
        return False

    try:
        summary = summarize_text("这是一个测试文本，用于验证 LLM API 是否正常工作。")
        return bool(summary) and "失败" not in summary and "异常" not in summary
    except Exception as e:
        logger.error(f"LLM 连接测试失败: {e}")
        return False
