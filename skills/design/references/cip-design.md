# CIP 设计参考

企业识别系统（Corporate Identity Program）设计：50+ 交付物、20 种风格、20 个行业。使用 Gemini Nano Banana（Flash/Pro）生成样机。

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/cip/search.py` | 检索交付物、风格、行业；生成 CIP 简报 |
| `scripts/cip/generate.py` | 用 Gemini（Flash/Pro）生成 CIP 样机 |
| `scripts/cip/render-html.py` | 由 CIP 样机渲染 HTML 演示文稿 |
| `scripts/cip/core.py` | CIP 数据 BM25 检索引擎 |

## 命令

### CIP 简报（从这里开始）

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "tech startup" --cip-brief -b "BrandName"
```

### 检索领域

```bash
# 交付物
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "business card letterhead" --domain deliverable

# 设计风格
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "luxury premium elegant" --domain style

# 行业指南
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "hospitality hotel" --domain industry

# 样机场景
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\search.py" "office reception" --domain mockup
```

### 生成样机

```bash
# 带 Logo（推荐 — 使用图像编辑）
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "TopGroup" --logo /path/to/logo.png --deliverable "business card" --industry "consulting"

# 完整 CIP 套装（带 Logo）
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "TopGroup" --logo /path/to/logo.png --industry "consulting" --set

# Pro 模型（4K 文字渲染）
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "TopGroup" --logo logo.png --deliverable "business card" --model pro

# 自定义交付物与宽高比
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "GreenLeaf" --logo logo.png --industry "organic food" --deliverables "letterhead,packaging,vehicle" --ratio 16:9

# 无 Logo（由 AI 诠释）
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\generate.py" --brand "TechFlow" --deliverable "business card" --no-logo-prompt
```

### 渲染 HTML 演示文稿

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\render-html.py" --brand "TopGroup" --industry "consulting" --images /path/to/cip-output
python "$env:USERPROFILE\.cursor\skills\design\scripts\cip\render-html.py" --brand "TopGroup" --industry "consulting" --images ./topgroup-cip --output presentation.html
```

## 模型

- `flash`（默认）：`gemini-2.5-flash-image` — 快速、成本低
- `pro`：`gemini-3-pro-image-preview` — 高质量、4K 文字渲染

## 交付物类别

| 类别 | 项目 |
|------|------|
| 核心识别 | Logo、Logo 变体 |
| 文具 | 名片、信纸、信封、文件夹、笔记本、笔 |
| 安全/通行 | 工牌、挂绳、门禁卡 |
| 办公环境 | 前台标识、导视、会议室标牌、墙面图形 |
| 服装 | Polo 衫、T 恤、帽、夹克、围裙 |
| 促销 | 托特包、礼盒、U 盘、水瓶、马克杯、雨伞 |
| 车辆 | 轿车、厢货、卡车 |
| 数字 | 社交媒体、邮件签名、PowerPoint、文档模板 |
| 产品 | 包装盒、标签、吊牌、零售陈列 |
| 活动 | 展会展位、易拉宝、桌布、背景板 |

## 设计风格

| 风格 | 色彩 | 最适合 |
|------|------|--------|
| Corporate Minimal | 海军蓝、白、蓝 | 金融、法律、咨询 |
| Modern Tech | 紫、青、绿 | 科技、创业、SaaS |
| Luxury Premium | 黑、金、白 | 时尚、珠宝、酒店 |
| Warm Organic | 棕、绿、奶油色 | 食品、有机、手工艺 |
| Bold Dynamic | 红、橙、黑 | 体育、娱乐 |

## HTML 演示文稿特性

- Hero 区：品牌名、行业、风格、情绪
- 交付物卡片：含样机图
- 说明：概念、用途、规格
- 响应式桌面/移动端、深色主题
- 图片以 base64 嵌入（单文件可移植）

## 工作流

1. 生成 CIP 简报 → `scripts/cip/search.py --cip-brief`
2. 带 Logo 生成样机 → `scripts/cip/generate.py --brand --logo --industry --set`
3. 渲染 HTML 演示文稿 → `scripts/cip/render-html.py --brand --industry --images`

**提示：** 若无 Logo，请先使用内置 Logo 设计生成。

## 详细参考

- `references/cip-deliverable-guide.md` — 交付物规格
- `references/cip-style-guide.md` — 设计风格说明
- `references/cip-prompt-engineering.md` — AI 生成提示词

## 环境配置

```bash
export GEMINI_API_KEY="your-key"
pip install google-genai pillow
```
