# 文章二维码功能 API 说明书

## 功能概述

为每篇文章生成对应的二维码图片，扫码后可直接跳转至原文链接。专为墨水屏显示优化，采用黑白高对比度设计。

---

## API 接口变更

### 1. 文章列表接口

**端点**: `GET /api/articles`

**新增字段**:

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `qr_code_url` | string | 二维码图片URL | `/static/qrcodes/13827.png` |

**响应示例**:
```json
{
  "id": 13827,
  "title": "小竹无人车将完成独立融资，估值达数亿美金...",
  "link": "https://example.com/article",
  "summary": "文章摘要...",
  "qr_code_url": "/static/qrcodes/13827.png",
  "published_at": "2026-06-23T06:12:08",
  "feed_id": 6,
  "feed_name": "36Kr",
  "feed_category": "tech-china"
}
```

---

## 二维码图片访问

### 图片URL格式

**格式**: `/static/qrcodes/{article_id}.png`

**示例**:
- 文章ID: 13827
- 二维码URL: `http://8.134.202.27:8000/static/qrcodes/13827.png`

### 访问方式

```bash
# 直接访问
curl http://8.134.202.27:8000/static/qrcodes/13827.png

# 前端使用
<img src="http://8.134.202.27:8000/static/qrcodes/13827.png" alt="文章二维码" />
```

---

## 二维码规格

| 参数 | 数值 |
|------|------|
| 尺寸 | 200×200 像素 |
| 颜色 | 黑白（高对比度） |
| 容错级别 | L (约7%容错) |
| 边框 | 4模块 |
| 格式 | PNG |

### 墨水屏显示适配

- **高对比度**: 纯黑白设计，无灰度
- **适中尺寸**: 200×200px适合240×360分辨率屏幕
- **清晰边缘**: 优化二维码模块大小

---

## 前端集成示例

### Vue.js 组件示例

```vue
<template>
  <div class="article-card">
    <h2>{{ article.title }}</h2>
    <p class="summary">{{ article.summary }}</p>
    <div class="article-footer">
      <span class="source">{{ article.feed_name }}</span>
      <img 
        :src="qrCodeUrl" 
        class="qrcode" 
        @error="handleQRError"
        alt="扫码阅读全文"
      />
    </div>
  </div>
</template>

<script>
export default {
  props: ['article'],
  computed: {
    qrCodeUrl() {
      const baseUrl = 'http://8.134.202.27:8000';
      return this.article.qr_code_url 
        ? `${baseUrl}${this.article.qr_code_url}`
        : null;
    }
  },
  methods: {
    handleQRError() {
      console.error('二维码加载失败');
      // 可选：显示默认占位图
    }
  }
}
</script>

<style scoped>
.qrcode {
  width: 100px;
  height: 100px;
  image-rendering: pixelated; /* 墨水屏优化 */
  border: 1px solid #000;
}
</style>
```

### React 组件示例

```jsx
function ArticleCard({ article }) {
  const baseUrl = 'http://8.134.202.27:8000';
  
  return (
    <div className="article-card">
      <h2>{article.title}</h2>
      <p>{article.summary}</p>
      <div className="footer">
        <span className="source">{article.feed_name}</span>
        {article.qr_code_url && (
          <img 
            src={`${baseUrl}${article.qr_code_url}`}
            alt="扫码阅读全文"
            className="qrcode"
            onError={(e) => {
              console.error('二维码加载失败');
              e.target.style.display = 'none';
            }}
          />
        )}
      </div>
    </div>
  );
}
```

---

## 数据更新流程

### 新文章抓取

```
RSS抓取 → 创建文章 → 生成二维码 → 保存qr_code_url
```

1. RSS源定时抓取新文章
2. 文章保存到数据库
3. 自动生成二维码图片
4. 更新 `qr_code_url` 字段

### 现有文章补全

使用批量生成脚本：

```bash
# 为所有无二维码的文章生成
python utils/generate_qr_codes.py

# 限制数量测试
python utils/generate_qr_codes.py --limit 100

# 强制重新生成
python utils/generate_qr_codes.py --force
```

---

## 错误处理

### 二维码字段为空

**原因**:
- 文章创建于功能上线前
- 二维码生成失败

**处理**:
```javascript
if (article.qr_code_url) {
  // 显示二维码
} else {
  // 显示占位符或跳过
}
```

### 图片访问失败

**处理**:
```html
<img 
  src="{{ qrCodeUrl }}" 
  onerror="this.style.display='none'"
  alt="二维码不可用"
/>
```

---

## 注意事项

1. **URL拼接**: 二维码URL为相对路径，前端需拼接完整URL
2. **缓存策略**: 建议前端缓存二维码图片，减少请求
3. **错误处理**: 务必处理二维码加载失败的情况
4. **墨水屏优化**: 使用 `image-rendering: pixelated` 提升显示效果

---

## 联系支持

如有问题，请通过以下方式联系：
- GitHub Issues: https://github.com/goodniuniu/AI-RSS-Hub/issues
- API文档: http://8.134.202.27:8000/docs
