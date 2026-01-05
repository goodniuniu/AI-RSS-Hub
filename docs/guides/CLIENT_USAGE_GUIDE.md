# AI-RSS-Hub Client Usage Guide

> Complete guide for consuming the AI-RSS-Hub API

---

## Table of Contents

1. [Interactive API Documentation](#interactive-api-documentation)
2. [API Endpoints Overview](#api-endpoints-overview)
3. [cURL Examples](#curl-examples)
4. [Python Client](#python-client)
5. [JavaScript/Node.js Client](#javascriptnodejs-client)
6. [Authentication](#authentication)
7. [Error Handling](#error-handling)

---

## 1. Interactive API Documentation

### Swagger UI (Recommended for Testing)
Open in browser: **http://localhost:8000/docs**

Features:
- 📖 Interactive documentation
- 🧪 Try out endpoints directly
- 📝 Auto-generated request/response examples
- 🔒 Authentication testing

### ReDoc
Open in browser: **http://localhost:8000/redoc**

Features:
- 📚 Clean, readable documentation
- 📋 Complete API reference

---

## 2. API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/health` | Health check | ❌ No |
| GET | `/api/status` | System status | ❌ No |
| GET | `/api/feeds` | List all RSS feeds | ❌ No |
| POST | `/api/feeds` | Add new RSS feed | ✅ Yes |
| GET | `/api/articles` | Get articles list | ❌ No |
| POST | `/api/feeds/fetch` | Manual RSS fetch | ✅ Yes |

---

## 3. cURL Examples

### 3.1 Health Check

```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "ok",
  "message": "AI-RSS-Hub is running"
}
```

### 3.2 System Status

```bash
curl http://localhost:8000/api/status
```

### 3.3 Get All Feeds

```bash
curl http://localhost:8000/api/feeds
```

### 3.4 Get Articles (with pagination)

```bash
# Get latest 10 articles
curl "http://localhost:8000/api/articles?limit=10"

# Get articles by category
curl "http://localhost:8000/api/articles?category=tech&limit=20"

# Get articles from last 7 days
curl "http://localhost:8000/api/articles?days=7&limit=50"
```

### 3.5 Add New Feed (Requires Authentication)

```bash
curl -X POST http://localhost:8000/api/feeds \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your-api-token-here" \
  -d '{
    "name": "My Blog",
    "url": "https://example.com/feed.xml",
    "category": "blog",
    "is_active": true
  }'
```

### 3.6 Manual RSS Fetch (Requires Authentication)

```bash
curl -X POST http://localhost:8000/api/feeds/fetch \
  -H "X-API-Token: your-api-token-here"
```

---

## 4. Python Client

### 4.1 Basic Setup

```python
import requests

BASE_URL = "http://localhost:8000"
API_TOKEN = "your-api-token-here"  # Optional, for protected endpoints

headers = {
    "X-API-Token": API_TOKEN
}
```

### 4.2 Get All Feeds

```python
import requests

def get_feeds(active_only=False):
    url = f"{BASE_URL}/api/feeds"
    params = {"active_only": active_only} if active_only else {}
    response = requests.get(url, params=params)
    return response.json()

# Usage
feeds = get_feeds()
for feed in feeds:
    print(f"{feed['name']}: {feed['url']}")
```

### 4.3 Get Articles

```python
def get_articles(limit=20, category=None, days=None):
    url = f"{BASE_URL}/api/articles"
    params = {"limit": limit}

    if category:
        params["category"] = category
    if days:
        params["days"] = days

    response = requests.get(url, params=params)
    return response.json()

# Usage
articles = get_articles(limit=10, category="tech")
for article in articles:
    print(f"\nTitle: {article['title']}")
    print(f"Summary (CN): {article['summary']}")
    print(f"Summary (EN): {article.get('summary_en', 'N/A')}")
    print(f"Link: {article['link']}")
```

### 4.4 Add New Feed

```python
def add_feed(name, url, category="tech", is_active=True):
    url = f"{BASE_URL}/api/feeds"
    headers = {"X-API-Token": API_TOKEN}
    data = {
        "name": name,
        "url": url,
        "category": category,
        "is_active": is_active
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Usage
new_feed = add_feed(
    name="Tech Blog",
    url="https://example.com/feed.xml",
    category="technology"
)
print(f"Added feed: {new_feed['name']} (ID: {new_feed['id']})")
```

### 4.5 Trigger Manual Fetch

```python
def fetch_feeds():
    url = f"{BASE_URL}/api/feeds/fetch"
    headers = {"X-API-Token": API_TOKEN}
    response = requests.post(url, headers=headers)
    return response.json()

# Usage
result = fetch_feeds()
print(f"Fetched {result['total_articles']} new articles")
```

### 4.6 Complete Python Client Class

```python
import requests
from typing import List, Dict, Optional

class RSSHubClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_token: Optional[str] = None):
        self.base_url = base_url
        self.api_token = api_token
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["X-API-Token"] = self.api_token
        return headers

    def health_check(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/api/health")
        return response.json()

    def get_status(self) -> Dict:
        """Get system status"""
        response = self.session.get(f"{self.base_url}/api/status")
        return response.json()

    def get_feeds(self, active_only: bool = False) -> List[Dict]:
        """Get all RSS feeds"""
        params = {"active_only": active_only} if active_only else {}
        response = self.session.get(f"{self.base_url}/api/feeds", params=params)
        return response.json()

    def get_articles(self, limit: int = 20, category: Optional[str] = None,
                    days: Optional[int] = None) -> List[Dict]:
        """Get articles with optional filters"""
        params = {"limit": limit}
        if category:
            params["category"] = category
        if days:
            params["days"] = days

        response = self.session.get(f"{self.base_url}/api/articles", params=params)
        return response.json()

    def add_feed(self, name: str, url: str, category: str = "tech",
                is_active: bool = True) -> Dict:
        """Add a new RSS feed"""
        data = {
            "name": name,
            "url": url,
            "category": category,
            "is_active": is_active
        }
        response = self.session.post(
            f"{self.base_url}/api/feeds",
            json=data,
            headers=self._get_headers()
        )
        return response.json()

    def fetch_feeds(self) -> Dict:
        """Trigger manual RSS fetch"""
        response = self.session.post(
            f"{self.base_url}/api/feeds/fetch",
            headers=self._get_headers()
        )
        return response.json()


# Usage Example
if __name__ == "__main__":
    # Initialize client (with API token for admin operations)
    client = RSSHubClient(api_token="your-api-token-here")

    # Check health
    print("Health:", client.health_check())

    # Get feeds
    feeds = client.get_feeds()
    print(f"Total feeds: {len(feeds)}")

    # Get latest articles
    articles = client.get_articles(limit=5)
    for article in articles:
        print(f"\n{article['title']}")
        print(f"Summary: {article['summary'][:100]}...")

    # Add new feed (requires API token)
    # new_feed = client.add_feed("My Blog", "https://example.com/feed.xml")
```

---

## 5. JavaScript/Node.js Client

### 5.1 Using fetch API

```javascript
const BASE_URL = 'http://localhost:8000';
const API_TOKEN = 'your-api-token-here';

// Get all feeds
async function getFeeds() {
  const response = await fetch(`${BASE_URL}/api/feeds`);
  const feeds = await response.json();
  return feeds;
}

// Get articles
async function getArticles(limit = 20, category = null, days = null) {
  const url = new URL(`${BASE_URL}/api/articles`);
  url.searchParams.append('limit', limit);
  if (category) url.searchParams.append('category', category);
  if (days) url.searchParams.append('days', days);

  const response = await fetch(url);
  return await response.json();
}

// Add new feed
async function addFeed(name, url, category = 'tech') {
  const response = await fetch(`${BASE_URL}/api/feeds`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Token': API_TOKEN
    },
    body: JSON.stringify({ name, url, category, is_active: true })
  });
  return await response.json();
}

// Usage
(async () => {
  const feeds = await getFeeds();
  console.log('Feeds:', feeds);

  const articles = await getArticles(10, 'tech');
  console.log('Articles:', articles);
})();
```

### 5.2 Using Axios

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';
const API_TOKEN = 'your-api-token-here';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'X-API-Token': API_TOKEN
  }
});

// Get all feeds
async function getFeeds() {
  const response = await api.get('/api/feeds');
  return response.data;
}

// Get articles
async function getArticles(limit = 20, category = null) {
  const params = { limit };
  if (category) params.category = category;

  const response = await api.get('/api/articles', { params });
  return response.data;
}

// Add new feed
async function addFeed(name, url, category = 'tech') {
  const response = await api.post('/api/feeds', {
    name,
    url,
    category,
    is_active: true
  });
  return response.data;
}

// Usage
(async () => {
  try {
    const feeds = await getFeeds();
    console.log(`Found ${feeds.length} feeds`);

    const articles = await getArticles(10);
    articles.forEach(article => {
      console.log(`${article.title}: ${article.summary}`);
    });
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
})();
```

---

## 6. Authentication

### 6.1 Configure API Token

Set the `API_TOKEN` in your `.env` file:

```bash
# .env
API_TOKEN=your-secret-api-token-here
```

### 6.2 Generate API Token

Use the provided script:

```bash
python scripts/generate_token.py
```

### 6.3 Using Authentication

For protected endpoints (`POST /api/feeds`, `POST /api/feeds/fetch`), include the token:

```bash
# cURL
curl -X POST http://localhost:8000/api/feeds \
  -H "X-API-Token: your-token-here" \
  -d '{"name": "My Feed", "url": "https://example.com/feed.xml"}'
```

```python
# Python
headers = {"X-API-Token": "your-token-here"}
response = requests.post(url, json=data, headers=headers)
```

```javascript
// JavaScript
headers: {
  'X-API-Token': 'your-token-here'
}
```

---

## 7. Error Handling

### 7.1 HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 403 | Forbidden (invalid API token) |
| 422 | Validation Error |
| 500 | Internal Server Error |

### 7.2 Error Response Format

```json
{
  "detail": "Error message here"
}
```

### 7.3 Error Handling Examples

**Python:**
```python
def add_feed(name, url):
    try:
        response = requests.post(
            f"{BASE_URL}/api/feeds",
            json={"name": name, "url": url},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
```

**JavaScript:**
```javascript
async function addFeed(name, url) {
  try {
    const response = await fetch(`${BASE_URL}/api/feeds`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Token': API_TOKEN
      },
      body: JSON.stringify({ name, url })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

---

## 8. Quick Start Examples

### Python Script Example

```python
#!/usr/bin/env python3
"""Quick start example for AI-RSS-Hub API"""

from rss_client import RSSHubClient

# Initialize client
client = RSSHubClient(api_token="your-token")

# 1. Check health
print("✅ API Status:", client.health_check())

# 2. Get all feeds
feeds = client.get_feeds()
print(f"\n📡 Total Feeds: {len(feeds)}")

# 3. Get latest articles
articles = client.get_articles(limit=5)
print(f"\n📰 Latest {len(articles)} Articles:")
for article in articles:
    print(f"\n  Title: {article['title']}")
    print(f"  Summary: {article['summary'][:100]}...")
    print(f"  Link: {article['link']}")

# 4. Add new feed
# new_feed = client.add_feed("Tech Blog", "https://example.com/feed.xml")
# print(f"\n➕ Added: {new_feed['name']}")
```

### Node.js Script Example

```javascript
// quick-start.js
const axios = require('axios');

const API = axios.create({
  baseURL: 'http://localhost:8000'
});

async function main() {
  // 1. Check health
  const health = (await API.get('/api/health')).data;
  console.log('✅ API Status:', health);

  // 2. Get feeds
  const feeds = (await API.get('/api/feeds')).data;
  console.log(`\n📡 Total Feeds: ${feeds.length}`);

  // 3. Get articles
  const articles = (await API.get('/api/articles?limit=5')).data;
  console.log(`\n📰 Latest Articles:`);
  articles.forEach(article => {
    console.log(`\n  ${article.title}`);
    console.log(`  ${article.summary.substring(0, 100)}...`);
  });
}

main().catch(console.error);
```

---

## 9. Environment Variables

### Server Side (.env)

```bash
# API Configuration
API_TOKEN=your-secret-token-here
OPENAI_API_KEY=sk-your-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# Database
DATABASE_URL=sqlite:///./ai_rss_hub.db

# Fetch Configuration
FETCH_INTERVAL_HOURS=1

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
RATE_LIMIT_ENABLED=true
```

### Client Side

```bash
# .env for client application
API_BASE_URL=http://localhost:8000
API_TOKEN=your-token-here
```

---

## 10. Testing the API

### Using cURL

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test articles endpoint
curl "http://localhost:8000/api/articles?limit=3" | jq
```

### Using Python

```bash
# Install dependencies
pip install requests

# Run test
python test_api.py
```

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

---

## Support

- 📖 API Docs: http://localhost:8000/docs
- 📚 ReDoc: http://localhost:8000/redoc
- 💡 GitHub Issues: [Project Repository]

---

**Last Updated:** 2026-01-03
