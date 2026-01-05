#!/usr/bin/env python3
"""
测试双语摘要生成功能

这个脚本会测试双语摘要生成是否正常工作
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.summarizer import summarize_article_bilingual, test_llm_connection_async
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def test_bilingual_summary():
    """测试双语摘要生成"""
    logger.info("=" * 60)
    logger.info("  双语摘要生成测试")
    logger.info("=" * 60)
    logger.info("")

    # 测试文章
    title = "AI Breakthrough in Language Models"
    content = """
    Researchers have made a significant breakthrough in the field of large language models.
    The new model, called "GPT-Next", has demonstrated unprecedented capabilities in understanding
    and generating human-like text across multiple languages. According to the research team,
    this advancement could revolutionize how we interact with AI systems in daily life,
    from education to healthcare. The model shows improved reasoning abilities and can
    maintain context over longer conversations. Early tests indicate a 40% improvement in
    accuracy compared to previous models.
    """

    logger.info("测试文章:")
    logger.info(f"标题: {title}")
    logger.info(f"内容: {content[:100]}...")
    logger.info("")

    # 测试LLM连接
    logger.info("⏳ 步骤1: 测试 LLM API 连接...")
    if await test_llm_connection_async():
        logger.info("✅ LLM API 连接正常")
    else:
        logger.error("❌ LLM API 连接失败，请检查配置")
        return

    logger.info("")

    # 生成双语摘要
    logger.info("⏳ 步骤2: 生成双语摘要...")
    logger.info("(这可能需要10-20秒，请耐心等待...)")
    logger.info("")

    try:
        zh_summary, en_summary = await summarize_article_bilingual(title, content)

        logger.info("=" * 60)
        logger.info("  ✅ 双语摘要生成成功！")
        logger.info("=" * 60)
        logger.info("")

        # 显示中文摘要
        logger.info("📌 中文摘要:")
        logger.info(f"   {zh_summary}")
        logger.info(f"   字数: {len(zh_summary)}")
        logger.info("")

        # 显示英文摘要
        logger.info("📌 English Summary:")
        logger.info(f"   {en_summary}")
        logger.info(f"   Words: {len(en_summary.split())}")
        logger.info("")

        # 验证结果
        success = True
        if not zh_summary or len(zh_summary) < 10:
            logger.warning("⚠️  中文摘要质量不佳")
            success = False
        if not en_summary or len(en_summary.split()) < 5:
            logger.warning("⚠️  英文摘要质量不佳")
            success = False

        if success:
            logger.info("=" * 60)
            logger.info("  ✅ 所有测试通过！")
            logger.info("=" * 60)
            logger.info("")
            logger.info("下一步:")
            logger.info("  1. 重启应用以应用更改")
            logger.info("  2. 测试RSS抓取是否生成双语摘要")
            logger.info("  3. 查看API响应是否包含 summary_en 字段")
        else:
            logger.warning("=" * 60)
            logger.info("  ⚠️  测试完成，但摘要质量需要改进")
            logger.info("=" * 60)

    except Exception as e:
        logger.error("")
        logger.error("=" * 60)
        logger.error("  ❌ 测试失败")
        logger.error("=" * 60)
        logger.error(f"错误: {e}")
        logger.error("")
        logger.error("建议:")
        logger.error("  1. 检查 API Key 是否正确")
        logger.error("  2. 检查网络连接")
        logger.error("  3. 查看详细错误日志")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(test_bilingual_summary())
