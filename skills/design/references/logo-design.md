# Logo 设计参考

AI 驱动的 Logo 设计：55+ 风格、30 套色板、25 个行业指南。使用 Gemini Nano Banana 模型。

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/logo/search.py` | 检索风格、色彩、行业；生成设计简报 |
| `scripts/logo/generate.py` | 用 Gemini Nano Banana 生成 Logo |
| `scripts/logo/core.py` | Logo 数据 BM25 检索引擎 |

## 命令

### 设计简报（从这里开始）

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\search.py" "tech startup modern" --design-brief -p "BrandName"
```

### 检索领域

```bash
# 风格
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\search.py" "minimalist clean" --domain style

# 色板
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\search.py" "tech professional" --domain color

# 行业指南
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\search.py" "healthcare medical" --domain industry
```

### 生成 Logo

**务必**以白色背景输出 Logo。

```bash
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\generate.py" --brand "TechFlow" --style minimalist --industry tech
python "$env:USERPROFILE\.cursor\skills\design\scripts\logo\generate.py" --prompt "coffee shop vintage badge" --style vintage
```

选项：`--style`、`--industry`、`--prompt`

## 可用风格

| 类别 | 风格 |
|------|------|
| 通用 | Minimalist、Wordmark、Lettermark、Pictorial Mark、Abstract Mark、Mascot、Emblem、Combination Mark |
| 美学 | Vintage/Retro、Art Deco、Luxury、Playful、Corporate、Organic、Neon、Grunge、Watercolor |
| 现代 | Gradient、Flat Design、3D/Isometric、Geometric、Line Art、Duotone、Motion-Ready |
| 巧思 | Negative Space、Monoline、Split/Fragmented、Responsive/Adaptive |

## 色彩心理学

| 颜色 | 心理联想 | 最适合 |
|------|----------|--------|
| Blue | 信任、稳定 | 金融、科技、医疗 |
| Green | 成长、自然 | 环保、健康、有机 |
| Red | 能量、热情 | 餐饮、体育、娱乐 |
| Gold | 奢华、高端 | 时尚、珠宝、酒店 |
| Purple | 创意、创新 | 美妆、创意、科技 |

## 行业默认

| 行业 | 风格 | 色彩 | 字体 |
|------|------|------|------|
| Tech | Minimalist、Abstract | 蓝、紫、渐变 | 几何无衬线 |
| Healthcare | Professional、Line Art | 蓝、绿、青 | 简洁无衬线 |
| Finance | Corporate、Emblem | 海军蓝、金 | 衬线或简洁无衬线 |
| Food | Vintage Badge、Mascot | 暖红、橙 | 友好、手写体 |
| Fashion | Wordmark、Luxury | 黑、金、白 | 优雅衬线 |

## 工作流

1. 生成设计简报 → `scripts/logo/search.py --design-brief`
2. 生成 Logo 变体 → `scripts/logo/generate.py --brand --style --industry`
3. 询问用户是否需要 HTML 预览 → `AskUserQuestion` 工具
4. 若需要，调用已汉化的 **ui-ux-pro-max** Skill 生成 HTML 画廊

## 详细参考

- `references/logo-style-guide.md` — 风格详解
- `references/logo-color-psychology.md` — 色彩含义与搭配
- `references/logo-prompt-engineering.md` — AI 生成提示词

## 环境配置

```bash
export GEMINI_API_KEY="your-key"
pip install google-genai
```
