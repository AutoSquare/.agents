# 组件规范

核心组件的详细规范，含状态与变体定义。

## Button

### 变体

| Variant | Background | Text | Border | 适用场景 |
|---------|------------|------|--------|----------|
| default | primary | white | none | 主要操作 |
| secondary | gray-100 | gray-900 | none | 次要操作 |
| outline | transparent | foreground | border | 第三级操作 |
| ghost | transparent | foreground | none | 轻量操作 |
| link | transparent | primary | none | 导航 |
| destructive | red-600 | white | none | 危险操作 |

### 尺寸

| Size | Height | Padding X | Padding Y | Font Size | Icon Size |
|------|--------|-----------|-----------|-----------|-----------|
| sm | 32px | 12px | 6px | 14px | 16px |
| default | 40px | 16px | 8px | 14px | 18px |
| lg | 48px | 24px | 12px | 16px | 20px |
| icon | 40px | 0 | 0 | - | 18px |

### 状态

| State | Background | Text | Opacity | Cursor |
|-------|------------|------|---------|--------|
| default | token | token | 1 | pointer |
| hover | darker | token | 1 | pointer |
| active | darkest | token | 1 | pointer |
| focus | token | token | 1 | pointer |
| disabled | muted | muted-fg | 0.5 | not-allowed |
| loading | token | token | 0.7 | wait |

### 结构

```
┌─────────────────────────────────────┐
│  [icon]  Label Text  [icon]         │
└─────────────────────────────────────┘
     ↑                      ↑
  leading icon         trailing icon
```

---

## Input

### 变体

| Variant | 说明 |
|---------|-------------|
| default | 标准单行文本输入 |
| textarea | 多行文本 |
| select | 下拉选择 |
| checkbox | 布尔开关 |
| radio | 单选 |
| switch | 切换开关 |

### 尺寸

| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| sm | 32px | 8px 12px | 14px |
| default | 40px | 8px 12px | 14px |
| lg | 48px | 12px 16px | 16px |

### 状态

| State | Border | Background | Ring |
|-------|--------|------------|------|
| default | gray-300 | white | none |
| hover | gray-400 | white | none |
| focus | primary | white | primary/20% |
| error | red-500 | white | red/20% |
| disabled | gray-200 | gray-100 | none |

### 结构

```
Label (optional)
┌─────────────────────────────────────┐
│ [icon] Placeholder/Value   [action] │
└─────────────────────────────────────┘
Helper text or error message
```

---

## Card

### 变体

| Variant | Shadow | Border | 适用场景 |
|---------|--------|--------|----------|
| default | sm | 1px | 标准卡片 |
| elevated | lg | none | 突出内容 |
| outline | none | 1px | 轻量容器 |
| interactive | sm→md | 1px | 可点击卡片 |

### 结构

```
┌─────────────────────────────────────┐
│ Card Header                         │
│   Title                             │
│   Description                       │
├─────────────────────────────────────┤
│ Card Content                        │
│   Main content area                 │
│                                     │
├─────────────────────────────────────┤
│ Card Footer                         │
│   Actions                           │
└─────────────────────────────────────┘
```

### 间距

| 区域 | Padding |
|------|---------|
| header | 24px 24px 0 |
| content | 24px |
| footer | 0 24px 24px |
| gap | 16px |

---

## Badge

### 变体

| Variant | Background | Text |
|---------|------------|------|
| default | primary | white |
| secondary | gray-100 | gray-900 |
| outline | transparent | foreground |
| destructive | red-600 | white |
| success | green-600 | white |
| warning | yellow-500 | gray-900 |

### 尺寸

| Size | Padding | Font Size | Height |
|------|---------|-----------|--------|
| sm | 4px 8px | 11px | 20px |
| default | 4px 10px | 12px | 24px |
| lg | 6px 12px | 14px | 28px |

---

## Alert

### 变体

| Variant | Icon | Background | Border |
|---------|------|------------|--------|
| default | info | gray-50 | gray-200 |
| destructive | alert | red-50 | red-200 |
| success | check | green-50 | green-200 |
| warning | warning | yellow-50 | yellow-200 |

### 结构

```
┌─────────────────────────────────────┐
│ [icon]  Title                    [×]│
│         Description text            │
└─────────────────────────────────────┘
```

---

## Dialog

### 尺寸

| Size | Max Width | 适用场景 |
|------|-----------|----------|
| sm | 384px | 简单确认 |
| default | 512px | 标准对话框 |
| lg | 640px | 复杂表单 |
| xl | 768px | 数据密集型对话框 |
| full | 100% - 32px | 移动端全屏 |

### 结构

```
┌───────────────────────────────────────┐
│ Dialog Header                      [×]│
│   Title                               │
│   Description                         │
├───────────────────────────────────────┤
│ Dialog Content                        │
│   Scrollable if needed                │
│                                       │
├───────────────────────────────────────┤
│ Dialog Footer                         │
│                     [Cancel] [Confirm]│
└───────────────────────────────────────┘
```

---

## Table

### 行状态

| State | Background | 适用场景 |
|-------|------------|----------|
| default | white | 普通行 |
| hover | gray-50 | 鼠标悬停 |
| selected | primary/10% | 选中行 |
| striped | gray-50/white | 斑马纹 |

### 单元格对齐

| 内容类型 | 对齐 |
|--------------|-----------|
| Text | Left |
| Numbers | Right |
| Status/Badge | Center |
| Actions | Right |

### 间距

| 元素 | 值 |
|---------|-------|
| cell padding | 12px 16px |
| header padding | 12px 16px |
| row height (compact) | 40px |
| row height (default) | 48px |
| row height (comfortable) | 56px |
