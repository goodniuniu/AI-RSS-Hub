# Postman Guide for AI-RSS-Hub API

> Server: `http://8.134.202.27:8000`

---

## 🚀 Quick Setup

### 1. Environment Variables

Create an environment in Postman with these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://8.134.202.27:8000` | API base URL |
| `api_token` | `your-token-here` | API token (if configured) |

**Steps:**
1. Click the gear icon (top right) → "Environments"
2. Click "Add"
3. Name: `AI-RSS-Hub`
4. Add variables:
   - Variable: `base_url`
   - Initial Value: `http://8.134.202.27:8000`
   - Variable: `api_token`
   - Initial Value: (leave empty or add your token)
5. Click "Add" and select this environment

---

## 📡 API Endpoints

### 1. Health Check
**GET** `{{base_url}}/api/health`

**Description:** Check if API is running

**Headers:** None required

**Pre-request Script:** None

**Tests (Optional):**
```javascript
pm.test("Status is ok", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql("ok");
});
```

**Example Response:**
```json
{
    "status": "ok",
    "message": "AI-RSS-Hub is running"
}
```

---

### 2. System Status
**GET** `{{base_url}}/api/status`

**Description:** Get system status including scheduler and database info

**Headers:** None required

**Example Response:**
```json
{
    "status": "running",
    "scheduler": {
        "running": true,
        "jobs": [...]
    },
    "database": "sqlite:///./ai_rss_hub.db",
    "fetch_interval_hours": 1,
    "llm_configured": true
}
```

---

### 3. Get All RSS Feeds
**GET** `{{base_url}}/api/feeds`

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| `active_only` | `true` or `false` | Only return active feeds (optional) |

**Headers:** None required

**Example Response:**
```json
[
    {
        "id": 1,
        "name": "Hacker News",
        "url": "https://hnrss.org/frontpage",
        "category": "tech",
        "is_active": true,
        "created_at": "2025-12-25T11:05:34.159232"
    }
]
```

**Postman Setup:**
1. Method: `GET`
2. URL: `{{base_url}}/api/feeds`
3. Params tab: Add `active_only` = `true` (optional)
4. Send

---

### 4. Add New RSS Feed
**POST** `{{base_url}}/api/feeds`

**Headers:**
| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |
| `X-API-Token` | `{{api_token}}` |

**Body (raw JSON):**
```json
{
    "name": "My Tech Blog",
    "url": "https://example.com/feed.xml",
    "category": "tech",
    "is_active": true
}
```

**Postman Setup:**
1. Method: `POST`
2. URL: `{{base_url}}/api/feeds`
3. Headers tab:
   - Add `Content-Type`: `application/json`
   - Add `X-API-Token`: `{{api_token}}`
4. Body tab:
   - Select `raw`
   - Select `JSON` from dropdown
   - Paste the JSON above
5. Send

---

### 5. Get Articles
**GET** `{{base_url}}/api/articles`

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| `limit` | `20` | Number of articles to return |
| `category` | `tech` | Filter by category (optional) |
| `days` | `7` | Only articles from last N days (optional) |

**Headers:** None required

**Example Responses:**

All articles (limit 10):
```
GET {{base_url}}/api/articles?limit=10
```

Tech category only:
```
GET {{base_url}}/api/articles?category=tech&limit=20
```

Last 7 days:
```
GET {{base_url}}/api/articles?days=7&limit=50
```

**Postman Setup:**
1. Method: `GET`
2. URL: `{{base_url}}/api/articles`
3. Params tab:
   - Add `limit` = `20`
   - Add `category` = `tech` (optional)
   - Add `days` = `7` (optional)
4. Send

---

### 6. Manual RSS Fetch
**POST** `{{base_url}}/api/feeds/fetch`

**Description:** Manually trigger RSS fetching for all active feeds

**Headers:**
| Key | Value |
|-----|-------|
| `X-API-Token` | `{{api_token}}` |

**Body:** None

**Example Response:**
```json
{
    "message": "RSS fetch completed",
    "total_feeds": 4,
    "total_articles": 20,
    "failed_feeds": 0
}
```

**Postman Setup:**
1. Method: `POST`
2. URL: `{{base_url}}/api/feeds/fetch`
3. Headers tab:
   - Add `X-API-Token`: `{{api_token}}`
4. Send (note: this may take 10-30 seconds)

---

## 🔐 Authentication Setup

If your server has `API_TOKEN` configured, you need to include it in protected endpoints.

### Option 1: Manual Header

Add this header to protected requests:
```
X-API-Token: your-actual-token-here
```

### Option 2: Environment Variable (Recommended)

1. Set up environment variable `api_token` with your token
2. In request headers, use:
   ```
   X-API-Token: {{api_token}}
   ```

### Option 3: Authorization Tab

1. Go to Authorization tab
2. Type: `API Key`
3. Add to: `Header`
4. Header name: `X-API-Token`
5. Value: `{{api_token}}`

---

## 📦 Postman Collection

Here's a complete Postman collection you can import:

```json
{
    "info": {
        "name": "AI-RSS-Hub API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Health Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/health",
                    "host": ["{{base_url}}"],
                    "path": ["api", "health"]
                }
            }
        },
        {
            "name": "System Status",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/status",
                    "host": ["{{base_url}}"],
                    "path": ["api", "status"]
                }
            }
        },
        {
            "name": "Get All Feeds",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/feeds",
                    "host": ["{{base_url}}"],
                    "path": ["api", "feeds"]
                }
            }
        },
        {
            "name": "Get Active Feeds Only",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/feeds?active_only=true",
                    "host": ["{{base_url}}"],
                    "path": ["api", "feeds"],
                    "query": [
                        {
                            "key": "active_only",
                            "value": "true"
                        }
                    ]
                }
            }
        },
        {
            "name": "Get Articles",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/articles?limit=20",
                    "host": ["{{base_url}}"],
                    "path": ["api", "articles"],
                    "query": [
                        {
                            "key": "limit",
                            "value": "20"
                        }
                    ]
                }
            }
        },
        {
            "name": "Get Tech Articles",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/articles?category=tech&limit=20",
                    "host": ["{{base_url}}"],
                    "path": ["api", "articles"],
                    "query": [
                        {
                            "key": "category",
                            "value": "tech"
                        },
                        {
                            "key": "limit",
                            "value": "20"
                        }
                    ]
                }
            }
        },
        {
            "name": "Add New Feed",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    },
                    {
                        "key": "X-API-Token",
                        "value": "{{api_token}}"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"name\": \"My Tech Blog\",\n    \"url\": \"https://example.com/feed.xml\",\n    \"category\": \"tech\",\n    \"is_active\": true\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/feeds",
                    "host": ["{{base_url}}"],
                    "path": ["api", "feeds"]
                }
            }
        },
        {
            "name": "Manual Fetch",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "X-API-Token",
                        "value": "{{api_token}}"
                    }
                ],
                "url": {
                    "raw": "{{base_url}}/api/feeds/fetch",
                    "host": ["{{base_url}}"],
                    "path": ["api", "feeds", "fetch"]
                }
            }
        }
    ]
}
```

### Import Instructions:
1. Copy the JSON above
2. In Postman: Import → Paste Raw Text
3. Save the collection
4. Set up your environment variables
5. Start making requests!

---

## 🧪 Testing Workflow

### Quick Test (No Auth Required)

1. **Health Check**
   ```
   GET {{base_url}}/api/health
   ```
   Expected: `200 OK` with `"status": "ok"`

2. **Get Feeds**
   ```
   GET {{base_url}}/api/feeds
   ```
   Expected: Array of feed objects

3. **Get Articles**
   ```
   GET {{base_url}}/api/articles?limit=5
   ```
   Expected: Array of article objects

### Admin Operations (Requires API Token)

If you have configured `API_TOKEN` in the server's `.env`:

1. **Add Feed**
   ```
   POST {{base_url}}/api/feeds
   Headers: X-API-Token: {{api_token}}
   Body: {
     "name": "Test Feed",
     "url": "https://example.com/feed.xml",
     "category": "test"
   }
   ```

2. **Manual Fetch**
   ```
   POST {{base_url}}/api/feeds/fetch
   Headers: X-API-Token: {{api_token}}
   ```
   Expected: Fetch result with article counts

---

## 🐛 Common Issues

### Issue 1: Connection Refused
**Error:** `Could not get any response`
**Solution:**
- Check server is running: `curl http://8.134.202.27:8000/api/health`
- Check firewall settings on server
- Verify port 8000 is open

### Issue 2: 403 Forbidden
**Error:** `"detail": "API Token 无效"` or similar
**Solution:**
- Add `X-API-Token` header with correct token
- Or disable auth by removing `API_TOKEN` from server's `.env`

### Issue 3: 422 Validation Error
**Error:** Validation error when adding feed
**Solution:**
- Check URL format is valid
- Ensure all required fields are present (name, url)
- Check category is not too long

### Issue 4: Timeout on Manual Fetch
**Error:** Request timeout when fetching
**Solution:**
- Increase timeout in Postman settings
- Manual fetch can take 10-30 seconds for multiple feeds
- Check server logs for errors

---

## 📊 Response Examples

### Success Response (200)
```json
{
    "status": "ok",
    "message": "AI-RSS-Hub is running"
}
```

### Error Response (403)
```json
{
    "detail": "API Token 无效"
}
```

### Error Response (422)
```json
{
    "detail": [
        {
            "loc": ["body", "url"],
            "msg": "URL格式不正确",
            "type": "value_error"
        }
    ]
}
```

---

## 🎯 Quick Start Checklist

- [ ] Install Postman
- [ ] Create environment `AI-RSS-Hub`
- [ ] Add variable `base_url` = `http://8.134.202.27:8000`
- [ ] Add variable `api_token` (if needed)
- [ ] Import the collection (optional)
- [ ] Test health check: `GET {{base_url}}/api/health`
- [ ] Test get feeds: `GET {{base_url}}/api/feeds`
- [ ] Test get articles: `GET {{base_url}}/api/articles?limit=10`
- [ ] Try adding a feed (with token): `POST {{base_url}}/api/feeds`

---

## 📖 Additional Resources

- **Interactive API Docs:** http://8.134.202.27:8000/docs
- **ReDoc:** http://8.134.202.27:8000/redoc
- **Client Usage Guide:** `CLIENT_USAGE_GUIDE.md`
- **Python Client:** `rss_client.py`

---

**Last Updated:** 2026-01-03
**Server URL:** http://8.134.202.27:8000
