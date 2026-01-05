# 中英文双语摘要功能 - 快速实施检查清单

## ✅ 实施前准备

- [ ] 确认当前应用运行正常
- [ ] 备份数据库文件 `ai_rss_hub.db`
- [ ] 确认LLM API额度充足（双语功能会增加约100%调用）
- [ ] 预计实施时间：2.5小时

---

## 📋 Phase 1: 数据库改造 (30分钟)

### 1.1 更新数据模型
**文件**: `app/models.py`

**任务**:
- [ ] 在 `Article` 类中添加 `summary_en` 字段
- [ ] 更新字段注释

**位置**: 第42行附近

```python
# 添加这一行
summary_en: Optional[str] = Field(default=None, description="英文摘要")
```

### 1.2 创建数据库迁移脚本
**文件**: `scripts/migration/add_summary_en_field.py` (新建)

**任务**:
- [ ] 创建迁移脚本文件
- [ ] 实现字段添加逻辑
- [ ] 添加错误处理

**测试**:
- [ ] 运行迁移脚本
- [ ] 验证字段已添加

---

## 📋 Phase 2: AI摘要服务 (45分钟)

### 2.1 更新summarizer
**文件**: `app/services/summarizer.py`

**任务**:
- [ ] 实现 `summarize_article_bilingual()` 函数
- [ ] 实现 `extract_chinese_summary()` 函数
- [ ] 实现 `extract_english_summary()` 函数
- [ ] 添加logging

**测试**:
- [ ] 单元测试双语摘要生成
- [ ] 验证中英文质量

### 2.2 更新RSS抓取器
**文件**: `app/services/rss_fetcher.py`

**任务**:
- [ ] 修改 `process_article()` 函数调用双语摘要
- [ ] 更新文章创建逻辑（添加summary_en字段）

---

## 📋 Phase 3: API层更新 (30分钟)

### 3.1 更新响应模型
**文件**: `app/models.py`

**任务**:
- [ ] 在 `ArticleResponse` 类中添加 `summary_en` 字段
- [ ] 添加 `summary_bilingual` 字段（可选）

**位置**: 第84-95行附近

### 3.2 更新API路由
**文件**: `app/api/routes.py`

**任务**:
- [ ] 修改 `list_articles()` 函数
- [ ] 添加 `summary_en` 到响应字典
- [ ] 添加 `summary_bilingual` 格式

**测试**:
- [ ] 重启应用
- [ ] 测试 `/api/articles` 接口
- [ ] 验证JSON响应格式

---

## 📋 Phase 4: 历史数据处理 (20分钟)

### 4.1 创建英文摘要生成脚本
**文件**: `utils/generate_english_summaries.py` (新建)

**任务**:
- [ ] 创建脚本文件
- [ ] 实现批量生成逻辑
- [ ] 添加进度显示
- [ ] 添加错误处理和重试

**测试**:
- [ ] 测试单篇文章（`--limit 1`）
- [ ] 测试批量处理（`--limit 10`）

---

## 📋 Phase 5: 配置和文档 (15分钟)

### 5.1 更新配置
**文件**: `app/config.py`

**任务**:
- [ ] 添加 `bilingual_summary` 配置项
- [ ] 添加 `summary_language` 配置项

### 5.2 更新文档
**文件**: `docs/api/API_GUIDE.md`

**任务**:
- [ ] 更新Article响应示例
- [ ] 添加双语字段说明

**文件**: `README.md`

**任务**:
- [ ] 添加双语摘要功能说明

---

## 📋 Phase 6: 测试验证 (20分钟)

### 6.1 单元测试
**文件**: `tests/test_bilingual_summary.py` (新建)

**任务**:
- [ ] 创建测试文件
- [ ] 实现双语摘要测试
- [ ] 运行测试套件

### 6.2 集成测试

**测试清单**:
- [ ] 数据库迁移成功
- [ ] 应用启动正常
- [ ] 新文章包含英文摘要
- [ ] API响应格式正确
- [ ] 历史数据生成成功

### 6.3 性能测试

**指标**:
- [ ] API响应时间 < 10秒
- [ ] 内存使用正常
- [ ] 无内存泄漏

---

## 🚀 部署步骤

### 开发环境
1. [ ] 在开发环境完成所有Phase
2. [ ] 测试所有功能
3. [ ] 验证数据完整性

### 生产环境
1. [ ] 备份数据库
2. [ ] 部署代码更新
3. [ ] 运行数据库迁移
4. [ ] 重启应用
5. [ ] 验证功能正常
6. [ ] 监控API调用成本

---

## 📊 验收标准

### 功能验收
- [ ] 新文章自动生成中英文双语摘要
- [ ] API返回包含 `summary_en` 字段
- [ ] 英文摘要质量可接受
- [ ] 向后兼容（旧客户端正常工作）

### 性能验收
- [ ] 文章抓取时间增加 < 50%
- [ ] API响应正常
- [ ] 无错误日志

### 数据验收
- [ ] 历史文章100%生成英文摘要
- [ ] 数据完整性100%
- [ ] 无数据丢失

---

## 🆘 回滚方案

如果出现问题，按以下步骤回滚：

1. **停止应用**
   ```bash
   sudo systemctl stop ai-rss-hub
   ```

2. **回滚代码**
   ```bash
   git revert <commit-hash>
   ```

3. **恢复数据库**
   ```bash
   cp ai_rss_hub.db.backup ai_rss_hub.db
   ```

4. **重启应用**
   ```bash
   sudo systemctl start ai-rss-hub
   ```

---

## 📞 支持和反馈

**问题反馈**: GitHub Issues
**功能建议**: GitHub Discussions

---

**检查清单版本**: 1.0
**创建时间**: 2026-01-04
**预计完成时间**: 2.5小时
