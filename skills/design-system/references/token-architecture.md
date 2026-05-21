# Token 架构

面向可扩展、可换肤设计系统的三层 token 体系。

## 层级概览

```
┌─────────────────────────────────────────┐
│  Component Tokens                       │  按组件覆盖
│  --button-bg, --card-padding            │
├─────────────────────────────────────────┤
│  Semantic Tokens                        │  基于用途的别名
│  --color-primary, --spacing-section     │
├─────────────────────────────────────────┤
│  Primitive Tokens                       │  原始设计值
│  --color-blue-600, --space-4            │
└─────────────────────────────────────────┘
```

## 为何采用三层？

| 层级 | 用途 | 变更时机 |
|-------|---------|----------------|
| Primitive | 基础值（颜色、尺寸） | 极少 — 作为基础层 |
| Semantic | 语义映射 | 主题切换 |
| Component | 组件定制 | 按组件需求 |

## 第 1 层：Primitive Token

不含语义含义的原始设计值。

```css
:root {
  /* Colors */
  --color-gray-50: #F9FAFB;
  --color-gray-900: #111827;
  --color-blue-500: #3B82F6;
  --color-blue-600: #2563EB;

  /* Spacing (4px base) */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-4: 1rem;     /* 16px */
  --space-6: 1.5rem;   /* 24px */

  /* Typography */
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;

  /* Radius */
  --radius-sm: 0.25rem;
  --radius-default: 0.5rem;
  --radius-lg: 0.75rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05);
  --shadow-default: 0 1px 3px rgb(0 0 0 / 0.1);
}
```

## 第 2 层：Semantic Token

引用 primitive 的、基于用途的别名。

```css
:root {
  /* Background */
  --color-background: var(--color-gray-50);
  --color-foreground: var(--color-gray-900);

  /* Primary */
  --color-primary: var(--color-blue-600);
  --color-primary-hover: var(--color-blue-700);

  /* Secondary */
  --color-secondary: var(--color-gray-100);
  --color-secondary-foreground: var(--color-gray-900);

  /* Muted */
  --color-muted: var(--color-gray-100);
  --color-muted-foreground: var(--color-gray-500);

  /* Destructive */
  --color-destructive: var(--color-red-600);
  --color-destructive-foreground: white;

  /* Spacing */
  --spacing-component: var(--space-4);
  --spacing-section: var(--space-6);
}
```

## 第 3 层：Component Token

引用 semantic 层的组件级 token。

```css
:root {
  /* Button */
  --button-bg: var(--color-primary);
  --button-fg: white;
  --button-hover-bg: var(--color-primary-hover);
  --button-padding-x: var(--space-4);
  --button-padding-y: var(--space-2);
  --button-radius: var(--radius-default);

  /* Input */
  --input-bg: var(--color-background);
  --input-border: var(--color-gray-300);
  --input-focus-ring: var(--color-primary);
  --input-padding: var(--space-2) var(--space-3);

  /* Card */
  --card-bg: var(--color-background);
  --card-border: var(--color-gray-200);
  --card-padding: var(--space-4);
  --card-radius: var(--radius-lg);
  --card-shadow: var(--shadow-default);
}
```

## 深色模式

覆盖 semantic token 以实现 dark 主题：

```css
.dark {
  --color-background: var(--color-gray-900);
  --color-foreground: var(--color-gray-50);
  --color-muted: var(--color-gray-800);
  --color-muted-foreground: var(--color-gray-400);
  --color-secondary: var(--color-gray-800);
}
```

## 命名约定

```
--{category}-{item}-{variant}-{state}

示例：
--color-primary           # category-item
--color-primary-hover     # category-item-state
--button-bg-hover         # component-property-state
--space-section-sm        # category-semantic-variant
```

## 类别

| 类别 | 示例 |
|----------|----------|
| color | primary, secondary, muted, destructive |
| space | 1, 2, 4, 8, section, component |
| font-size | xs, sm, base, lg, xl |
| radius | sm, default, lg, full |
| shadow | sm, default, lg |
| duration | fast, normal, slow |

## 文件组织

```
tokens/
├── primitives.css     # 原始值
├── semantic.css       # 语义别名
├── components.css     # component token
└── index.css          # 汇总 import
```

或单文件按层级注释划分：

```css
/* === PRIMITIVES === */
:root { ... }

/* === SEMANTIC === */
:root { ... }

/* === COMPONENTS === */
:root { ... }

/* === DARK MODE === */
.dark { ... }
```

## 从扁平 Token 迁移

迁移前（扁平）：
```css
--button-primary-bg: #2563EB;
--button-secondary-bg: #F3F4F6;
```

迁移后（三层）：
```css
/* Primitive */
--color-blue-600: #2563EB;
--color-gray-100: #F3F4F6;

/* Semantic */
--color-primary: var(--color-blue-600);
--color-secondary: var(--color-gray-100);

/* Component */
--button-bg: var(--color-primary);
--button-secondary-bg: var(--color-secondary);
```

## 与 W3C DTCG 对齐

Token JSON 格式（W3C Design Tokens Community Group）：

```json
{
  "color": {
    "blue": {
      "600": {
        "$value": "#2563EB",
        "$type": "color"
      }
    }
  }
}
```
