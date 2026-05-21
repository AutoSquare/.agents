---
name: ckm:design-system
description: Token 架构、组件规范与幻灯片生成。三层 token（primitive→semantic→component）、CSS 变量、间距/排版尺度、组件规范、策略化幻灯片创建。适用于 design token、系统化设计、符合品牌规范的演示文稿。
argument-hint: "[component or token]"
license: MIT
metadata:
  author: claudekit
  version: "1.0.0"
---

# Design System

Token 架构、组件规范、系统化设计与幻灯片生成。

## 适用场景

- 创建 design token
- 定义组件状态
- 构建 CSS 变量体系
- 间距/排版尺度
- 设计到代码交付
- Tailwind 主题配置
- **幻灯片/演示文稿生成**

## Token 架构

加载：`references/token-architecture.md`

### 三层结构

```
Primitive（原始值）
       ↓
Semantic（语义别名）
       ↓
Component（组件级）
```

**示例：**
```css
/* Primitive */
--color-blue-600: #2563EB;

/* Semantic */
--color-primary: var(--color-blue-600);

/* Component */
--button-bg: var(--color-primary);
```

## 快速开始

**生成 token：**
```bash
node scripts/generate-tokens.cjs --config tokens.json -o tokens.css
```

**校验用法：**
```bash
node scripts/validate-tokens.cjs --dir src/
```

## 参考文档

| 主题 | 文件 |
|------|------|
| Token 架构 | `references/token-architecture.md` |
| Primitive Token | `references/primitive-tokens.md` |
| Semantic Token | `references/semantic-tokens.md` |
| Component Token | `references/component-tokens.md` |
| 组件规范 | `references/component-specs.md` |
| 状态与变体 | `references/states-and-variants.md` |
| Tailwind 集成 | `references/tailwind-integration.md` |

## 组件规范模式

| 属性 | Default | Hover | Active | Disabled |
|----------|---------|-------|--------|----------|
| Background | primary | primary-dark | primary-darker | muted |
| Text | white | white | white | muted-fg |
| Border | none | none | none | muted-border |
| Shadow | sm | md | none | none |

## 脚本

| 脚本 | 用途 |
|--------|---------|
| `generate-tokens.cjs` | 从 JSON token 配置生成 CSS |
| `validate-tokens.cjs` | 检查代码中的硬编码值 |
| `search-slides.py` | BM25 检索 + 上下文推荐 |
| `slide-token-validator.py` | 校验幻灯片 HTML 的 token 合规性 |
| `fetch-background.py` | 从 Pexels/Unsplash 获取图片 |

## 模板

| 模板 | 用途 |
|----------|---------|
| `design-tokens-starter.json` | 含三层结构的 starter JSON |

## 集成

**与 brand 联动：** 从品牌色/排版提取 primitive
**与 ui-styling 联动：** component token → Tailwind 配置

**技能依赖：** brand, ui-styling
**主要 Agent：** ui-ux-designer, frontend-developer

## 幻灯片系统

基于 design token + Chart.js + 上下文决策系统，生成符合品牌规范的演示文稿。

### 单一事实来源

| 文件 | 用途 |
|------|---------|
| `docs/brand-guidelines.md` | 品牌标识、语调、色彩 |
| `assets/design-tokens.json` | Token 定义（primitive→semantic→component） |
| `assets/design-tokens.css` | CSS 变量（在幻灯片中 import） |
| `assets/css/slide-animations.css` | CSS 动画库 |

### 幻灯片检索（BM25）

```bash
# 基础检索（自动检测领域）
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "investor pitch"

# 按领域检索
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "problem agitation" -d copy
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "revenue growth" -d chart

# 上下文检索（Premium System）
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "problem slide" --context --position 2 --total 9
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "cta" --context --position 9 --prev-emotion frustration
```

### 决策系统 CSV

| 文件 | 用途 |
|------|---------|
| `data/slide-strategies.csv` | 15 种 deck 结构 + 情绪弧线 + sparkline 节拍 |
| `data/slide-layouts.csv` | 25 种布局 + 组件变体 + 动画 |
| `data/slide-layout-logic.csv` | 目标 → 布局 + break_pattern 标志 |
| `data/slide-typography.csv` | 内容类型 → 排版尺度 |
| `data/slide-color-logic.csv` | 情绪 → 色彩处理 |
| `data/slide-backgrounds.csv` | 幻灯片类型 → 图片类别（Pexels/Unsplash） |
| `data/slide-copy.csv` | 25 种文案公式（PAS、AIDA、FAB） |
| `data/slide-charts.csv` | 25 种图表类型及 Chart.js 配置 |

### 上下文决策流程

```
1. 解析目标/上下文
        ↓
2. 检索 slide-strategies.csv → 获取策略 + 情绪节拍
        ↓
3. 对每张幻灯片：
   a. 查询 slide-layout-logic.csv → layout + break_pattern
   b. 查询 slide-typography.csv → type scale
   c. 查询 slide-color-logic.csv → color treatment
   d. 查询 slide-backgrounds.csv → 按需获取图片
   e. 从 slide-animations.css 应用 animation class
        ↓
4. 使用 design token 生成 HTML
        ↓
5. 用 slide-token-validator.py 校验
```

### 模式打破（Duarte Sparkline）

高质量 deck 在情绪间交替切换以提升参与度：
```
"What Is"（frustration）↔ "What Could Be"（hope）
```

系统在 1/3 与 2/3 位置计算 pattern break。

### 幻灯片要求

**所有幻灯片必须：**
1. import `assets/design-tokens.css` — 单一事实来源
2. 使用 CSS 变量：`var(--color-primary)`、`var(--slide-bg)` 等
3. 图表使用 Chart.js（禁止纯 CSS 条形图）
4. 包含导航（键盘方向键、点击、进度条）
5. 内容居中对齐
6. 聚焦说服与转化

### Chart.js 集成

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

<canvas id="revenueChart"></canvas>
<script>
new Chart(document.getElementById('revenueChart'), {
    type: 'line',
    data: {
        labels: ['Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            data: [5, 12, 28, 45],
            borderColor: '#FF6B6B',  // Use brand coral
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            fill: true,
            tension: 0.4
        }]
    }
});
</script>
```

### Token 合规

```css
/* CORRECT - uses token */
background: var(--slide-bg);
color: var(--color-primary);
font-family: var(--typography-font-heading);

/* WRONG - hardcoded */
background: #0D0D0D;
color: #FF6B6B;
font-family: 'Space Grotesk';
```

### 参考实现

包含全部特性的可运行示例：
```
assets/designs/slides/claudekit-pitch-251223.html
```

### 命令

```bash
/slides:create "10-slide investor pitch for ClaudeKit Marketing"
```

## 最佳实践

1. 组件中禁止使用原始 hex — 始终引用 token
2. semantic 层支持主题切换（light/dark）
3. component token 支持按组件定制
4. 使用 HSL 格式以便控制透明度
5. 为每个 token 记录用途
6. **幻灯片必须 import design-tokens.css，且仅使用 var()**
