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
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

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
        # 初始化异步 OpenAI 客户端（上下文管理器确保连接正确释放）
        async with AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
            timeout=settings.llm_timeout,
        ) as client:
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


# ==================== 语言检测功能 ====================

def detect_content_language(content: str) -> str:
    """
    检测内容的主要语言

    Args:
        content: 文章内容

    Returns:
        'zh': 中文为主 (>50% 中文字符)
        'en': 英文为主
        'mixed': 混合内容（中英文都超过30%）
    """
    if not content:
        return 'zh'

    # 统计中文字符数
    chinese_chars = sum(1 for char in content if '一' <= char <= '鿿')
    # 统计英文字母数
    english_chars = sum(1 for char in content if char.isalpha() and char.isascii())

    total_chars = len(content)
    if total_chars == 0:
        return 'zh'

    chinese_ratio = chinese_chars / total_chars
    english_ratio = english_chars / total_chars

    # 如果中英文都超过30%，视为混合内容
    if chinese_ratio > 0.3 and english_ratio > 0.3:
        return 'mixed'
    # 中文超过50%视为中文内容
    elif chinese_ratio > 0.5:
        return 'zh'
    # 否则视为英文内容
    else:
        return 'en'


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


@retry(
    stop=stop_after_attempt(settings.summary_retry_attempts),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((APIError, APITimeoutError)),
    before_sleep=before_sleep_log(logger, logging.INFO),
)
async def _do_summarize_bilingual(title: str, content: str) -> tuple[str, str]:
    """
    实际执行双语摘要生成的内部函数（带重试机制）
    """
    try:
        # 初始化异步 OpenAI 客户端（上下文管理器确保连接正确释放）
        async with AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
            timeout=settings.llm_timeout,
        ) as client:
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
        # 降级：使用原文内容作为摘要
        return _generate_fallback_summary(content), ""

    except APIError as e:
        error_msg = f"双语摘要 API 调用失败: {e}"
        logger.error(error_msg)
        # 降级：使用原文内容作为摘要
        return _generate_fallback_summary(content), ""

    except Exception as e:
        error_msg = f"双语摘要生成发生未知错误: {e}"
        logger.error(error_msg)
        # 降级：使用原文内容作为摘要
        return _generate_fallback_summary(content), ""


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


async def summarize_article_auto(
    title: str,
    content: str,
    semaphore: asyncio.Semaphore = None
) -> tuple[str, str]:
    """
    自动检测语言并生成摘要
    - 纯中文内容：只生成中文摘要
    - 纯英文内容：只生成英文摘要
    - 混合内容：生成双语摘要

    Args:
        title: 文章标题
        content: 文章内容
        semaphore: 并发控制信号量（可选）

    Returns:
        (zh_summary, en_summary): 中文摘要和英文摘要（其中一个可能为空）
    """
    # 检测内容语言
    language = detect_content_language(content)

    logger.info(f"内容语言检测结果: {language}, 标题: {title[:50]}...")

    if language == 'zh':
        # 纯中文内容：只生成中文摘要
        zh_summary = await _summarize_chinese_only(title, content, semaphore)
        return zh_summary, ""
    elif language == 'en':
        # 纯英文内容：只生成英文摘要
        en_summary = await _summarize_english_only(title, content, semaphore)
        return "", en_summary
    else:
        # 混合内容：使用双语摘要
        return await summarize_article_bilingual(title, content, semaphore)


@retry(
    stop=stop_after_attempt(settings.summary_retry_attempts),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((APIError, APITimeoutError)),
    before_sleep=before_sleep_log(logger, logging.INFO),
)
async def _summarize_chinese_only(
    title: str,
    content: str,
    semaphore: asyncio.Semaphore = None
) -> str:
    """
    只生成中文摘要（用于纯中文内容）
    """
    try:
        # 使用信号量控制并发
        if semaphore:
            async with semaphore:
                return await _do_summarize_chinese(title, content)
        else:
            return await _do_summarize_chinese(title, content)
    except Exception as e:
        logger.error(f"中文摘要生成失败: {e}")
        return _generate_fallback_summary(content)


async def _do_summarize_chinese(title: str, content: str) -> str:
    """
    实际执行中文摘要生成
    """
    async with AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        timeout=settings.llm_timeout,
    ) as client:
        prompt = f"""请用中文对以下文章进行简短总结，不超过{settings.summary_max_length}字。

标题：{title}
内容：{content[:3000]}

要求：
1. 直接输出总结内容，不要有任何前缀或说明
2. 保持简洁，抓住要点
3. 只输出中文"""

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "你是一个专业的中文文章摘要助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=200,
        )

        summary = response.choices[0].message.content.strip()

        # 截断过长的摘要
        if len(summary) > settings.summary_max_length:
            summary = summary[:settings.summary_max_length] + "..."

        logger.info(f"中文摘要生成成功，长度: {len(summary)}字")
        return summary


@retry(
    stop=stop_after_attempt(settings.summary_retry_attempts),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((APIError, APITimeoutError)),
    before_sleep=before_sleep_log(logger, logging.INFO),
)
async def _summarize_english_only(
    title: str,
    content: str,
    semaphore: asyncio.Semaphore = None
) -> str:
    """
    只生成英文摘要（用于纯英文内容）
    """
    try:
        # 使用信号量控制并发
        if semaphore:
            async with semaphore:
                return await _do_summarize_english(title, content)
        else:
            return await _do_summarize_english(title, content)
    except Exception as e:
        logger.error(f"英文摘要生成失败: {e}")
        return ""


async def _do_summarize_english(title: str, content: str) -> str:
    """
    实际执行英文摘要生成
    """
    async with AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        timeout=settings.llm_timeout,
    ) as client:
        prompt = f"""Please summarize the following article in English, no more than {settings.summary_max_length * 2} words.

Title: {title}
Content: {content[:3000]}

Requirements:
1. Output ONLY the summary, no prefixes or explanations
2. Keep it concise and capture key points
3. Output in English only"""

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a professional article summarizer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=300,
        )

        summary = response.choices[0].message.content.strip()

        # 截断过长的摘要
        if len(summary) > settings.summary_max_length * 2:
            summary = summary[:settings.summary_max_length * 2] + "..."

        logger.info(f"英文摘要生成成功，长度: {len(summary)}字符")
        return summary


def _generate_fallback_summary(content: str) -> str:
    """
    生成降级摘要（使用原文开头）
    """
    if not content:
        return ""
    # 清理 HTML 标签
    import re
    clean_content = re.sub(r'<[^>]+>', '', content)
    clean_content = clean_content.strip()

    if len(clean_content) > settings.summary_max_length:
        clean_content = clean_content[:settings.summary_max_length] + "..."
    return clean_content


async def summarize_text_async(text: str, semaphore: asyncio.Semaphore = None) -> str:
    """
    对文本进行 AI 总结（异步版本）

    Args:
        text: 原始文本内容
        semaphore: 并发控制信号量（可选）

    Returns:
        总结后的文本（100字以内）
    """
    zh_summary, _ = await summarize_article_auto("Article", text, semaphore)
    return zh_summary or "摘要生成失败"
