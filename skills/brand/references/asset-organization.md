# 资产组织指南

营销资产结构化、可检索管理的规范。

## 目录结构

```
project-root/
├── .assets/                          # Git-tracked metadata
│   ├── manifest.json                 # Central asset registry
│   ├── tags.json                     # Tagging system
│   ├── versions/                     # Version history
│   │   └── {asset-id}/
│   │       └── v{n}.json
│   └── metadata/                     # Type-specific metadata
│       ├── designs.json
│       ├── banners.json
│       ├── logos.json
│       └── videos.json
├── assets/                           # Raw files
│   ├── designs/
│   │   ├── campaigns/                # Campaign-specific designs
│   │   ├── web/                      # Website graphics
│   │   └── print/                    # Print materials
│   ├── banners/
│   │   ├── social-media/             # Platform banners
│   │   ├── email-headers/            # Email template headers
│   │   └── landing-pages/            # Hero/section images
│   ├── logos/
│   │   ├── full-horizontal/          # Full logo with wordmark
│   │   ├── icon-only/                # Symbol only
│   │   ├── monochrome/               # Single color versions
│   │   └── variations/               # Special versions
│   ├── videos/
│   │   ├── ads/                      # Promotional videos
│   │   ├── tutorials/                # How-to content
│   │   └── testimonials/             # Customer videos
│   ├── infographics/                 # Data visualizations
│   └── generated/                    # AI-generated assets
│       └── {YYYYMMDD}/               # Date-organized
```

## 命名规范

### 格式
```
{type}_{campaign}_{description}_{timestamp}_{variant}.{ext}
```

### 组成部分
| 组成部分 | 格式 | 必填 | 示例 |
|----------|------|------|------|
| type | lowercase | 是 | banner, logo, design, video |
| campaign | kebab-case | 是* | claude-launch, q1-promo, evergreen |
| description | kebab-case | 是 | hero-image, email-header |
| timestamp | YYYYMMDD | 是 | 20251209 |
| variant | kebab-case | 否 | dark-mode, 1x1, mobile |

*非 campaign 资产使用 "evergreen"

### 示例
```
banner_claude-launch_hero-image_20251209_16-9.png
logo_brand-refresh_horizontal-full-color_20251209.svg
design_holiday-campaign_email-hero_20251209_dark-mode.psd
video_product-demo_feature-walkthrough_20251209.mp4
infographic_evergreen_pricing-comparison_20251209.png
```

## 元数据模式

### 资产条目（manifest.json）
```json
{
  "id": "uuid-v4",
  "name": "Campaign Hero Banner",
  "type": "banner",
  "path": "assets/banners/landing-pages/banner_claude-launch_hero-image_20251209.png",
  "dimensions": { "width": 1920, "height": 1080 },
  "fileSize": 245760,
  "mimeType": "image/png",
  "tags": ["campaign", "hero", "launch"],
  "status": "approved",
  "source": {
    "model": "imagen-4",
    "prompt": "...",
    "createdAt": "2025-12-09T10:30:00Z"
  },
  "version": 2,
  "createdBy": "agent:content-creator",
  "approvedBy": "user:john",
  "approvedAt": "2025-12-09T14:00:00Z"
}
```

### 版本条目（versions/{id}/v{n}.json）
```json
{
  "version": 2,
  "previousVersion": 1,
  "path": "assets/banners/landing-pages/banner_claude-launch_hero-image_20251209_v2.png",
  "changes": "Updated CTA button color to match brand refresh",
  "createdAt": "2025-12-09T12:00:00Z",
  "createdBy": "agent:ui-designer"
}
```

## 标签体系

### 标准标签
| 类别 | 取值 |
|------|------|
| status | draft, review, approved, archived |
| platform | instagram, twitter, linkedin, facebook, youtube, email, web |
| content-type | promotional, educational, brand, product, testimonial |
| format | 1x1, 4x5, 9x16, 16x9, story, reel, banner |
| source | imagen-4, veo-3, user-upload, canva, figma |

### 标签用法
- 每项资产应包含：status + platform + content-type
- 可选：format、source、campaign

## 文件组织最佳实践

1. **一文件一变体** — 明暗模式分文件存放
2. **源文件分离** — .psd / .fig 保持相同目录结构
3. **AI 资产按日期** — 按生成日期自动归档
4. **归档而非删除** — 移入 `archived/` 并加日期前缀
5. **大文件外置** — 视频超过 100MB 使用云存储链接

## 检索模式

### 按类型
```bash
# Find all banners
ls assets/banners/**/*
```

### 按 campaign
```bash
# Find all assets for specific campaign
grep -l "claude-launch" .assets/manifest.json
```

### 按状态
```bash
# Find approved assets only
jq '.assets[] | select(.status == "approved")' .assets/manifest.json
```

## 清理工作流

1. 对新资产运行 `extract-colors.cjs`
2. 对照品牌指南校验
3. 在 manifest.json 中新增条目
4. 打标签
5. 移除重复 / 过时版本
