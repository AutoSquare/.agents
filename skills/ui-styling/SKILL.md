---
name: ckm:ui-styling
description: 使用 shadcn/ui 组件（基于 Radix UI + Tailwind）、Tailwind CSS 实用类优先样式与 Canvas 视觉设计，构建美观且可访问的用户界面。适用于搭建 UI、实现设计系统、创建响应式布局、添加可访问组件（Dialog、Dropdown、Form、Table）、定制主题与配色、实现深色模式、生成视觉设计与海报，或在应用中建立一致的样式规范。
argument-hint: "[component or layout]"
license: MIT
metadata:
  author: claudekit
  version: "1.0.0"
---

# UI 样式技能

综合技能，用于结合 shadcn/ui 组件、Tailwind CSS 实用类样式与 Canvas 视觉设计系统，创建美观且可访问的用户界面。

## 参考资源

- shadcn/ui: https://ui.shadcn.com/llms.txt
- Tailwind CSS: https://tailwindcss.com/docs

## 适用场景

在以下情况使用本技能：
- 基于 React 框架（Next.js、Vite、Remix、Astro）构建 UI
- 实现可访问组件（Dialog、Form、Table、导航）
- 采用实用类优先的 CSS 样式方案
- 创建响应式、移动优先的布局
- 实现深色模式与主题定制
- 基于一致 Design Token 构建设计系统
- 生成视觉设计、海报或品牌物料
- 快速原型验证，获得即时视觉反馈
- 添加复杂 UI 模式（Data Table、Chart、Command Palette）

## 核心技术栈

### 组件层：shadcn/ui
- 基于 Radix UI 原语提供预置可访问组件
- 复制粘贴式分发（组件源码位于你的代码库中）
- TypeScript 优先，具备完整类型安全
- 可组合原语，便于构建复杂 UI
- 基于 CLI 的安装与管理

### 样式层：Tailwind CSS
- 实用类优先的 CSS 框架
- 构建时处理，零运行时开销
- 移动优先的响应式设计
- 一致的 Design Token（颜色、间距、排版）
- 自动剔除未使用样式

### 视觉设计层：Canvas
- 博物馆级视觉构图
- 以设计哲学驱动的创作方法
- 精密的视觉传达
- 文字极简、视觉冲击最大化
- 系统化模式与精致美学

## 快速开始

### 组件 + 样式配置

**安装 shadcn/ui 与 Tailwind：**
```bash
npx shadcn@latest init
```

CLI 会引导选择框架、TypeScript、路径与主题偏好，并同时配置 shadcn/ui 与 Tailwind CSS。

**添加组件：**
```bash
npx shadcn@latest add button card dialog form
```

**在组件中使用实用类样式：**
```tsx
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export function Dashboard() {
  return (
    <div className="container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Analytics</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">View your metrics</p>
          <Button variant="default" className="w-full">
            View Details
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
```

### 备选方案：仅 Tailwind 配置

**Vite 项目：**
```bash
npm install -D tailwindcss @tailwindcss/vite
```

```javascript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default { plugins: [tailwindcss()] }
```

```css
/* src/index.css */
@import "tailwindcss";
```

## 组件库指南

**完整组件目录，含用法模式、安装说明与组合示例。**

参见：`references/shadcn-components.md`

涵盖：
- 表单与输入组件（Button、Input、Select、Checkbox、Date Picker、Form 校验）
- 布局与导航（Card、Tabs、Accordion、Navigation Menu）
- 浮层与对话框（Dialog、Drawer、Popover、Toast、Command）
- 反馈与状态（Alert、Progress、Skeleton）
- 展示组件（Table、Data Table、Avatar、Badge）

## 主题与定制

**主题配置、CSS 变量、深色模式实现与组件定制。**

参见：`references/shadcn-theming.md`

涵盖：
- 使用 next-themes 配置深色模式
- CSS 变量体系
- 颜色定制与调色板
- 组件变体定制
- 主题切换实现

## 可访问性模式

**ARIA 模式、键盘导航、屏幕阅读器支持与可访问组件用法。**

参见：`references/shadcn-accessibility.md`

涵盖：
- Radix UI 可访问性能力
- 键盘导航模式
- 焦点管理
- 屏幕阅读器播报
- 表单校验可访问性

## Tailwind 实用类

**布局、间距、排版、颜色、边框与阴影等核心实用类。**

参见：`references/tailwind-utilities.md`

涵盖：
- 布局实用类（Flexbox、Grid、定位）
- 间距体系（padding、margin、gap）
- 排版（字号、字重、对齐、行高）
- 颜色与背景
- 边框与阴影
- 任意值（Arbitrary Values）自定义样式

## 响应式设计

**移动优先断点、响应式实用类与自适应布局。**

参见：`references/tailwind-responsive.md`

涵盖：
- 移动优先方法
- 断点体系（sm、md、lg、xl、2xl）
- 响应式实用类模式
- Container Queries
- Max-width 查询
- 自定义断点

## Tailwind 定制

**配置文件结构、自定义实用类、插件与主题扩展。**

参见：`references/tailwind-customization.md`

涵盖：
- 使用 @theme 指令定义自定义 Token
- 自定义颜色与字体
- 间距与断点扩展
- 创建自定义实用类
- 自定义变体
- 层级组织（@layer base、components、utilities）
- 使用 @apply 提取组件样式

## 视觉设计系统

**基于 Canvas 的设计哲学、视觉传达原则与精密构图。**

参见：`references/canvas-design-system.md`

涵盖：
- 设计哲学方法
- 视觉优先于文字
- 系统化模式与构图
- 色彩、形态与空间设计
- 极简文字融入
- 博物馆级执行标准
- 多页设计系统

## 实用脚本

**用于组件安装与配置生成的 Python 自动化工具。**

### shadcn_add.py
添加 shadcn/ui 组件并处理依赖：
```bash
python "$env:USERPROFILE\.cursor\skills\ui-styling\scripts\shadcn_add.py" button card dialog
```

### tailwind_config_gen.py
生成带自定义主题的 tailwind.config.js：
```bash
python "$env:USERPROFILE\.cursor\skills\ui-styling\scripts\tailwind_config_gen.py" --colors brand:blue --fonts display:Inter
```

## 最佳实践

1. **组件组合**：由简单、可组合的原语构建复杂 UI
2. **实用类优先**：直接使用 Tailwind 类；仅在真正重复时提取组件
3. **移动优先响应式**：从移动端样式起步，再叠加响应式变体
4. **可访问性优先**：利用 Radix UI 原语，添加焦点状态，使用语义化 HTML
5. **Design Token**：使用一致的间距刻度、调色板与排版体系
6. **深色模式一致性**：为所有主题元素应用 dark 变体
7. **性能**：利用自动 CSS 裁剪，避免动态类名
8. **TypeScript**：充分利用类型安全以提升开发体验
9. **视觉层级**：以构图引导注意力，有意图地使用间距与颜色
10. **专业工艺**：细节决定品质——将 UI 视为一门工艺

## 参考导航

**组件库**
- `references/shadcn-components.md` — 完整组件目录
- `references/shadcn-theming.md` — 主题与定制
- `references/shadcn-accessibility.md` — 可访问性模式

**样式体系**
- `references/tailwind-utilities.md` — 核心实用类
- `references/tailwind-responsive.md` — 响应式设计
- `references/tailwind-customization.md` — 配置与扩展

**视觉设计**
- `references/canvas-design-system.md` — 设计哲学与 Canvas 工作流

**自动化**
- `scripts/shadcn_add.py` — 组件安装
- `scripts/tailwind_config_gen.py` — 配置生成

## 常见模式

**带校验的表单：**
```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export function LoginForm() {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" }
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-6">
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" className="w-full">Sign In</Button>
      </form>
    </Form>
  )
}
```

**响应式布局与深色模式：**
```tsx
<div className="min-h-screen bg-white dark:bg-gray-900">
  <div className="container mx-auto px-4 py-8">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Content
          </h3>
        </CardContent>
      </Card>
    </div>
  </div>
</div>
```

## 外部资源

- shadcn/ui 文档: https://ui.shadcn.com
- Tailwind CSS 文档: https://tailwindcss.com
- Radix UI: https://radix-ui.com
- Tailwind UI: https://tailwindui.com
- Headless UI: https://headlessui.com
- v0（AI UI 生成器）: https://v0.dev
