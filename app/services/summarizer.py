"""
AI 总结服务
使用 OpenAI 兼容接口进行文本总结
可以轻松替换为 DeepSeek、Gemini 等其他提供商
"""
from openai import AsyncOpenAI, APITimeoutError, APIError
from app.config import settings
import logging
import asyncio
import re

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


# ==================== 双语摘要功能 ====================

async def summarize_article_bilingual(
    title: str,
    content: str,
    semaphore: asyncio.Semaphore = None
) -> tuple[str, str]:
    """
    生成中英文双语摘要

    Args:
        title: 文章标题
        content: 文章内容
        semaphore: 并发控制信号量（可选）

    Returns:
        (zh_summary, en_summary): 中文摘要和英文摘要
    """
    # 检查 API Key
    if not settings.openai_api_key:
        logger.warning("未配置 OPENAI_API_KEY，跳过双语总结")
        return "未配置 AI 服务", ""

    # 如果内容为空或太短，直接返回
    if not content or len(content.strip()) < 10:
        return "内容过短，无需总结", ""

    # 使用信号量控制并发
    if semaphore:
        async with semaphore:
            return await _do_summarize_bilingual(title, content)
    else:
        return await _do_summarize_bilingual(title, content)


async def _do_summarize_bilingual(title: str, content: str) -> tuple[str, str]:
    """
    实际执行双语摘要生成的内部函数
    """
    try:
        # 初始化异步 OpenAI 客户端
        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
            timeout=settings.llm_timeout,
        )

        # 构建双语摘要提示词
        prompt = f"""Please summarize the following article in BOTH Chinese and English.

Title: {title}
Content: {content[:3000]}

Requirements:
1. Chinese summary (中文摘要): No more than {settings.summary_max_length} Chinese characters
2. English summary (英文摘要): No more than {settings.summary_max_length * 2} English words
3. Keep key information and main points
4. Make both summaries concise and informative

Please respond in the following format:
Chinese: [你的中文摘要]
English: [Your English Summary]

Important: Only provide the summaries, no other text."""

        # 调用 API
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional bilingual summarizer (Chinese and English)."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=0.3,
            max_tokens=500,  # 增加输出token限制以容纳双语摘要
        )

        # 提取响应内容
        result = response.choices[0].message.content.strip()

        # 解析中英文摘要
        zh_summary = extract_chinese_summary(result)
        en_summary = extract_english_summary(result)

        # 截断过长的摘要
        if len(zh_summary) > settings.summary_max_length:
            zh_summary = zh_summary[:settings.summary_max_length] + "..."
        if len(en_summary) > settings.summary_max_length * 2:
            en_summary = en_summary[:settings.summary_max_length * 2] + "..."

        logger.info(f"双语摘要生成成功 - 中文: {len(zh_summary)}字, 英文: {len(en_summary)}词")
        return zh_summary, en_summary

    except APITimeoutError:
        error_msg = f"双语摘要生成超时（超过 {settings.llm_timeout} 秒）"
        logger.error(error_msg)
        # 降级：生成中文摘要
        try:
            zh_summary = await _do_summarize(content)
            return zh_summary, ""
        except:
            return "双语摘要生成超时", ""

    except APIError as e:
        error_msg = f"双语摘要 API 调用失败: {e}"
        logger.error(error_msg)
        # 降级：生成中文摘要
        try:
            zh_summary = await _do_summarize(content)
            return zh_summary, ""
        except:
            return "双语摘要生成失败", ""

    except Exception as e:
        error_msg = f"双语摘要生成发生未知错误: {e}"
        logger.error(error_msg)
        # 降级：生成中文摘要
        try:
            zh_summary = await _do_summarize(content)
            return zh_summary, ""
        except:
            return "双语摘要生成异常", ""


def extract_chinese_summary(text: str) -> str:
    """
    从 LLM 响应中提取中文摘要

    Args:
        text: LLM 响应文本

    Returns:
        中文摘要内容
    """
    # 尝试多种匹配模式
    patterns = [
        r'Chinese:\s*(.*?)(?=\nEnglish:|$)',  # "Chinese: ... \nEnglish:"
        r'Chinese:\s*(.*?)(?=\n\n|$)',        # "Chinese: ... \n\n"
        r'中文摘要[：:]\s*(.*?)(?=\n英文|$)',  # "中文摘要：... \n英文"
        r'中文[：:]\s*(.*?)(?=\n\n|英文|$)',  # "中文：... \n\n英文"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            summary = match.group(1).strip()
            # 清理可能的引号
            summary = summary.strip('"\'')
            if summary and len(summary) > 5:
                logger.debug(f"成功提取中文摘要 (模式: {pattern})")
                return summary

    # 如果没有匹配到，尝试提取前200个字符
    logger.warning("无法通过正则提取中文摘要，使用备用方案")
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('English', '英文', 'Summary')) and len(line) > 10:
            # 检查是否包含中文字符
            if any('\u4e00' <= char <= '\u9fff' for char in line):
                return line.strip('"\'')

    return ""


def extract_english_summary(text: str) -> str:
    """
    从 LLM 响应中提取英文摘要

    Args:
        text: LLM 响应文本

    Returns:
        英文摘要内容
    """
    # 尝试多种匹配模式
    patterns = [
        r'English:\s*(.*?)(?=$)',  # "English: ..." (到结尾)
        r'English:\s*(.*?)(?=\n\n|$)',  # "English: ... \n\n"
        r'英文摘要[：:]\s*(.*?)(?=$)',  # "英文摘要：..."
        r'英文[：:]\s*(.*?)(?=\n\n|$)',  # "英文：... \n\n"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            summary = match.group(1).strip()
            # 清理可能的引号
            summary = summary.strip('"\'')
            if summary and len(summary) > 5:
                logger.debug(f"成功提取英文摘要 (模式: {pattern})")
                return summary

    # 如果没有匹配到，尝试提取英文行
    logger.warning("无法通过正则提取英文摘要，使用备用方案")
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('Chinese', '中文')) and len(line) > 10:
            # 检查是否主要是英文字符
            if sum(1 for char in line if char.isalpha() and char.isascii()) > len(line) * 0.7:
                return line.strip('"\'')

    return ""


async def summarize_text_async(text: str, semaphore: asyncio.Semaphore = None) -> str:
    """
    对文本进行 AI 总结（异步版本）

    Args:
        text: 原始文本内容
        semaphore: 并发控制信号量（可选）

    Returns:
        总结后的文本（100字以内）
    """
    zh_summary, _ = await summarize_article_bilingual("Article", text, semaphore)
    return zh_summary
