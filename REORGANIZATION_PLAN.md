# AI-RSS-Hub Reorganization Plan

## Current Issues

1. **Cluttered Root Directory**: 26+ loose files in root
2. **Scattered Documentation**: 11 .md files mixed with code
3. **Scripts Not Organized**: 6 shell scripts scattered
4. **Utility Files Misplaced**: Python utilities in root
5. **Inconsistent Naming**: Mix of English and Chinese file names
6. **Temporary Files**: Development notes in production directory

## Proposed Directory Structure

```
AI-RSS-Hub/
├── app/                          # Core application code ✅ (Already good)
│   ├── api/                      # API routes
│   ├── security/                 # Security modules
│   ├── services/                 # Business logic
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Configuration management
│   ├── crud.py                   # Database operations
│   ├── database.py               # Database connection
│   ├── models.py                 # Data models
│   └── scheduler.py              # Task scheduler
│
├── docs/                         # 📚 All documentation (NEW)
│   ├── api/                      # API documentation
│   │   └── API_GUIDE.md          # Complete API reference
│   ├── guides/                   # User and developer guides
│   │   ├── README.md             # Main project README
│   │   ├── SETUP.md              # Setup guide
│   │   ├── CLIENT_USAGE_GUIDE.md # Client usage
│   │   ├── QUICK_START_CLIENT.md # Quick start
│   │   └── POSTMAN_GUIDE.md      # Postman collection guide
│   ├── deployment/               # Deployment documentation
│   │   ├── AUTO_START_GUIDE.md   # Auto-start setup
│   │   └── REBOOT_TEST_GUIDE.md  # Reboot testing
│   ├── development/              # Development documentation
│   │   ├── PROJECT_UNDERSTANDING.md
│   │   └── 开发部署隔离方案.md
│   └── legacy/                   # Legacy/Archived docs
│       ├── 2025-12-25-项目说明文档.md
│       ├── next-20251225.txt
│       ├── 项目文件清单.md
│       ├── 项目运行状态记录.md
│       └── 测试部署文件说明.txt
│
├── scripts/                      # 🔧 Utility scripts (REORGANIZED)
│   ├── service/                  # Service management scripts
│   │   ├── install_service.sh    # Install systemd service
│   │   ├── manage_service.sh     # Service management tool
│   │   └── verify_after_reboot.sh # Verification script
│   ├── deployment/               # Deployment scripts
│   │   └── sync_to_deploy.sh     # Deploy to production
│   ├── security/                 # Security scripts (MOVED here)
│   │   ├── check_security.sh     # Security check
│   │   └── generate_token.py     # Token generator
│   └── dev/                      # Development scripts
│       ├── run.sh                # Quick dev run
│       └── start.sh              # Start with reload
│
├── utils/                        # 🛠️ Python utility modules (NEW)
│   ├── __init__.py
│   ├── rss_client.py             # RSS client utility
│   ├── regenerate_summaries.py   # Summary regeneration tool
│   └── example_usage.py          # Usage examples
│
├── tests/                        # ✅ Test files (Already good)
│   ├── __init__.py
│   ├── test_security.py
│   └── test_summarizer.py
│
├── config/                       # ⚙️ Configuration files (NEW)
│   ├── systemd/                  # Systemd service files
│   │   └── ai-rss-hub.service
│   ├── postman/                  # API testing collections
│   │   └── AI-RSS-Hub-Postman-Collection.postman_collection.json
│   └── env/                      # Environment templates
│       ├── .env.example
│       ├── .env.template
│       └── .env.security
│
├── .gitignore                    # ✅ Git ignore rules
├── requirements.txt              # ✅ Python dependencies
├── README.md                     # 📄 Main README (short, points to docs)
└── REORGANIZATION_PLAN.md        # This file
```

## File Migration Plan

### 1. Create New Directories

```bash
mkdir -p docs/{api,guides,deployment,development,legacy}
mkdir -p scripts/{service,deployment,security,dev}
mkdir -p utils
mkdir -p config/{systemd,postman,env}
```

### 2. Move Documentation Files

| From | To |
|------|-----|
| `API_GUIDE.md` | `docs/api/API_GUIDE.md` |
| `README.md` | `docs/guides/README.md` |
| `SETUP.md` | `docs/guides/SETUP.md` |
| `CLIENT_USAGE_GUIDE.md` | `docs/guides/CLIENT_USAGE_GUIDE.md` |
| `QUICK_START_CLIENT.md` | `docs/guides/QUICK_START_CLIENT.md` |
| `POSTMAN_GUIDE.md` | `docs/guides/POSTMAN_GUIDE.md` |
| `AUTO_START_GUIDE.md` | `docs/deployment/AUTO_START_GUIDE.md` |
| `REBOOT_TEST_GUIDE.md` | `docs/deployment/REBOOT_TEST_GUIDE.md` |
| `PROJECT_UNDERSTANDING.md` | `docs/development/PROJECT_UNDERSTANDING.md` |
| `开发部署隔离方案.md` | `docs/development/开发部署隔离方案.md` |
| `2025-12-25-项目说明文档.md` | `docs/legacy/2025-12-25-项目说明文档.md` |
| `next-20251225.txt` | `docs/legacy/next-20251225.txt` |
| `项目文件清单.md` | `docs/legacy/项目文件清单.md` |
| `项目运行状态记录.md` | `docs/legacy/项目运行状态记录.md` |
| `测试部署文件说明.txt` | `docs/legacy/测试部署文件说明.txt` |

### 3. Move Script Files

| From | To |
|------|-----|
| `install_service.sh` | `scripts/service/install_service.sh` |
| `manage_service.sh` | `scripts/service/manage_service.sh` |
| `verify_after_reboot.sh` | `scripts/service/verify_after_reboot.sh` |
| `sync_to_deploy.sh` | `scripts/deployment/sync_to_deploy.sh` |
| `run.sh` | `scripts/dev/run.sh` |
| `start.sh` | `scripts/dev/start.sh` |
| `scripts/check_security.sh` | `scripts/security/check_security.sh` |
| `scripts/generate_token.py` | `scripts/security/generate_token.py` |

### 4. Move Python Utilities

| From | To |
|------|-----|
| `rss_client.py` | `utils/rss_client.py` |
| `regenerate_summaries.py` | `utils/regenerate_summaries.py` |
| `example_usage.py` | `utils/example_usage.py` |
| `test_setup.py` | `tests/test_setup.py` |

### 5. Move Configuration Files

| From | To |
|------|-----|
| `ai-rss-hub.service` | `config/systemd/ai-rss-hub.service` |
| `AI-RSS-Hub-Postman-Collection.postman_collection.json` | `config/postman/AI-RSS-Hub-Postman-Collection.postman_collection.json` |
| `.env.example` | `config/env/.env.example` |
| `.env.template` | `config/env/.env.template` |
| `.env.security` | `config/env/.env.security` |

### 6. Create New README

Create a concise main `README.md` in root that:
- Provides project overview
- Quick start instructions
- Links to detailed documentation in `docs/`

### 7. Update .gitignore

Add patterns to ignore:
- `__pycache__/` (should already be there)
- `*.pyc`
- `.pytest_cache/`
- `ai_rss_hub.db*`
- `config/env/.env` (actual env file)

## Benefits

✅ **Cleaner Root Directory**: Only essential files in root
✅ **Logical Organization**: Files grouped by purpose
✅ **Better Discoverability**: Easy to find what you need
✅ **Professional Structure**: Follows Python best practices
✅ **Scalability**: Easy to add new files
✅ **Separation of Concerns**: Docs, scripts, utils separated
✅ **Legacy Archive**: Old documents preserved but out of the way

## Post-Reorganization Tasks

1. Update all script references
2. Update documentation with new paths
3. Update service file paths
4. Test all scripts after moving
5. Update import statements in Python files
6. Verify git tracking status

## Execution Checklist

- [ ] Create new directory structure
- [ ] Move documentation files
- [ ] Move script files
- [ ] Move utility files
- [ ] Move configuration files
- [ ] Create new main README
- [ ] Update .gitignore
- [ ] Update script file references
- [ ] Update service file paths
- [ ] Test all functionality
- [ ] Commit changes

## Notes

- This reorganization maintains backward compatibility for the app code
- Scripts will need to be updated with correct paths
- Documentation will need path updates
- Git will track the moves (no history lost)
- Consider creating a migration script for automation
