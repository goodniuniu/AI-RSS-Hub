"""
RSS 生成服务

为文章数据生成 RSS 2.0 格式的 XML 输出
"""
from datetime import datetime
from typing import List, Optional
from feedgen.feed import FeedGenerator
from app.models import Article
import logging

logger = logging.getLogger(__name__)


class RSSGenerator:
    """
    RSS 生成器

    功能：
    - 生成标准 RSS 2.0 格式
    - 支持多种摘要语言（中文、英文、双语）
    - 支持分类过滤
    - 支持时间范围过滤
    - 自动添加来源信息
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        language: str = "zh-cn",
        feed_title: str = "AI-RSS-Hub 智能资讯",
        feed_description: str = "AI 智能聚合的 RSS 资讯源，提供中英文双语摘要"
    ):
        """
        初始化 RSS 生成器

        Args:
            base_url: 服务基础 URL
            language: RSS 语言代码
            feed_title: RSS 标题
            feed_description: RSS 描述
        """
        self.base_url = base_url
        self.language = language
        self.feed_title = feed_title
        self.feed_description = feed_description

    def generate_rss(
        self,
        articles: List[Article],
        title: Optional[str] = None,
        description: Optional[str] = None,
        summary_type: str = "zh"  # zh, en, bilingual
    ) -> str:
        """
        生成 RSS XML

        Args:
            articles: 文章列表
            title: 自定义 RSS 标题
            description: 自定义 RSS 描述
            summary_type: 摘要类型 (zh/en/bilingual)

        Returns:
            RSS XML 字符串
        """
        logger.info(f"RSS 生成器收到 {len(articles)} 篇文章")
        fg = FeedGenerator()

        # 设置 RSS 基本信息
        fg.id(f"{self.base_url}/api/rss")
        fg.title(title or self.feed_title)
        fg.link(href=self.base_url, rel="alternate")
        fg.description(description or self.feed_description)
        fg.language(self.language)
        fg.generator("AI-RSS-Hub 1.0")

        # 设置最后构建时间（使用字符串格式）
        last_build = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        fg.lastBuildDate(last_build)

        # 添加文章条目
        entry_count = 0
        for i, article in enumerate(articles):
            try:
                logger.info(f"处理第 {i+1} 篇文章: {article.title[:50]}...")
                self._create_entry(fg, article, summary_type)
                entry_count += 1
            except Exception as e:
                logger.error(f"生成 RSS 条目失败: {article.title}, 错误: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue

        # 生成 RSS XML
        rss_xml = fg.rss_str(pretty=True)

        logger.info(f"成功生成 RSS: {entry_count}/{len(articles)} 篇文章, 摘要类型: {summary_type}")

        return rss_xml

    def _create_entry(self, fg: FeedGenerator, article: Article, summary_type: str) -> None:
        """
        创建单个 RSS 条目

        Args:
            fg: FeedGenerator 对象
            article: 文章对象
            summary_type: 摘要类型

        Returns:
            None（直接修改 fg）
        """
        # 使用 feedgen 的正确 API：调用 fg.add_entry() 创建新条目
        fe = fg.add_entry()

        # 基本信息
        fe.id(article.link)
        fe.title(article.title)
        fe.link(href=article.link)

        # 生成描述（摘要）
        description = self._generate_description(article, summary_type)
        fe.description(description)

        # 发布时间（转换为字符串格式，避免时区问题）
        if article.published_at:
            # 直接使用 ISO 格式字符串
            pub_date_str = article.published_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
            fe.published(pub_date_str)

        # 作者/来源信息
        if article.feed:
            feed_name = article.feed.name
            fe.author(name=feed_name)

        # 分类
        if article.feed and article.feed.category:
            fe.category(article.feed.category)

    def _generate_description(self, article: Article, summary_type: str) -> str:
        """
        生成文章描述（HTML 格式）

        Args:
            article: 文章对象
            summary_type: 摘要类型

        Returns:
            HTML 格式的描述
        """
        parts = []

        # 中文摘要
        if summary_type in ["zh", "bilingual"] and article.summary:
            parts.append(f"<strong>中文摘要：</strong><br/>")
            parts.append(f"{article.summary}")

        # 英文摘要
        if summary_type in ["en", "bilingual"] and article.summary_en:
            if summary_type == "bilingual":
                parts.append("<br/><br/>")
            parts.append(f"<strong>English Summary:</strong><br/>")
            parts.append(f"{article.summary_en}")

        # 如果没有摘要，使用标题
        if not parts:
            parts.append(f"<em>{article.title}</em>")

        # 添加"阅读原文"链接
        parts.append("<br/><br/>")
        parts.append(f'<a href="{article.link}">阅读原文</a>')

        # 添加来源信息
        if article.feed:
            parts.append(f' | 来源: {article.feed.name}')

        # 组合（不使用 CDATA，feedgen 会自动处理）
        description = "".join(parts)
        return description

    def generate_category_rss(
        self,
        articles: List[Article],
        category: str,
        summary_type: str = "zh"
    ) -> str:
        """
        生成特定分类的 RSS

        Args:
            articles: 文章列表
            category: 分类名称
            summary_type: 摘要类型

        Returns:
            RSS XML 字符串
        """
        title = f"AI-RSS-Hub - {category}"
        description = f"AI 智能聚合的 {category} 资讯"

        return self.generate_rss(
            articles=articles,
            title=title,
            description=description,
            summary_type=summary_type
        )


def generate_rss_response(
    articles: List[Article],
    summary_type: str = "zh",
    base_url: str = "http://localhost:8000",
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """
    便捷函数：生成 RSS 响应

    Args:
        articles: 文章列表
        summary_type: 摘要类型 (zh/en/bilingual)
        base_url: 服务基础 URL
        title: 自定义标题
        description: 自定义描述

    Returns:
        RSS XML 字符串
    """
    generator = RSSGenerator(base_url=base_url)
    return generator.generate_rss(
        articles=articles,
        title=title,
        description=description,
        summary_type=summary_type
    )


def generate_category_rss(
    articles: List[Article],
    category: str,
    summary_type: str = "zh",
    base_url: str = "http://localhost:8000"
) -> str:
    """
    便捷函数：生成分类 RSS

    Args:
        articles: 文章列表
        category: 分类名称
        summary_type: 摘要类型
        base_url: 服务基础 URL

    Returns:
        RSS XML 字符串
    """
    generator = RSSGenerator(base_url=base_url)
    return generator.generate_category_rss(
        articles=articles,
        category=category,
        summary_type=summary_type
    )
