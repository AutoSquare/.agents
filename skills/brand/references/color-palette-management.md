# 色板管理

品牌色彩定义、提取与执行指南。

## 色彩体系结构

### 层级
```
Primary Colors (1-2)
├── Main brand color - Used for CTAs, headers, key elements
└── Supporting primary - Secondary emphasis

Secondary Colors (2-3)
├── Accent colors - Highlights, interactive states
└── Supporting visuals - Icons, illustrations

Neutral Palette (3-5)
├── Background colors - Page, card, modal backgrounds
├── Text colors - Headings, body, muted text
└── UI elements - Borders, dividers, shadows

Semantic Colors (4)
├── Success - #22C55E (green)
├── Warning - #F59E0B (amber)
├── Error - #EF4444 (red)
└── Info - #3B82F6 (blue)
```

## 色彩文档格式

### Markdown 表格
```markdown
| Name | Hex | RGB | HSL | Usage |
|------|-----|-----|-----|-------|
| Primary Blue | #2563EB | rgb(37,99,235) | hsl(217,91%,53%) | CTAs, links |
```

### CSS 变量
```css
:root {
  /* Primary */
  --color-primary: #2563EB;
  --color-primary-light: #3B82F6;
  --color-primary-dark: #1D4ED8;

  /* Secondary */
  --color-secondary: #8B5CF6;
  --color-accent: #F59E0B;

  /* Neutral */
  --color-background: #FFFFFF;
  --color-surface: #F9FAFB;
  --color-text-primary: #111827;
  --color-text-secondary: #6B7280;
  --color-border: #E5E7EB;
}
```

### Tailwind 配置
```javascript
colors: {
  primary: {
    DEFAULT: '#2563EB',
    50: '#EFF6FF',
    100: '#DBEAFE',
    500: '#3B82F6',
    600: '#2563EB',
    700: '#1D4ED8',
  }
}
```

## 无障碍要求

### 对比度（WCAG 2.1）
| 等级 | 常规文字 | 大号文字 | UI 组件 |
|------|----------|----------|---------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | 4.5:1 |

### 对比度计算
```javascript
// Formula for relative luminance
function luminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map(v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function contrastRatio(l1, l2) {
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

## 色彩提取

### 自图像

使用 `extract-colors.cjs` 脚本：
1. 加载图像文件
2. 以 k-means 聚类提取主色
3. 映射至最近品牌色
4. 输出合规百分比

### 自品牌指南

解析 Markdown 提取：
- 表格中的 Hex 值
- CSS 变量定义
- 颜色名称与用途说明

## 品牌合规校验

### 规则
1. **主色占比**：设计面积的 60–70%
2. **辅色占比**：20–30%
3. **强调色占比**：5–10%
4. **非品牌色容差**：非色板颜色不超过 20%

### 校验输出
```json
{
  "compliance": 85,
  "colors": {
    "brand": ["#2563EB", "#8B5CF6", "#FFFFFF"],
    "offBrand": ["#FF5500"],
    "dominant": "#2563EB"
  },
  "issues": [
    "Off-brand color #FF5500 detected (15% coverage)",
    "Primary color underused (45% vs 60% target)"
  ]
}
```

## 色彩使用规范

### 应当
- 主色用于主要 CTA 与关键元素
- 悬停 / 激活状态保持一致
- 测试全部组合的无障碍对比度
- 记录色彩决策

### 避免
- 单一组件使用超过 2–3 种颜色
- 无意混用冷暖色调
- 正文使用纯黑（#000），宜采用 #111 等近似色
- 仅凭颜色传达含义（须配合图标或文字）

## 色板示例

### 科技 / SaaS
```
Primary: #2563EB (Blue)
Secondary: #8B5CF6 (Purple)
Accent: #10B981 (Emerald)
Background: #F9FAFB
Text: #111827
```

### 营销 / 创意
```
Primary: #F97316 (Orange)
Secondary: #EC4899 (Pink)
Accent: #14B8A6 (Teal)
Background: #FFFFFF
Text: #1F2937
```

### 商务 / 企业
```
Primary: #1E40AF (Navy)
Secondary: #475569 (Slate)
Accent: #0EA5E9 (Sky)
Background: #F8FAFC
Text: #0F172A
```

## 工具与资源

- [Coolors](https://coolors.co) - Palette generation
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Tailwind Color Reference](https://tailwindcss.com/docs/customizing-colors)
- [Color Hunt](https://colorhunt.co) - Curated palettes
