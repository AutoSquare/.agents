---
name: ckm:design
description: "综合设计技能：品牌识别、设计令牌、UI 样式、Logo 生成（55 种风格，Gemini AI）、企业识别系统 CIP（50 项交付物与样机）、HTML 演示文稿（Chart.js）、横幅设计（22 种风格，社交/广告/网页/印刷）、图标设计（15 种风格，SVG，Gemini 3.1 Pro）、社交配图（HTML→截图，多平台）。操作：设计 Logo、创建 CIP、生成样机、制作幻灯片、设计横幅、生成图标、制作社交配图、品牌识别、设计系统。平台：Facebook、Twitter、LinkedIn、YouTube、Instagram、Pinterest、TikTok、Threads、Google Ads。"
argument-hint: "[设计类型] [上下文]"
license: MIT
metadata:
  author: claudekit
  version: "2.1.0"
---

# 设计

统一设计技能：品牌、令牌、UI、Logo、CIP、幻灯片、横幅、社交配图、图标。

## 适用场景

- 品牌识别、语调与资产
- 设计系统令牌与规格
- 基于 shadcn/ui + Tailwind 的 UI 样式
- Logo 设计与 AI 生成
- 企业识别系统（CIP）交付物
- 演示文稿与融资路演
- 社交媒体、广告、网页、印刷横幅设计
- Instagram、Facebook、LinkedIn、Twitter、Pinterest、TikTok 社交配图

## 子技能路由

| 任务 | 子技能 | 详情 |
|------|--------|------|
| 品牌识别、语调、资产 | `brand` | 外部技能 |
| 令牌、规格、CSS 变量 | `design-system` | 外部技能 |
| shadcn/ui、Tailwind、代码 | `ui-styling` | 外部技能 |
| Logo 创建、AI 生成 | Logo（内置） | `references/logo-design.md` |
| CIP 样机、交付物 | CIP（内置） | `references/cip-design.md` |
| 演示文稿、融资路演 | 幻灯片（内置） | `references/slides.md` |
| 横幅、封面、页眉 | 横幅（内置） | `references/banner-sizes-and-styles.md` |
| 社交媒体图片/配图 | 社交配图（内置） | `references/social-photos-design.md` |
| SVG 图标、图标集 | 图标（内置） | `references/icon-design.md` |

## Logo 设计（内置）

55+ 风格、30 套色板、25 个行业指南。Gemini Nano Banana 模型。

### Logo：生成设计简报

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\search.py" "tech startup modern" --design-brief -p "BrandName"
```

### Logo：检索风格/色彩/行业

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\search.py" "minimalist clean" --domain style
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\search.py" "tech professional" --domain color
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\search.py" "healthcare medical" --domain industry
```

### Logo：AI 生成

**务必**以白色背景输出 Logo 图像。

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\generate.py" --brand "TechFlow" --style minimalist --industry tech
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\generate.py" --prompt "coffee shop vintage badge" --style vintage
```

**重要：** 脚本失败时，应直接尝试修复脚本。

生成完成后，**务必**通过 `AskUserQuestion` 询问用户是否需要 HTML 预览。若需要，调用已汉化的 **ui-ux-pro-max** Skill 生成画廊。

## CIP 设计（内置）

50+ 交付物、20 种风格、20 个行业。Gemini Nano Banana（Flash/Pro）。

### CIP：生成简报

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "tech startup" --cip-brief -b "BrandName"
```

### CIP：检索领域

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "business card letterhead" --domain deliverable
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "luxury premium elegant" --domain style
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "hospitality hotel" --domain industry
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "office reception" --domain mockup
```

### CIP：生成样机

```bash
# 带 Logo（推荐）
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "TopGroup" --logo /path/to/logo.png --deliverable "business card" --industry "consulting"

# 完整 CIP 套装
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "TopGroup" --logo /path/to/logo.png --industry "consulting" --set

# Pro 模型（4K 文字）
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "TopGroup" --logo logo.png --deliverable "business card" --model pro

# 无 Logo
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "TechFlow" --deliverable "business card" --no-logo-prompt
```

模型：`flash`（默认，`gemini-2.5-flash-image`）、`pro`（`gemini-3-pro-image-preview`）

### CIP：渲染 HTML 演示文稿

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\render-html.py" --brand "TopGroup" --industry "consulting" --images /path/to/cip-output
```

**提示：** 若无 Logo，请先使用上文 Logo 设计章节生成。

## 幻灯片（内置）

战略性 HTML 演示文稿，集成 Chart.js、设计令牌与文案公式。

加载 `references/slides-create.md` 获取创建流程。

### 幻灯片：知识库

| 主题 | 文件 |
|------|------|
| 创建指南 | `references/slides-create.md` |
| 版式模式 | `references/slides-layout-patterns.md` |
| HTML 模板 | `references/slides-html-template.md` |
| 文案公式 | `references/slides-copywriting-formulas.md` |
| 幻灯片策略 | `references/slides-strategies.md` |

## 横幅设计（内置）

22 种美术指导风格，覆盖社交、广告、网页、印刷。联动 `frontend-design`、`ai-artist`、`ai-multimodal`、`chrome-devtools` 技能。

加载 `references/banner-sizes-and-styles.md` 获取完整尺寸与风格参考。

### 横幅：工作流

1. **收集需求** — 通过 `AskUserQuestion`：用途、平台、内容、品牌、风格、数量
2. **调研** — 激活已汉化的 **ui-ux-pro-max** Skill，在 Pinterest 浏览参考
3. **设计** — 用 `frontend-design` 创建 HTML/CSS 横幅，用 `ai-artist`/`ai-multimodal` 生成视觉
4. **导出** — 通过 `chrome-devtools` 按精确尺寸截图导出 PNG
5. **呈现** — 并排展示所有方案，根据反馈迭代

### 横幅：常用尺寸速查

| 平台 | 类型 | 尺寸（px） |
|------|------|-----------|
| Facebook | 封面 | 820 x 312 |
| Twitter/X | 页眉 | 1500 x 500 |
| LinkedIn | 个人 | 1584 x 396 |
| YouTube | 频道图 | 2560 x 1440 |
| Instagram | Story | 1080 x 1920 |
| Instagram | 帖子 | 1080 x 1080 |
| Google Ads | 中等矩形 | 300 x 250 |
| 网站 | Hero | 1920 x 600-1080 |

### 横幅：主要美术风格

| 风格 | 最适合 |
|------|--------|
| Minimalist | SaaS、科技 |
| Bold Typography | 公告、活动 |
| Gradient | 现代品牌 |
| Photo-Based | 生活方式、电商 |
| Geometric | 科技、金融科技 |
| Glassmorphism | SaaS、应用 |
| Neon/Cyberpunk | 游戏、活动 |

### 横幅：设计规则

- 安全区：关键内容置于画布中央 70–80%
- 每幅横幅一个 CTA，右下放置，最小高度 44px
- 最多 2 种字体，正文最小 16px，标题 ≥32px
- 广告文字占比低于 20%（Meta 会降权）
- 印刷：300 DPI、CMYK、出血 3–5mm

## 图标设计（内置）

15 种风格、12 个类别。Gemini 3.1 Pro Preview 生成 SVG 文本输出。

### 图标：生成单个图标

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "settings gear" --style outlined
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "shopping cart" --style filled --color "#6366F1"
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --name "dashboard" --category navigation --style duotone
```

### 图标：批量生成变体

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "cloud upload" --batch 4 --output-dir ./icons
```

### 图标：多尺寸导出

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\icon\generate.py" --prompt "user profile" --sizes "16,24,32,48" --output-dir ./icons
```

### 图标：主要风格

| 风格 | 最适合 |
|------|--------|
| outlined | UI 界面、Web 应用 |
| filled | 移动应用、导航栏 |
| duotone | 营销、落地页 |
| rounded | 友好型应用、健康 |
| sharp | 科技、金融科技、企业 |
| flat | Material Design、Google 风格 |
| gradient | 现代品牌、SaaS |

**模型：** `gemini-3.1-pro-preview` — 纯文本输出（SVG 为 XML 文本），无需图像生成 API。

## 社交配图（内置）

多平台社交图片设计：HTML/CSS → 截图导出。联动已汉化的 **ui-ux-pro-max**、`brand`、`design-system`、`chrome-devtools` 技能。

加载 `references/social-photos-design.md` 获取尺寸、模板与最佳实践。

### 社交配图：工作流

1. **编排** — `project-management` 技能创建 TODO；独立任务可并行子智能体
2. **分析** — 解析提示：主题、平台、风格、品牌上下文、内容元素
3. **构思** — 3–5 个概念，通过 `AskUserQuestion` 呈现
4. **设计** — `/ckm:brand` → `/ckm:design-system` → 随机调用已汉化的 `/ck:ui-ux-pro-max` 或 `/ck:frontend-design`；每个概念 × 尺寸生成 HTML
5. **导出** — `chrome-devtools` 或 Playwright 按精确 px 截图（`deviceScaleFactor: 2`）
6. **校验** — 用 Chrome MCP 或 `chrome-devtools` 目视检查导出图；修复版式/样式后重新导出
7. **报告** — 将摘要写入 `plans/reports/`，含设计决策
8. **整理** — 调用 `assets-organizing` 技能整理输出与报告

### 社交配图：关键尺寸

| 平台 | 尺寸（px） | 平台 | 尺寸（px） |
|------|-----------|------|-----------|
| IG Post | 1080×1080 | FB Post | 1200×630 |
| IG Story | 1080×1920 | X Post | 1200×675 |
| IG Carousel | 1080×1350 | LinkedIn | 1200×627 |
| YT Thumb | 1280×720 | Pinterest | 1000×1500 |

## 工作流

### 完整品牌包

1. **Logo** → `scripts/logo/generate.py` → 生成 Logo 变体
2. **CIP** → `scripts/cip/generate.py --logo ...` → 创建交付物样机
3. **演示文稿** → 加载 `references/slides-create.md` → 制作融资路演

### 新建设计系统

1. **品牌**（brand 技能）→ 定义色彩、字体、语调
2. **令牌**（design-system 技能）→ 创建语义令牌层
3. **实现**（ui-styling 技能）→ 配置 Tailwind、shadcn/ui

## 参考文档

| 主题 | 文件 |
|------|------|
| 设计路由 | `references/design-routing.md` |
| Logo 设计指南 | `references/logo-design.md` |
| Logo 风格 | `references/logo-style-guide.md` |
| Logo 色彩 | `references/logo-color-psychology.md` |
| Logo 提示词 | `references/logo-prompt-engineering.md` |
| CIP 设计指南 | `references/cip-design.md` |
| CIP 交付物 | `references/cip-deliverable-guide.md` |
| CIP 风格 | `references/cip-style-guide.md` |
| CIP 提示词 | `references/cip-prompt-engineering.md` |
| 幻灯片创建 | `references/slides-create.md` |
| 幻灯片版式 | `references/slides-layout-patterns.md` |
| 幻灯片模板 | `references/slides-html-template.md` |
| 幻灯片文案 | `references/slides-copywriting-formulas.md` |
| 幻灯片策略 | `references/slides-strategies.md` |
| 横幅尺寸与风格 | `references/banner-sizes-and-styles.md` |
| 社交配图指南 | `references/social-photos-design.md` |
| 图标设计指南 | `references/icon-design.md` |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/logo/search.py` | 检索 Logo 风格、色彩、行业 |
| `scripts/logo/generate.py` | 用 Gemini AI 生成 Logo |
| `scripts/logo/core.py` | Logo 数据 BM25 检索引擎 |
| `scripts/cip/search.py` | 检索 CIP 交付物、风格、行业 |
| `scripts/cip/generate.py` | 用 Gemini 生成 CIP 样机 |
| `scripts/cip/render-html.py` | 由 CIP 样机渲染 HTML 演示文稿 |
| `scripts/cip/core.py` | CIP 数据 BM25 检索引擎 |
| `scripts/icon/generate.py` | 用 Gemini 3.1 Pro 生成 SVG 图标 |

## 环境配置

```bash
export GEMINI_API_KEY="your-key"  # https://aistudio.google.com/apikey
pip install google-genai pillow
```

## 集成

**外部子技能：** brand、design-system、ui-styling
**相关技能：** frontend-design、ui-ux-pro-max（已汉化 Skill）、ai-multimodal、chrome-devtools
