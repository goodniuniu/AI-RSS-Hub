#!/usr/bin/env python3
"""
AI-RSS-Hub Usage Examples

This script demonstrates how to use the AI-RSS-Hub API from a client.
"""

from rss_client import RSSHubClient, RSSHubAdminClient
import json


def print_separator(title):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def example_basic_usage():
    """Basic usage example - read-only operations"""
    print_separator("Example 1: Basic Usage (Read-Only)")

    # Initialize client (no API token needed for read operations)
    client = RSSHubClient(base_url="http://localhost:8000")

    # 1. Health check
    print("1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Message: {health['message']}")

    # 2. System status
    print("\n2. System Status:")
    status = client.get_status()
    print(f"   Scheduler Running: {status['scheduler']['running']}")
    print(f"   Database: {status['database']}")
    print(f"   LLM Configured: {status['llm_configured']}")

    # 3. Get all feeds
    print("\n3. All RSS Feeds:")
    feeds = client.get_feeds()
    print(f"   Total: {len(feeds)} feeds")
    for feed in feeds:
        status_icon = "✅" if feed.get("is_active") else "❌"
        print(f"   {status_icon} {feed['name']} ({feed['category']})")

    # 4. Get latest articles
    print("\n4. Latest Articles:")
    articles = client.get_latest_articles(limit=5)
    for i, article in enumerate(articles, 1):
        print(f"\n   [{i}] {article['title']}")
        print(f"       📰 {article['feed_name']}")
        print(f"       📝 {article['summary'][:80]}...")
        print(f"       🔗 {article['link'][:60]}...")


def example_filtered_articles():
    """Example of filtering articles"""
    print_separator("Example 2: Filtered Articles")

    client = RSSHubClient()

    # Get tech articles from last 7 days
    print("1. Tech category articles (last 7 days):")
    articles = client.get_articles(category="tech", days=7, limit=3)
    for article in articles:
        print(f"   - {article['title']}")
        print(f"     {article['summary'][:60]}...")

    # Get articles from specific feed
    print("\n2. Articles from Hacker News:")
    feeds = client.get_feeds()
    hacker_news_feed = next((f for f in feeds if "Hacker News" in f["name"]), None)
    if hacker_news_feed:
        articles = client.get_articles_by_feed(hacker_news_feed["id"], limit=3)
        for article in articles:
            print(f"   - {article['title']}")


def example_search():
    """Example of searching articles"""
    print_separator("Example 3: Search Articles")

    client = RSSHubClient()

    # Search for articles
    queries = ["AI", "Python", "security"]

    for query in queries:
        print(f"\nSearching for '{query}':")
        results = client.search_articles(query, limit=3)
        if results:
            for article in results:
                print(f"   - {article['title']}")
        else:
            print("   No results found")


def example_admin_operations():
    """Example of admin operations (requires API token)"""
    print_separator("Example 4: Admin Operations")

    # Note: You need to set up API_TOKEN in .env file first
    # Uncomment the following lines to test:

    # admin_client = RSSHubAdminClient(
    #     base_url="http://localhost:8000",
    #     api_token="your-api-token-here"
    # )

    # # 1. Get statistics
    # print("1. System Statistics:")
    # stats = admin_client.get_statistics()
    # print(f"   Total Feeds: {stats['total_feeds']}")
    # print(f"   Active Feeds: {stats['active_feeds']}")
    # print(f"   Total Articles: {stats['total_articles']}")
    # print(f"   Categories: {', '.join(stats['categories'])}")

    # # 2. Add a new feed
    # print("\n2. Adding new feed:")
    # new_feed = admin_client.add_feed(
    #     name="Example Blog",
    #     url="https://example.com/feed.xml",
    #     category="blog"
    # )
    # print(f"   Added: {new_feed['name']} (ID: {new_feed['id']})")

    # # 3. Trigger manual fetch
    # print("\n3. Triggering manual RSS fetch:")
    # result = admin_client.fetch_feeds()
    # print(f"   Total articles processed: {result.get('total_articles', 0)}")

    print("   ⚠️  Admin operations require API token")
    print("   Set API_TOKEN in your .env file to test these features")


def example_bulk_operations():
    """Example of bulk operations"""
    print_separator("Example 5: Bulk Operations")

    # Note: Requires API token
    print("Bulk adding multiple feeds:")

    feeds_to_add = [
        {
            "name": "Reddit Programming",
            "url": "https://www.reddit.com/r/programming/.rss",
            "category": "programming"
        },
        {
            "name": "Hacker News",
            "url": "https://hnrss.org/frontpage",
            "category": "tech"
        }
    ]

    print(f"\n   Feeds to add: {len(feeds_to_add)}")
    for feed in feeds_to_add:
        print(f"   - {feed['name']}: {feed['url']}")

    print("\n   ⚠️  Uncomment and set API token to execute")

    # admin = RSSHubAdminClient(api_token="your-token")
    # created = admin.bulk_add_feeds(feeds_to_add)
    # print(f"\n   Successfully added: {len(created)} feeds")


def example_error_handling():
    """Example of error handling"""
    print_separator("Example 6: Error Handling")

    client = RSSHubClient()

    # Try to access non-existent article
    print("1. Attempting to access non-existent article:")
    try:
        article = client.get_article(99999)
        print(f"   Article: {article['title']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Try to add feed without API token
    print("\n2. Attempting to add feed without API token:")
    try:
        feed = client.add_feed("Test", "http://example.com/feed.xml")
        print(f"   Added: {feed['name']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n3. Proper error handling:")
    try:
        feeds = client.get_feeds()
        print(f"   ✓ Successfully retrieved {len(feeds)} feeds")
    except Exception as e:
        print(f"   ✗ Failed to get feeds: {e}")


def example_json_output():
    """Example of exporting data as JSON"""
    print_separator("Example 7: Export Data as JSON")

    client = RSSHubClient()

    # Export feeds
    feeds = client.get_feeds()
    print("1. Feeds JSON:")
    print(json.dumps(feeds, indent=2)[:300] + "...")

    # Export articles
    articles = client.get_latest_articles(limit=3)
    print("\n2. Articles JSON:")
    for article in articles:
        article_data = {
            "title": article["title"],
            "summary": article["summary"],
            "link": article["link"],
            "feed": article["feed_name"]
        }
        print(json.dumps(article_data, indent=2, ensure_ascii=False))


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("  AI-RSS-Hub Client Usage Examples")
    print("  Make sure the server is running on localhost:8000")
    print("="*60)

    try:
        # Run examples
        example_basic_usage()
        example_filtered_articles()
        example_search()
        example_admin_operations()
        example_bulk_operations()
        example_error_handling()
        example_json_output()

        print("\n" + "="*60)
        print("  All examples completed!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the AI-RSS-Hub server is running on http://localhost:8000")


if __name__ == "__main__":
    main()
