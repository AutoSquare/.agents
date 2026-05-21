# 状态与变体

组件状态定义与变体模式。

## 交互状态

### 状态定义

| State | 触发条件 | 视觉变化 |
|-------|---------|---------------|
| default | 无 | 基础外观 |
| hover | 鼠标悬停 | 轻微色彩变化 |
| focus | Tab/点击 | focus ring |
| active | 鼠标按下 | 最深色 |
| disabled | disabled 属性 | 降低透明度 |
| loading | 异步操作 | spinner + 透明度 |

### 状态优先级

多个状态同时生效时，优先级（高 → 低）：

1. disabled
2. loading
3. active
4. focus
5. hover
6. default

### 状态过渡

```css
/* Standard transition for interactive elements */
.interactive {
  transition-property: color, background-color, border-color, box-shadow;
  transition-duration: var(--duration-fast);
  transition-timing-function: ease-in-out;
}
```

| 过渡属性 | Duration | Easing |
|------------|----------|--------|
| Color changes | 150ms | ease-in-out |
| Background | 150ms | ease-in-out |
| Transform | 200ms | ease-out |
| Opacity | 150ms | ease |
| Shadow | 200ms | ease-out |

## Focus 状态

### Focus Ring 规范

```css
/* Standard focus ring */
.focusable:focus-visible {
  outline: none;
  box-shadow: 0 0 0 var(--ring-offset) var(--color-background),
              0 0 0 calc(var(--ring-offset) + var(--ring-width)) var(--ring-color);
}
```

| 属性 | 值 |
|----------|-------|
| Ring width | 2px |
| Ring offset | 2px |
| Ring color | primary (blue-500) |
| Offset color | background |

### Focus Within

```css
/* Container focus when child is focused */
.container:focus-within {
  border-color: var(--color-ring);
}
```

## Disabled 状态

### 视觉处理

```css
.disabled {
  opacity: var(--opacity-disabled); /* 0.5 */
  pointer-events: none;
  cursor: not-allowed;
}
```

| 属性 | Disabled 值 |
|----------|----------------|
| Opacity | 50% |
| Pointer events | none |
| Cursor | not-allowed |
| Background | muted |
| Color | muted-foreground |

### 无障碍

- 语义禁用使用 `aria-disabled="true"`
- 表单元素使用 `disabled` 属性
- 保持足够对比度（最低 3:1）

## Loading 状态

### Spinner 位置

| 组件 | Spinner 位置 |
|-----------|------------------|
| Button | 替换 icon 或居中 |
| Input | 尾部 |
| Card | 居中遮罩 |
| Page | 视口居中 |

### Loading 处理

```css
.loading {
  position: relative;
  pointer-events: none;
}

.loading::after {
  content: '';
  /* spinner styles */
}

.loading > * {
  opacity: 0.7;
}
```

## Error 状态

### 视觉指示

```css
.error {
  border-color: var(--color-error);
  color: var(--color-error);
}

.error:focus-visible {
  box-shadow: 0 0 0 2px var(--color-background),
              0 0 0 4px var(--color-error);
}
```

| 元素 | Error 处理 |
|---------|-----------------|
| Input border | red-500 |
| Input focus ring | red/20% |
| Helper text | red-600 |
| Icon | red-500 |

### 错误消息

- 置于 input 下方
- 使用 error 色
- 配合 icon 提升无障碍
- 输入有效后清除

## 变体模式

### 颜色变体

```css
/* Pattern for color variants */
.component {
  --component-bg: var(--color-primary);
  --component-fg: var(--color-primary-foreground);
  background: var(--component-bg);
  color: var(--component-fg);
}

.component.secondary {
  --component-bg: var(--color-secondary);
  --component-fg: var(--color-secondary-foreground);
}

.component.destructive {
  --component-bg: var(--color-destructive);
  --component-fg: var(--color-destructive-foreground);
}
```

### 尺寸变体

```css
/* Pattern for size variants */
.component {
  --component-height: 40px;
  --component-padding: var(--space-4);
  --component-font: var(--font-size-sm);
}

.component.sm {
  --component-height: 32px;
  --component-padding: var(--space-3);
  --component-font: var(--font-size-xs);
}

.component.lg {
  --component-height: 48px;
  --component-padding: var(--space-6);
  --component-font: var(--font-size-base);
}
```

## 无障碍要求

### 颜色对比度

| 元素 | 最低比例 |
|---------|---------------|
| Normal text | 4.5:1 |
| Large text (18px+) | 3:1 |
| UI components | 3:1 |
| Focus indicator | 3:1 |

### 状态指示

- 不可仅依赖颜色
- 配合 icon、文字或图案
- 确保 focus 可见
- 提供 loading 播报

### ARIA 状态

```html
<!-- Disabled -->
<button disabled aria-disabled="true">Submit</button>

<!-- Loading -->
<button aria-busy="true" aria-describedby="loading-text">
  <span id="loading-text" class="sr-only">Loading...</span>
</button>

<!-- Error -->
<input aria-invalid="true" aria-describedby="error-msg">
<span id="error-msg" role="alert">Error message</span>
```
