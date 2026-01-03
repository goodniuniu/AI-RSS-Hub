#!/usr/bin/env python3
"""
AI-RSS-Hub Python Client Library

Simple, clean interface to the AI-RSS-Hub API.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime


class RSSHubClient:
    """Client for AI-RSS-Hub API"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the RSSHub client.

        Args:
            base_url: Base URL of the API (default: http://localhost:8000)
            api_token: API token for authenticated requests (optional)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication if configured"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_token:
            headers["X-API-Token"] = self.api_token
        return headers

    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response with error checking"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = response.json().get("detail", "Unknown error")
            raise Exception(f"API Error ({response.status_code}): {error_detail}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request Error: {str(e)}")

    def health_check(self) -> Dict:
        """
        Check API health status.

        Returns:
            Dict with health status
        """
        response = self.session.get(
            f"{self.base_url}/api/health",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        return self._handle_response(response)

    def get_status(self) -> Dict:
        """
        Get system status including scheduler and database info.

        Returns:
            Dict with system status
        """
        response = self.session.get(
            f"{self.base_url}/api/status",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        return self._handle_response(response)

    def get_feeds(self, active_only: bool = False) -> List[Dict]:
        """
        Get all RSS feeds.

        Args:
            active_only: If True, only return active feeds

        Returns:
            List of feed dictionaries
        """
        params = {"active_only": active_only} if active_only else {}
        response = self.session.get(
            f"{self.base_url}/api/feeds",
            headers=self._get_headers(),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)

    def get_feed(self, feed_id: int) -> Dict:
        """
        Get a specific feed by ID.

        Args:
            feed_id: Feed ID

        Returns:
            Feed dictionary
        """
        response = self.session.get(
            f"{self.base_url}/api/feeds/{feed_id}",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        return self._handle_response(response)

    def add_feed(
        self,
        name: str,
        url: str,
        category: str = "tech",
        is_active: bool = True
    ) -> Dict:
        """
        Add a new RSS feed.

        Args:
            name: Feed name
            url: Feed URL
            category: Feed category (default: "tech")
            is_active: Whether feed is active (default: True)

        Returns:
            Created feed dictionary

        Raises:
            Exception: If API token is not configured or request fails
        """
        if not self.api_token:
            raise Exception("API token required for adding feeds")

        data = {
            "name": name,
            "url": url,
            "category": category,
            "is_active": is_active
        }
        response = self.session.post(
            f"{self.base_url}/api/feeds",
            json=data,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        return self._handle_response(response)

    def get_articles(
        self,
        limit: int = 20,
        category: Optional[str] = None,
        days: Optional[int] = None
    ) -> List[Dict]:
        """
        Get articles with optional filters.

        Args:
            limit: Maximum number of articles to return (default: 20)
            category: Filter by category (optional)
            days: Only include articles from last N days (optional)

        Returns:
            List of article dictionaries
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        if days:
            params["days"] = days

        response = self.session.get(
            f"{self.base_url}/api/articles",
            headers=self._get_headers(),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)

    def get_article(self, article_id: int) -> Dict:
        """
        Get a specific article by ID.

        Args:
            article_id: Article ID

        Returns:
            Article dictionary
        """
        response = self.session.get(
            f"{self.base_url}/api/articles/{article_id}",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        return self._handle_response(response)

    def fetch_feeds(self) -> Dict:
        """
        Trigger manual RSS fetch for all active feeds.

        Returns:
            Dict with fetch results including article counts

        Raises:
            Exception: If API token is not configured or request fails
        """
        if not self.api_token:
            raise Exception("API token required for manual fetch")

        response = self.session.post(
            f"{self.base_url}/api/feeds/fetch",
            headers=self._get_headers(),
            timeout=self.timeout  # May take longer for multiple feeds
        )
        return self._handle_response(response)

    def search_articles(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search articles by title or content (client-side filtering).

        Args:
            query: Search query
            limit: Maximum results (default: 20)

        Returns:
            List of matching articles
        """
        articles = self.get_articles(limit=100)  # Get more for filtering
        query_lower = query.lower()

        matches = [
            a for a in articles
            if query_lower in a.get("title", "").lower() or
               query_lower in a.get("summary", "").lower() or
               query_lower in a.get("content", "").lower()
        ]

        return matches[:limit]

    def get_latest_articles(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recent articles.

        Args:
            limit: Number of articles (default: 10)

        Returns:
            List of recent articles
        """
        return self.get_articles(limit=limit)

    def get_articles_by_feed(self, feed_id: int, limit: int = 20) -> List[Dict]:
        """
        Get articles from a specific feed (client-side filtering).

        Args:
            feed_id: Feed ID
            limit: Maximum articles (default: 20)

        Returns:
            List of articles from the specified feed
        """
        articles = self.get_articles(limit=100)
        feed_articles = [a for a in articles if a.get("feed_id") == feed_id]
        return feed_articles[:limit]


class RSSHubAdminClient(RSSHubClient):
    """
    Extended client with admin features.

    Requires API token for all operations.
    """

    def __init__(self, base_url: str = "http://localhost:8000", api_token: str = None):
        if not api_token:
            raise ValueError("API token is required for AdminClient")
        super().__init__(base_url=base_url, api_token=api_token)

    def bulk_add_feeds(self, feeds: List[Dict]) -> List[Dict]:
        """
        Add multiple feeds at once.

        Args:
            feeds: List of feed dictionaries with keys: name, url, category

        Returns:
            List of created feeds
        """
        created = []
        for feed_data in feeds:
            try:
                feed = self.add_feed(
                    name=feed_data["name"],
                    url=feed_data["url"],
                    category=feed_data.get("category", "tech")
                )
                created.append(feed)
            except Exception as e:
                print(f"Failed to add feed {feed_data.get('name')}: {e}")
        return created

    def get_statistics(self) -> Dict:
        """
        Get system statistics.

        Returns:
            Dict with various statistics
        """
        status = self.get_status()
        feeds = self.get_feeds()
        articles = self.get_articles(limit=10000)  # Get all

        return {
            "total_feeds": len(feeds),
            "active_feeds": len([f for f in feeds if f.get("is_active")]),
            "total_articles": len(articles),
            "categories": list(set(f.get("category") for f in feeds)),
            "scheduler_running": status.get("scheduler", {}).get("running", False),
            "llm_configured": status.get("llm_configured", False)
        }


# Convenience functions for quick usage

def create_client(base_url: str = "http://localhost:8000", api_token: str = None) -> RSSHubClient:
    """
    Create an RSSHub client.

    Args:
        base_url: API base URL
        api_token: Optional API token

    Returns:
        RSSHubClient instance
    """
    return RSSHubClient(base_url=base_url, api_token=api_token)


def create_admin_client(base_url: str = "http://localhost:8000", api_token: str = None) -> RSSHubAdminClient:
    """
    Create an admin RSSHub client (requires API token).

    Args:
        base_url: API base URL
        api_token: API token (required)

    Returns:
        RSSHubAdminClient instance
    """
    return RSSHubAdminClient(base_url=base_url, api_token=api_token)


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = RSSHubClient(api_token="your-token-here")

    # Check health
    print("Health:", client.health_check())

    # Get feeds
    feeds = client.get_feeds()
    print(f"\nTotal feeds: {len(feeds)}")

    # Get latest articles
    articles = client.get_latest_articles(limit=5)
    print(f"\nLatest {len(articles)} articles:")
    for article in articles:
        print(f"\n  {article['title']}")
        print(f"  Summary: {article['summary'][:100]}...")
