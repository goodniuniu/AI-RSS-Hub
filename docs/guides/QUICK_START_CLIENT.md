# AI-RSS-Hub - Quick Start for Clients

## 🚀 Three Ways to Use the API

### 1️⃣ Interactive API Documentation (Easiest)
Open your browser: **http://localhost:8000/docs**

- Try out all endpoints interactively
- No coding required
- Perfect for testing and exploration

---

### 2️⃣ Python Client Library (Recommended)

#### Installation
```bash
cd AI-RSS-Hub
pip install requests
```

#### Quick Start
```python
from rss_client import RSSHubClient

# Initialize
client = RSSHubClient()

# Get articles
articles = client.get_latest_articles(limit=10)
for article in articles:
    print(article['title'])
    print(article['summary'])
    print(article['link'])
    print('---')
```

#### Full Example
```python
from rss_client import RSSHubClient, RSSHubAdminClient

# Read-only client
client = RSSHubClient()

# Health check
print(client.health_check())

# Get all feeds
feeds = client.get_feeds()
print(f"Total feeds: {len(feeds)}")

# Get latest articles
articles = client.get_latest_articles(limit=5)

# Search articles
results = client.search_articles("AI", limit=10)

# Admin operations (requires API token)
admin = RSSHubAdminClient(api_token="your-token")

# Add new feed
admin.add_feed("My Blog", "https://example.com/feed.xml")

# Trigger manual fetch
admin.fetch_feeds()

# Get statistics
stats = admin.get_statistics()
```

#### Run Examples
```bash
python3 example_usage.py
```

---

### 3️⃣ HTTP API (Any Language)

#### Base URL
```
http://localhost:8000
```

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/status` | System status |
| GET | `/api/feeds` | List all feeds |
| POST | `/api/feeds` | Add new feed (needs auth) |
| GET | `/api/articles` | Get articles |
| POST | `/api/feeds/fetch` | Manual fetch (needs auth) |

#### cURL Examples

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Get Articles:**
```bash
curl "http://localhost:8000/api/articles?limit=10"
```

**Add Feed (with auth):**
```bash
curl -X POST http://localhost:8000/api/feeds \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your-token-here" \
  -d '{
    "name": "Tech Blog",
    "url": "https://example.com/feed.xml",
    "category": "tech"
  }'
```

---

## 📚 Full Documentation

- **Complete Guide**: `CLIENT_USAGE_GUIDE.md`
- **Python Library**: `rss_client.py`
- **Examples**: `example_usage.py`
- **Interactive Docs**: http://localhost:8000/docs

---

## 🔑 Authentication (Optional)

For protected endpoints, set up API token:

```bash
# Generate token
python scripts/generate_token.py

# Add to .env
echo "API_TOKEN=generated-token-here" >> .env
```

Then use in requests:
```python
client = RSSHubClient(api_token="your-token")
```

---

## ✅ Test the API

```bash
# Quick health check
curl http://localhost:8000/api/health

# Run Python examples
python3 example_usage.py

# Open interactive docs
# http://localhost:8000/docs
```

---

## 📖 Next Steps

1. ✅ Server is running on http://localhost:8000
2. ✅ API is working (62 articles in database)
3. ✅ Client library installed
4. ✅ Examples ready to run

Choose your approach and start building!
