# 品牌指南 v1.0

> 最后更新：{DATE}
> 状态：草稿

## 快速参考

| 元素 | 数值 |
|------|------|
| 主色 | #2563EB |
| 辅色 | #8B5CF6 |
| 主字体 | Inter |
| 调性 | 专业、务实、清晰 |

---

## 1. 色板

### 主色

| 名称 | Hex | RGB | 用途 |
|------|-----|-----|------|
| Primary Blue | #2563EB | rgb(37,99,235) | CTA、标题、链接 |
| Primary Dark | #1D4ED8 | rgb(29,78,216) | 悬停态、强调 |

### 辅色

| 名称 | Hex | RGB | 用途 |
|------|-----|-----|------|
| Secondary Purple | #8B5CF6 | rgb(139,92,246) | 点缀、高亮 |
| Accent Green | #10B981 | rgb(16,185,129) | 成功、正向状态 |

### 中性色

| 名称 | Hex | RGB | 用途 |
|------|-----|-----|------|
| Background | #FFFFFF | rgb(255,255,255) | 页面背景 |
| Surface | #F9FAFB | rgb(249,250,251) | 卡片、区块 |
| Text Primary | #111827 | rgb(17,24,39) | 标题、正文 |
| Text Secondary | #6B7280 | rgb(107,114,128) | 注释、弱化文字 |
| Border | #E5E7EB | rgb(229,231,235) | 分隔线、边框 |

### 语义色

| 状态 | Hex | 用途 |
|------|-----|------|
| Success | #22C55E | 正向操作、确认 |
| Warning | #F59E0B | 警示、待处理 |
| Error | #EF4444 | 错误、破坏性操作 |
| Info | #3B82F6 | 信息提示 |

### 无障碍

- 白底文字对比度：7.2:1（AAA）
- 主色于白底：4.6:1（AA）
- 全部交互元素满足 WCAG 2.1 AA

---

## 2. 字体

### 字体栈

```css
--font-heading: 'Inter', system-ui, -apple-system, sans-serif;
--font-body: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### 字号阶梯

| 元素 | 尺寸（桌面） | 尺寸（移动） | 字重 | 行高 |
|------|--------------|--------------|------|------|
| H1 | 48px | 32px | 700 | 1.2 |
| H2 | 36px | 28px | 600 | 1.25 |
| H3 | 28px | 24px | 600 | 1.3 |
| H4 | 24px | 20px | 600 | 1.35 |
| Body | 16px | 16px | 400 | 1.5 |
| Body Large | 18px | 18px | 400 | 1.6 |
| Small | 14px | 14px | 400 | 1.5 |
| Caption | 12px | 12px | 400 | 1.4 |

### 字体加载

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

---

## 3. Logo 使用

### 变体

| 变体 | 文件 | 使用场景 |
|------|------|----------|
| Full Horizontal | logo-full-horizontal.svg | 页眉、文档 |
| Stacked | logo-stacked.svg | 方形区域 |
| Icon Only | logo-icon.svg | Favicon、小尺寸 |
| Monochrome | logo-mono.svg | 受限配色场景 |

### 安全区

最小安全区 = Logo 标识（mark）高度

### 最小尺寸

| 情境 | 最小宽度 |
|------|----------|
| 数字媒体 — 完整 Logo | 120px |
| 数字媒体 — 图标 | 24px |
| 印刷 — 完整 Logo | 35mm |
| 印刷 — 图标 | 10mm |

### 禁止事项

- 禁止旋转或倾斜 Logo
- 禁止在批准色板外改色
- 禁止添加阴影或特效
- 禁止裁剪或改变比例
- 禁止在对比不足的多变背景上使用

---

## 4. 调性与语气

### 品牌人格

| 特质 | 描述 |
|------|------|
| **Professional** | 专业可靠，权威而不疏离 |
| **Helpful** | 以解决方案为导向，提供可执行指引 |
| **Clear** | 表达直接，避免行话 |
| **Confident** | 自信稳妥，不傲慢 |

### 调性对照表

| 特质 | 我们是 | 我们不是 |
|------|--------|----------|
| Professional | 专业、有见地 | 刻板、官僚 |
| Helpful | 支持、赋能 | 居高临下 |
| Clear | 直接、简洁 | 模糊、冗长 |
| Confident | 可靠、值得信赖 | 傲慢、过度推销 |

### 分情境语气

| 情境 | 语气 | 示例 |
|------|------|------|
| Marketing |  engaging、强调收益 | "Create campaigns that convert." |
| Documentation | 清晰、指导性 | "Run the command to start." |
| Error messages |  calm、聚焦解决方案 | "Try refreshing the page." |
| Success |  brief、适度庆祝 | "Campaign published!" |

### 禁用词

| 避免 | 原因 |
|------|------|
| Revolutionary | 过度使用 |
| Best-in-class | 表述空泛 |
| Seamless | 过度使用 |
| Synergy | 企业行话 |
| Leverage | 改用「使用」 |

---

## 5. 影像规范

### 摄影风格

- **Lighting:** 优先自然、柔和光线
- **Subjects:** 真实人物与真实场景
- **Color treatment:** 后期保持品牌色
- **Composition:** 主体清晰、构图简洁

### 插画

- Style: 现代扁平，带轻微渐变
- Colors: 仅使用品牌色板
- Line weight: 统一 2px 描边
- Corners: 4px 圆角

### 图标

- Style: 线框，24px 基准网格
- Stroke: 统一 1.5px
- Corner radius: 2px
- Fill: 无填充（仅线框）

---

## 6. 设计组件

### 按钮

| 类型 | 背景 | 文字 | 圆角 |
|------|------|------|------|
| Primary | #2563EB | #FFFFFF | 8px |
| Secondary | Transparent | #2563EB | 8px |
| Tertiary | Transparent | #6B7280 | 8px |

### 间距阶梯

| 令牌 | 数值 | 用途 |
|------|------|------|
| xs | 4px | 紧凑间距 |
| sm | 8px | 紧凑元素 |
| md | 16px | 标准间距 |
| lg | 24px | 区块间距 |
| xl | 32px | 较大间隙 |
| 2xl | 48px | 区块分隔 |

### 圆角

| 元素 | 圆角 |
|------|------|
| Buttons | 8px |
| Cards | 12px |
| Inputs | 8px |
| Modals | 16px |
| Pills/Tags | 9999px |

---

## AI 图像生成

### 基础提示词模板

生成图像时在提示词前追加：

```
{DESCRIBE YOUR VISUAL STYLE HERE - mood, colors with hex codes, lighting, atmosphere}
```

### 风格关键词

| 类别 | 关键词 |
|------|--------|
| **Lighting** | {e.g., soft lighting, dramatic, natural} |
| **Mood** | {e.g., professional, energetic, calm} |
| **Composition** | {e.g., centered, rule of thirds, minimal} |
| **Treatment** | {e.g., high contrast, muted, vibrant} |
| **Aesthetic** | {e.g., modern, vintage, minimalist} |

### 视觉氛围描述

- {Mood descriptor 1}
- {Mood descriptor 2}
- {Mood descriptor 3}

### 视觉禁忌

| 避免 | 原因 |
|------|------|
| {Item to avoid} | {Why to avoid it} |

### 提示词示例

**Hero Banner:**
```
{Example prompt for hero banners}
```

**Social Media Post:**
```
{Example prompt for social graphics}
```

---

## 变更记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | {DATE} | 初始版本 |
