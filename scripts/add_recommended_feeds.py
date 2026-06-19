#!/usr/bin/env python3
"""
批量添加推荐 RSS 源脚本

用法:
    python scripts/add_recommended_feeds.py
    python scripts/add_recommended_feeds.py --category tech
    python scripts/add_recommended_feeds.py --feed-id 1
"""
import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from datetime import datetime

# API 配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")


# 推荐的 RSS 源列表
RECOMMENDED_FEEDS = [
    # 国际科技媒体
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "category": "tech",
        "description": "科技新闻、评论和评测"
    },
    {
        "name": "Wired",
        "url": "https://www.wired.com/feed/rss",
        "category": "tech",
        "description": "科技文化、未来趋势"
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "category": "tech",
        "description": "新兴技术深度报道"
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "category": "tech",
        "description": "技术新闻深度分析"
    },

    # 中文科技媒体
    {
        "name": "虎嗅",
        "url": "https://www.huxiu.com/rss/0.xml",
        "category": "tech-china",
        "description": "商业科技资讯"
    },
    {
        "name": "钛媒体",
        "url": "https://www.tmtpost.com/rss",
        "category": "tech-china",
        "description": "TMT 领域专业媒体"
    },
    {
        "name": "爱范儿",
        "url": "https://www.ifanr.com/feed",
        "category": "tech-china",
        "description": "科技生活媒体"
    },

    # AI 专用
    {
        "name": "MIT AI News",
        "url": "https://news.mit.edu/topic/artificial-intelligence2/feed",
        "category": "ai",
        "description": "MIT AI 研究新闻"
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "category": "ai",
        "description": "OpenAI 官方博客"
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "category": "ai",
        "description": "Google AI 研究博客"
    },

    # 开发工具
    {
        "name": "DEV.to",
        "url": "https://dev.to/feed",
        "category": "development",
        "description": "开发者社区"
    },
    {
        "name": "Hashnode",
        "url": "https://hashnode.com/feed.xml",
        "category": "development",
        "description": "技术博客平台"
    },

    # 科学
    {
        "name": "Nature News",
        "url": "https://www.nature.com/news/rss",
        "category": "science",
        "description": "自然杂志新闻"
    },
    {
        "name": "ScienceDaily",
        "url": "https://www.sciencedaily.com/rss/top.xml",
        "category": "science",
        "description": "每日科学新闻"
    },

    # 金融科技
    {
        "name": "FinTech News",
        "url": "https://www.ft.com/rss/companies/tech",
        "category": "fintech",
        "description": "金融科技新闻"
    },
]


def add_feed(feed_data: dict) -> bool:
    """
    添加单个 RSS 源

    Args:
        feed_data: RSS 源数据

    Returns:
        是否成功
    """
    url = f"{API_BASE_URL}/api/feeds"
    headers = {}
    if API_TOKEN:
        headers["X-API-Token"] = API_TOKEN

    try:
        response = requests.post(
            url,
            json={
                "name": feed_data["name"],
                "url": feed_data["url"],
                "category": feed_data["category"],
                "is_active": True
            },
            headers=headers,
            timeout=10
        )

        if response.status_code == 201:
            print(f"✅ 成功添加: {feed_data['name']}")
            return True
        elif response.status_code == 409:
            print(f"⏭️  已存在: {feed_data['name']}")
            return True
        else:
            print(f"❌ 失败: {feed_data['name']} - {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 异常: {feed_data['name']} - {e}")
        return False


def get_existing_feeds() -> list:
    """
    获取已存在的 RSS 源列表

    Returns:
        已存在的源列表
    """
    url = f"{API_BASE_URL}/api/feeds"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"获取现有源失败: {e}")
    return []


def main():
    global API_BASE_URL

    parser = argparse.ArgumentParser(description="批量添加推荐 RSS 源")
    parser.add_argument("--category", help="只添加指定分类的源")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要添加的源，不实际添加")
    parser.add_argument("--api-url", default=API_BASE_URL, help="API 地址")
    args = parser.parse_args()

    # 更新 API URL
    API_BASE_URL = args.api_url

    print("=" * 60)
    print("批量添加推荐 RSS 源")
    print("=" * 60)
    print(f"API 地址: {API_BASE_URL}")
    print(f"总源数: {len(RECOMMENDED_FEEDS)}")

    # 筛选分类
    feeds_to_add = RECOMMENDED_FEEDS
    if args.category:
        feeds_to_add = [f for f in RECOMMENDED_FEEDS if f["category"] == args.category]
        print(f"筛选分类: {args.category}")

    print(f"待添加源数: {len(feeds_to_add)}")
    print("-" * 60)

    if args.dry_run:
        print("🔍 DRY RUN 模式 - 不会实际添加")
        for feed in feeds_to_add:
            print(f"  - {feed['name']} ({feed['category']})")
        return

    # 获取已存在的源
    existing_feeds = get_existing_feeds()
    existing_urls = {f["url"] for f in existing_feeds}
    print(f"已存在源数: {len(existing_urls)}")

    # 添加新源
    success_count = 0
    skip_count = 0

    for feed in feeds_to_add:
        if feed["url"] in existing_urls:
            skip_count += 1
            continue

        if add_feed(feed):
            success_count += 1

    print("-" * 60)
    print(f"完成: 成功 {success_count}, 跳过 {skip_count}, 失败 {len(feeds_to_add) - success_count - skip_count}")


if __name__ == "__main__":
    main()
