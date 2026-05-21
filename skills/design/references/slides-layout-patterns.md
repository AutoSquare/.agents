# 版式模式

25 种幻灯片版式，含 CSS 结构与动画类。

## 按场景选择版式

| 版式 | 适用场景 | 动画 |
|------|----------|------|
| Title Slide | 开场 / 首屏印象 | `animate-fade-up` |
| Problem Statement | 建立痛点 | `animate-stagger` |
| Solution Overview | 引入解决方案 | `animate-scale` |
| Feature Grid | 展示能力（3–6 张卡片） | `animate-stagger` |
| Metrics Dashboard | 展示 KPI（3–4 项指标） | `animate-stagger-scale` |
| Comparison Table | 对比选项 | `animate-fade-up` |
| Timeline Flow | 展示进程 | `animate-stagger` |
| Team Grid | 介绍团队成员 | `animate-stagger` |
| Quote Testimonial | 客户背书 | `animate-fade-up` |
| Two Column Split | 对比 / 对照 | `animate-fade-up` |
| Big Number Hero | 单一核心指标 | `animate-count` |
| Product Screenshot | 展示产品界面 | `animate-scale` |
| Pricing Cards | 展示价格档位 | `animate-stagger` |
| CTA Closing | 驱动行动 | `animate-pulse` |

## CSS 结构

### Title Slide
```css
.slide-title {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
```

### Two Column Split
```css
.slide-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
    align-items: center;
}
@media (max-width: 768px) {
    .slide-split { grid-template-columns: 1fr; gap: 24px; }
}
```

### Feature Grid (3 columns)
```css
.slide-features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}
@media (max-width: 768px) {
    .slide-features { grid-template-columns: repeat(2, 1fr); gap: 16px; }
}
@media (max-width: 480px) {
    .slide-features { grid-template-columns: 1fr; }
}
```

### Metrics Dashboard (4 columns)
```css
.slide-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}
@media (max-width: 768px) {
    .slide-metrics { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
    .slide-metrics { grid-template-columns: 1fr; }
}
```

## 组件变体

### 卡片样式
| 样式 | CSS 类 | 适用场景 |
|------|--------|----------|
| Icon Left | `.card-icon-left` | 带图标的功能项 |
| Accent Bar | `.card-accent-bar` | 需强调的功能项 |
| Metric Card | `.card-metric` | 数字 / 统计 |
| Avatar Card | `.card-avatar` | 团队成员 |
| Pricing Card | `.card-pricing` | 价格档位 |

### 指标样式
| 样式 | 效果 |
|------|------|
| `gradient-number` | 数字渐变文字 |
| `oversized` | 超大字号（120px+） |
| `sparkline` | 小型内联图表 |
| `funnel-numbers` | 转化阶段 |

## 视觉处理

| 处理 | 适用场景 |
|------|----------|
| `gradient-glow` | 标题幻灯片、CTA |
| `subtle-border` | 问题陈述 |
| `icon-top` | 功能网格 |
| `screenshot-shadow` | 产品截图 |
| `popular-highlight` | 定价（缩放 1.05） |
| `bg-overlay` | 背景图 |
| `contrast-pair` | 前后对比 |
| `logo-grayscale` | 客户 Logo |

## 检索命令

```bash
# 按场景查找版式
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "metrics dashboard" -d layout

# 情境化推荐
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "traction slide" \
  --context --position 4 --total 10
```

## 版式决策流程

```
1. 本页幻灯片的目标是什么？
   └─> 检索 layout-logic.csv

2. 应触发何种情绪？
   └─> 检索 color-logic.csv

3. 内容类型是什么？
   └─> 检索 typography.csv

4. 是否打破既有模式？
   └─> 检查位置（1/3、2/3）→ 使用 full-bleed
```
