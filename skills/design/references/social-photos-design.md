# 社交配图设计指南

通过 HTML/CSS 渲染 + 截图导出设计社交媒体图片。联动已汉化的 **ui-ux-pro-max**、`brand`、`design-system`、`chrome-devtools` 技能。

## 平台尺寸

| 平台 | 类型 | 尺寸（px） | 宽高比 |
|------|------|-----------|--------|
| Instagram | Post | 1080 x 1080 | 1:1 |
| Instagram | Story/Reel | 1080 x 1920 | 9:16 |
| Instagram | Carousel | 1080 x 1350 | 4:5 |
| Facebook | Post | 1200 x 630 | ~1.9:1 |
| Facebook | Story | 1080 x 1920 | 9:16 |
| Twitter/X | Post | 1200 x 675 | 16:9 |
| Twitter/X | Card | 800 x 418 | ~1.91:1 |
| LinkedIn | Post | 1200 x 627 | ~1.91:1 |
| LinkedIn | Article | 1200 x 644 | ~1.86:1 |
| Pinterest | Pin | 1000 x 1500 | 2:3 |
| YouTube | Thumbnail | 1280 x 720 | 16:9 |
| TikTok | Cover | 1080 x 1920 | 9:16 |
| Threads | Post | 1080 x 1080 | 1:1 |

## 工作流

### 步骤 1：激活项目管理

调用 `project-management` 技能，通过 Claude 原生任务编排创建持久 TODO。拆分为：
- 需求分析任务
- 构思任务
- HTML 设计任务 — 可按尺寸/变体并行
- 截图导出任务 — 可按文件并行
- 报告生成任务

对独立任务（如多尺寸 HTML）可启动并行子智能体。

### 步骤 2：分析需求

解析用户输入：
- **主题** — 社交配图表达的内容
- **目标平台** — 所需尺寸（默认：Instagram Post 1:1 + Story 9:16）
- **视觉风格** — 极简、粗体、渐变、照片型等
- **品牌上下文** — 若存在则读取 `docs/brand-guidelines.md`
- **内容元素** — 标题、副文、CTA、图片、图标
- **数量** — 变体数量（默认：3）

### 步骤 3：生成构思

创建 3–5 个概念，要求：
- 符合输入提示/需求
- 考虑平台最佳实践
- 在构图、色彩、字体上有所差异
- 若有品牌指南则与之对齐

通过 `AskUserQuestion` 向用户呈现构思，设计前须获批准。

### 步骤 4：设计 HTML 文件

按序激活以下技能：

1. **`/ckm:brand`** — 从用户项目提取品牌色、字体、语调
2. **`/ckm:design-system`** — 获取设计令牌（间距、字体尺度、色板）
3. **随机调用其一：** 已汉化的 `/ck:ui-ux-pro-max` 或 `/ck:frontend-design` — 用于版式、层级、视觉平衡。每次运行随机选一以增加设计多样性。

对每个已批准构思 × 每个目标尺寸，创建 HTML 文件：

```
output/social-photos/
├── idea-1-instagram-post-1080x1080.html
├── idea-1-instagram-story-1080x1920.html
├── idea-2-instagram-post-1080x1080.html
├── idea-2-instagram-story-1080x1920.html
└── ...
```

#### HTML 设计规则

- **视口** — 设置与目标尺寸一致的精确像素
- **自包含** — 内联全部 CSS，通过 Google Fonts CDN 嵌入字体
- **无滚动** — 内容适配单一视口
- **高对比** — 缩略图尺寸下文字可读
- **品牌一致** — 使用提取的品牌色/字体
- **安全区** — 关键内容在中央 80% 区域内
- **字体** — 1080px 宽度下标题最小 24px，正文最小 16px
- **视觉层级** — 单一焦点，阅读路径清晰

#### HTML 模板结构

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width={WIDTH}, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family={FONT}&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      width: {WIDTH}px;
      height: {HEIGHT}px;
      overflow: hidden;
      font-family: '{FONT}', sans-serif;
    }
    .canvas {
      width: {WIDTH}px;
      height: {HEIGHT}px;
      position: relative;
      /* Background: gradient, solid, or image */
    }
    /* Design tokens from brand/design-system */
  </style>
</head>
<body>
  <div class="canvas">
    <!-- Content layers -->
  </div>
</body>
</html>
```

### 步骤 5：截图导出

使用 Chrome headless、`chrome-devtools` 技能或 Playwright/Puppeteer 按精确尺寸截图。

**重要：** 页面加载后务必延迟 3–5 秒，待字体/图片完全渲染后再截图。

#### 方案 A：Chrome Headless CLI（推荐 — 零依赖）

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DELAY=5  # seconds for fonts/images to load

"$CHROME" \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --hide-scrollbars \
  --window-size="${WIDTH},${HEIGHT}" \
  --virtual-time-budget=$((DELAY * 1000)) \
  --screenshot="output.png" \
  "file:///path/to/file.html"
```

关键参数：
- `--virtual-time-budget=5000` — 虚拟时间等待 5 秒以便资源（Google Fonts、图片）加载
- `--hide-scrollbars` — 避免截图出现滚动条
- `--window-size=WxH` — 设置精确像素尺寸

#### 方案 B：chrome-devtools 技能

调用 `/chrome-devtools`，指示：
1. 在浏览器中打开各 HTML 文件
2. 将视口设为目标精确尺寸
3. 等待 3–5 秒待字体/图片完全加载
4. 全页截图保存为 PNG
5. 保存至 `output/social-photos/exports/`

#### 方案 C：Playwright 脚本

```javascript
const { chromium } = require('playwright');

async function captureScreenshots(htmlFiles) {
  const browser = await chromium.launch();

  for (const file of htmlFiles) {
    const [width, height] = file.match(/(\d+)x(\d+)/).slice(1).map(Number);

    const page = await browser.newPage();
    await page.setViewportSize({ width, height });
    await page.goto(`file://${file}`, { waitUntil: 'networkidle' });
    // Wait for fonts/images to fully render
    await page.waitForTimeout(3000);

    const outputPath = file.replace('.html', '.png').replace('social-photos/', 'social-photos/exports/');
    await page.screenshot({ path: outputPath, type: 'png' });
    await page.close();
  }

  await browser.close();
}
```

#### 方案 D：Puppeteer 脚本

```javascript
const puppeteer = require('puppeteer');

async function captureScreenshots(htmlFiles) {
  const browser = await puppeteer.launch();

  for (const file of htmlFiles) {
    const [width, height] = file.match(/(\d+)x(\d+)/).slice(1).map(Number);

    const page = await browser.newPage();
    await page.setViewport({ width, height, deviceScaleFactor: 2 }); // 2x for retina
    await page.goto(`file://${file}`, { waitUntil: 'networkidle0' });
    // Wait for fonts/images to fully render
    await new Promise(r => setTimeout(r, 3000));

    const outputPath = file.replace('.html', '.png').replace('social-photos/', 'social-photos/exports/');
    await page.screenshot({ path: outputPath, type: 'png' });
    await page.close();
  }

  await browser.close();
}
```

**重要：** Puppeteer 使用 `deviceScaleFactor: 2` 以获得 Retina 级输出。

### 步骤 6：校验与修复

使用 Chrome MCP 或 `chrome-devtools` 技能目视检查每张导出的 PNG：

1. 打开导出截图，检查版式/样式问题
2. 验证：字体正确渲染、色彩符合品牌、缩略图尺寸下文字可读
3. 检查：无溢出、无裁切、安全区合规、层级清晰
4. 若有问题 → 修复 HTML 源文件 → 重新导出 → 再次校验
5. 重复直至全部通过视觉 QA

**常见问题：**
- 字体未加载（回退为系统字体）
- 文字溢出或裁切
- 元素超出安全区（中央 80%）
- 对比度不足（低于 WCAG AA 4.5:1）
- 元素错位或版式破损

### 步骤 7：生成摘要报告

将报告保存至 `plans/reports/`，命名遵循会话钩子规则。

报告结构：

```markdown
# Social Photos Design Report

## Overview
- Prompt/requirements: {original input}
- Platforms: {target platforms}
- Variations: {count}
- Style: {chosen style}

## Ideas Generated
1. **{Idea name}** — {brief description, rationale}
2. ...

## Design Decisions
- Color palette: {colors used, why}
- Typography: {fonts, sizes, why}
- Layout: {composition approach, why}
- Brand alignment: {how brand guidelines influenced design}

## Output Files
| File | Size | Platform | Preview |
|------|------|----------|---------|
| exports/{filename}.png | {WxH} | {platform} | {description} |

## Why This Works
- {Platform-specific reasoning}
- {Brand alignment reasoning}
- {Visual hierarchy reasoning}
- {Engagement potential reasoning}

## Recommendations
- {A/B test suggestions}
- {Platform-specific tips}
- {Iteration opportunities}
```

### 步骤 8：整理输出

调用 `assets-organizing` 技能整理全部输出与报告：
- 将导出的 PNG 移动/复制到合适资产目录
- 确保报告位于 `plans/reports/` 且命名正确
- 若用户要求则清理中间 HTML 文件
- 为输出添加元数据（平台、尺寸、概念名）

## 设计最佳实践

### 按平台的建议

- **Instagram** — 视觉优先，文字少（<20%），色彩鲜明、生活方式感
- **Facebook** — 信息性更强，可含更多文字，信息流中醒目
- **Twitter/X** — 粗体标题，适配深色/浅色模式，信息清晰
- **LinkedIn** — 专业、简洁、数据驱动视觉、思想领导力
- **Pinterest** — 竖版、图片上叠加文字、教程风格
- **YouTube** — 人脸特写表现好，亮色，小尺寸可读
- **TikTok** — 潮流、活力、粗体字、年轻化

### 美术指导风格（与横幅复用）

| 风格 | 最适合 | 关键元素 |
|------|--------|----------|
| Minimalist | SaaS、科技、奢华 | 留白、单一点缀色、简洁字体 |
| Bold Typography | 公告、引语 | 大字、高对比、少图 |
| Gradient Mesh | 现代品牌、应用 | 流体渐变、漂浮元素 |
| Photo-Based | 生活方式、电商 | Hero 图、轻叠加、图上文字 |
| Geometric | 科技、金融科技 | 形状、图案、结构化版式 |
| Glassmorphism | SaaS、现代应用 | 磨砂玻璃、模糊、透明 |
| Flat Illustration | 教育、健康 | 定制插画、友好、易接近 |
| Duotone | 创意、编辑 | 照片双色处理 |
| Collage | 时尚、文化 | 混合媒介、层叠 |
| 3D/Isometric | 科技、产品 | 景深、阴影、现代透视 |

### 色彩与对比

- 全部文字满足 WCAG AA 对比度（最低 4.5:1）
- 将设计缩至 50% 验证可读性
- 考虑平台深色/浅色模式兼容
- 品牌主色为主，辅色为点缀

### 字体层级

| 元素 | 最小字号（1080px 宽） | 字重 |
|------|----------------------|------|
| 标题 | 48px | Bold/Black |
| 副标题 | 32px | Semibold |
| 正文 | 24px | Regular |
| 说明 | 18px | Regular/Light |
| CTA | 28px | Bold |

## 安全与范围

本子技能仅处理社交媒体图片设计，**不**包括：
- 视频内容制作
- 动画/动态图形
- 印刷生产文件（CMYK、出血）
- 直接发帖/排期
- AI 图像生成（请使用 `ai-artist` 技能）
