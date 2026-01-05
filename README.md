# AI-RSS-Hub

> 🤖 Intelligent RSS Aggregation System with AI-Powered Summaries

---

## 📖 What is AI-RSS-Hub?

AI-RSS-Hub is an intelligent RSS feed aggregator that automatically fetches RSS feeds and uses AI to generate concise article summaries. Built with FastAPI and SQLModel, it provides a robust RESTful API for managing feeds and articles.

### ✨ Key Features

- 📡 **Automatic RSS Fetching** - Scheduled feed fetching (configurable interval)
- 🤖 **AI-Powered Summaries** - Automatic article summarization using LLM APIs
- 🔒 **Security First** - API token authentication, rate limiting, input validation
- 🚀 **Production Ready** - systemd service support, auto-restart, logging
- 🌐 **Multi-LLM Support** - OpenAI, DeepSeek, Gemini, and more
- 📊 **RESTful API** - Complete API for client integration
- 📅 **Date Filtering** - Query articles by specific date or date ranges (NEW!)
- 📈 **API Monitoring** - Built-in request tracking and statistics (NEW!)
- 🌍 **Bilingual Summaries** - Chinese and English summaries for language learning

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/goodniuniu/AI-RSS-Hub.git
cd AI-RSS-Hub

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/env/.env.example .env
# Edit .env and add your API keys
```

### Configuration

Edit `.env` file with your settings:

```bash
# Required
OPENAI_API_KEY=your_api_key_here
API_TOKEN=your_secure_token_here

# Optional
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
FETCH_INTERVAL_HOURS=1
```

### Run the Application

```bash
# Development mode
./scripts/dev/start.sh

# Or manually
python -m app.main
```

The API will be available at: `http://localhost:8000`

- 📖 API Documentation: http://localhost:8000/docs
- 💚 Health Check: http://localhost:8000/api/health
- 📊 System Status: http://localhost:8000/api/status

---

## 📚 Documentation

### For Users

| Document | Description |
|----------|-------------|
| [📖 Setup Guide](docs/guides/SETUP.md) | Complete setup instructions |
| [🚀 Auto-Start Guide](docs/deployment/AUTO_START_GUIDE.md) | Deploy with systemd (auto-start on boot) |
| [✅ Reboot Test Guide](docs/deployment/REBOOT_TEST_GUIDE.md) | Verify auto-start configuration |

### For Developers

| Document | Description |
|----------|-------------|
| [🔧 API Reference](docs/api/API_GUIDE.md) | Complete API documentation for client development |
| [💻 Client Usage Guide](docs/guides/CLIENT_USAGE_GUIDE.md) | How to use the API |
| [⚡ Quick Start for Clients](docs/guides/QUICK_START_CLIENT.md) | Fast-track client integration |
| [📮 Postman Collection](docs/guides/POSTMAN_GUIDE.md) | API testing with Postman |
| [📅 Date Filtering Guide](docs/API_DATE_FILTERING_GUIDE.md) | **NEW**: Query articles by date and date ranges |
| [📊 API Monitoring Guide](docs/API_MONITORING_GUIDE.md) | **NEW**: Monitor API usage and performance |
| [📝 Project Understanding](docs/development/PROJECT_UNDERSTANDING.md) | Architecture and design |
| [🔐 Security Guide](config/env/.env.security) | Security best practices |

### Additional Documentation

- [Reorganization Plan](REORGANIZATION_PLAN.md) - Project structure reorganization details
- [Legacy Docs](docs/legacy/) - Archived documentation

---

## 📁 Project Structure

```
AI-RSS-Hub/
├── app/                    # Core application
│   ├── api/               # API routes
│   ├── security/          # Security modules
│   ├── services/          # Business logic
│   └── main.py            # Application entry
├── docs/                  # 📚 All documentation
│   ├── api/              # API docs
│   ├── guides/           # User guides
│   ├── deployment/       # Deployment guides
│   └── development/      # Development docs
├── scripts/              # 🔧 Utility scripts
│   ├── service/         # Systemd service management
│   ├── deployment/      # Deployment scripts
│   ├── security/        # Security tools
│   └── dev/             # Development tools
├── utils/               # 🛠️ Python utilities
├── tests/               # ✅ Test files
├── config/              # ⚙️ Configuration files
│   ├── systemd/        # Service files
│   ├── postman/        # API collections
│   └── env/            # Environment templates
└── requirements.txt     # Python dependencies
```

---

## 🔧 Usage Examples

### Get Articles

```bash
# Get latest 10 articles
curl http://localhost:8000/api/articles?limit=10

# Get articles from a specific date (NEW!)
curl "http://localhost:8000/api/articles?date=2026-01-05"

# Get articles from a date range (NEW!)
curl "http://localhost:8000/api/articles?start_date=2026-01-01&end_date=2026-01-05"

# Get articles from the last 7 days
curl "http://localhost:8000/api/articles?days=7"
```

### Add RSS Feed (Requires Authentication)

```bash
curl -X POST http://localhost:8000/api/feeds \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your_token" \
  -d '{
    "name": "Tech Blog",
    "url": "https://example.com/feed",
    "category": "tech"
  }'
```

### Trigger Manual Fetch (Requires Authentication)

```bash
curl -X POST http://localhost:8000/api/feeds/fetch \
  -H "X-API-Token: your_token"
```

---

## 🌐 Bilingual Summaries

AI-RSS-Hub automatically generates **bilingual summaries** (Chinese and English) for all articles, making it perfect for language learning while consuming news.

### How It Works

1. **Automatic Generation**: When articles are fetched, the system generates summaries in both languages using a single LLM API call
2. **Language Learning**: Read Chinese summaries first, then English summaries to improve your English skills
3. **API Response**: Each article includes both `summary` (Chinese) and `summary_en` (English) fields

### Example Response

```json
{
  "id": 1,
  "title": "Show HN: I built a tool to...",
  "summary": "一位开发者分享了他构建的工具，该工具可以帮助开发者更高效地管理项目。",
  "summary_en": "A developer shared a tool they built to help developers manage projects more efficiently.",
  "link": "https://example.com/article",
  "feed_name": "Hacker News"
}
```

### Processing Historical Articles

If you have existing articles without English summaries, use the batch processing script:

```bash
# Test with 5 articles first
venv/bin/python scripts/dev/generate_english_summaries.py --limit=5

# Process all articles
venv/bin/python scripts/dev/generate_english_summaries.py

# With custom batch size (default: 3)
venv/bin/python scripts/dev/generate_english_summaries.py --batch-size=5
```

**Performance**:
- Average: 4.4 seconds per article
- Success rate: 99.6%
- Cost-effective: Single API call generates both summaries

---

## 🚀 Production Deployment

### Using systemd Service (Recommended)

```bash
# Install service
sudo bash scripts/service/install_service.sh

# Check status
sudo systemctl status ai-rss-hub

# View logs
sudo journalctl -u ai-rss-hub -f
```

See [Auto-Start Guide](docs/deployment/AUTO_START_GUIDE.md) for details.

---

## 🛠️ Development

### Running Tests

```bash
pytest

# With coverage
pytest --cov=app tests/
```

### Code Style

The project follows Python best practices:
- PEP 8 style guide
- Type hints for better code clarity
- Comprehensive docstrings
- Security-focused design

### Security Tools

```bash
# Generate secure API token
python scripts/security/generate_token.py

# Run security checks
bash scripts/security/check_security.sh
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🌟 Features in Detail

### Core Features
- **Automatic Fetching**: Scheduled RSS feed fetching with APScheduler
- **Bilingual AI Summaries**: LLM-powered article summarization in both Chinese and English (100 words each)
- **Data Persistence**: SQLite database (easy to switch to PostgreSQL)
- **RESTful API**: Complete API for feed and article management
- **Multi-LLM Support**: OpenAI, DeepSeek, Gemini, and compatible APIs

### Security Features
- **API Token Authentication**: Protect sensitive operations
- **Rate Limiting**: Prevent API abuse (configurable)
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, etc.
- **Input Validation**: URL format validation and data sanitization
- **Security Logging**: Track authentication failures and suspicious activity

### Production Features
- **Systemd Service**: Auto-start on boot, auto-restart on failure
- **Service Management**: Easy-to-use management scripts
- **Log Management**: Integrated with journalctl
- **Error Handling**: Comprehensive error handling and recovery

---

## 📊 Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel + SQLAlchemy
- **Database**: SQLite (switchable to PostgreSQL)
- **RSS Parser**: feedparser
- **LLM Client**: OpenAI (supports custom base_url)
- **Task Scheduler**: APScheduler
- **Security**: Bearer Token, slowapi
- **System Service**: systemd

---

## 📞 Support

- 🐛 [Report Issues](https://github.com/goodniuniu/AI-RSS-Hub/issues)
- 💬 [Discussions](https://github.com/goodniuniu/AI-RSS-Hub/discussions)
- 📧 Email: goodniuniu@users.noreply.github.com

---

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- OpenAI for LLM APIs
- The open-source community

---

**Built with ❤️ by [goodniuniu](https://github.com/goodniuniu)**

**Project Status**: ✅ Active | 🚀 Production Ready

---

*Last updated: 2026-01-04*
