# shadcn/ui 可访问性模式

ARIA 模式、键盘导航、屏幕阅读器支持与可访问组件用法。

## 基础：Radix UI 原语

shadcn/ui 基于 Radix UI 原语构建——无样式、可访问组件，遵循 WAI-ARIA 设计模式。

优势：
- 内置键盘导航
- 屏幕阅读器播报
- 焦点管理
- 自动应用 ARIA 属性
- 经可访问性标准测试

## 键盘导航

### 焦点管理

**焦点可见状态：**
```tsx
<Button className="focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
  Accessible Button
</Button>
```

**跳过导航至主内容：**
```tsx
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2">
  Skip to content
</a>

<main id="main-content">
  {/* Content */}
</main>
```

### Dialog / Modal 导航

Dialog 通过 Radix Dialog 原语自动锁定焦点：

```tsx
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    {/* 焦点锁定于此 */}
    <input />  {/* 自动聚焦 */}
    <Button>Action</Button>
    {/* Esc 关闭，Tab 导航 */}
  </DialogContent>
</Dialog>
```

特性：
- 焦点锁定在 Dialog 内
- Esc 键关闭
- Tab 在可聚焦元素间循环
- 关闭后焦点回到触发器

### Dropdown / Menu 导航

```tsx
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

<DropdownMenu>
  <DropdownMenuTrigger>Open</DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Settings</DropdownMenuItem>
    <DropdownMenuItem>Logout</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

键盘快捷键：
- `Space/Enter`：打开菜单
- `Arrow Up/Down`：在选项间导航
- `Esc`：关闭菜单
- `Tab`：关闭并移动焦点

### Command Palette 导航

```tsx
import { Command } from "@/components/ui/command"

<Command>
  <CommandInput placeholder="Search..." />
  <CommandList>
    <CommandGroup heading="Suggestions">
      <CommandItem>Calendar</CommandItem>
      <CommandItem>Search</CommandItem>
    </CommandGroup>
  </CommandList>
</Command>
```

特性：
- 输入过滤
- 方向键导航
- Enter 选择
- Esc 关闭

## 屏幕阅读器支持

### 语义化 HTML

使用正确的 HTML 元素：

```tsx
// 推荐：语义化 HTML
<button>Click me</button>
<nav><a href="/">Home</a></nav>

// 避免：div 堆砌
<div onClick={handler}>Click me</div>
```

### ARIA 标签

**为交互元素添加标签：**
```tsx
<Button aria-label="Close dialog">
  <X className="h-4 w-4" />
</Button>

<Input aria-label="Email address" type="email" />
```

**描述元素：**
```tsx
<Button aria-describedby="delete-description">
  Delete Account
</Button>
<p id="delete-description" className="sr-only">
  This action permanently deletes your account and cannot be undone
</p>
```

### 仅屏幕阅读器可见文本

使用 `sr-only` 类隐藏视觉文本、保留朗读内容：

```tsx
<Button>
  <Trash className="h-4 w-4" />
  <span className="sr-only">Delete item</span>
</Button>

// sr-only 的 CSS
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

### Live Region

播报动态内容：

```tsx
<div aria-live="polite" aria-atomic="true">
  {message}
</div>

// 紧急更新
<div aria-live="assertive">
  {error}
</div>
```

Toast 组件包含 Live Region：
```tsx
const { toast } = useToast()

toast({
  title: "Success",
  description: "Profile updated"
})
// 自动向屏幕阅读器播报
```

## 表单可访问性

### 标签与描述

**始终为输入框添加标签：**
```tsx
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

<div>
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" />
</div>
```

**添加描述：**
```tsx
import { FormDescription, FormMessage } from "@/components/ui/form"

<FormItem>
  <FormLabel>Username</FormLabel>
  <FormControl>
    <Input {...field} />
  </FormControl>
  <FormDescription>
    Your public display name
  </FormDescription>
  <FormMessage />  {/* 错误信息 */}
</FormItem>
```

### 错误处理

向屏幕阅读器播报错误：

```tsx
<FormField
  control={form.control}
  name="email"
  render={({ field, fieldState }) => (
    <FormItem>
      <FormLabel>Email</FormLabel>
      <FormControl>
        <Input
          {...field}
          aria-invalid={!!fieldState.error}
          aria-describedby={fieldState.error ? "email-error" : undefined}
        />
      </FormControl>
      <FormMessage id="email-error" />
    </FormItem>
  )}
/>
```

### 必填字段

标明必填字段：

```tsx
<Label htmlFor="name">
  Name <span className="text-destructive">*</span>
  <span className="sr-only">(required)</span>
</Label>
<Input id="name" required />
```

### Fieldset 与 Legend

分组相关字段：

```tsx
<fieldset>
  <legend className="text-lg font-semibold mb-4">
    Contact Information
  </legend>
  <div className="space-y-4">
    <FormField name="email" />
    <FormField name="phone" />
  </div>
</fieldset>
```

## 组件特定模式

### Accordion

```tsx
import { Accordion } from "@/components/ui/accordion"

<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>
      {/* 自动包含 aria-expanded、aria-controls */}
      Is it accessible?
    </AccordionTrigger>
    <AccordionContent>
      {/* 折叠时隐藏，展开时播报 */}
      Yes. Follows WAI-ARIA design pattern.
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

### Tabs

```tsx
import { Tabs } from "@/components/ui/tabs"

<Tabs defaultValue="account">
  <TabsList role="tablist">
    {/* 方向键导航，Space/Enter 激活 */}
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    {/* 未选中时隐藏，aria-labelledby 关联触发器 */}
    Account content
  </TabsContent>
</Tabs>
```

### Select

```tsx
import { Select } from "@/components/ui/select"

<Select>
  <SelectTrigger aria-label="Choose theme">
    <SelectValue placeholder="Theme" />
  </SelectTrigger>
  <SelectContent>
    {/* 支持键盘导航，向屏幕阅读器播报 */}
    <SelectItem value="light">Light</SelectItem>
    <SelectItem value="dark">Dark</SelectItem>
  </SelectContent>
</Select>
```

### Checkbox 与 Radio

```tsx
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

<div className="flex items-center space-x-2">
  <Checkbox id="terms" aria-describedby="terms-description" />
  <Label htmlFor="terms">Accept terms</Label>
</div>
<p id="terms-description" className="text-sm text-muted-foreground">
  You agree to our Terms of Service and Privacy Policy
</p>
```

### Alert

```tsx
import { Alert } from "@/components/ui/alert"

<Alert role="alert">
  {/* 立即向屏幕阅读器播报 */}
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Your session has expired
  </AlertDescription>
</Alert>
```

## 颜色对比度

确保文字与背景之间有足够的对比度。

**WCAG 要求：**
- **AA**：普通文字 4.5:1，大号文字 3:1
- **AAA**：普通文字 7:1，大号文字 4.5:1

**检查默认值：**
```tsx
// 推荐：高对比度
<p className="text-gray-900 dark:text-gray-100">Text</p>

// 避免：低对比度
<p className="text-gray-400 dark:text-gray-600">Hard to read</p>
```

**弱化文字：**
```tsx
// 使用语义化 muted foreground
<p className="text-muted-foreground">
  Secondary text with accessible contrast
</p>
```

## 焦点指示器

始终提供可见的焦点指示：

**默认焦点环：**
```tsx
<Button className="focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
  Button
</Button>
```

**自定义焦点样式：**
```tsx
<a href="#" className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:underline">
  Link
</a>
```

**不要移除焦点样式：**
```tsx
// 避免
<button className="focus:outline-none">Bad</button>

// 改用 focus-visible
<button className="focus-visible:ring-2">Good</button>
```

## 动效与动画

尊重减少动效偏好：

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

在组件中：
```tsx
<div className="transition-all motion-reduce:transition-none">
  Respects user preference
</div>
```

## 测试清单

- [ ] 所有交互元素可通过键盘访问
- [ ] 焦点指示器可见
- [ ] 屏幕阅读器正确播报全部内容
- [ ] 表单错误已播报并关联
- [ ] 颜色对比度满足 WCAG AA
- [ ] 使用语义化 HTML
- [ ] 纯图标按钮提供 ARIA 标签
- [ ] Modal / Dialog 焦点锁定正常
- [ ] Dropdown / Select 支持键盘导航
- [ ] Live Region 播报更新
- [ ] 尊重减少动效偏好
- [ ] 浏览器缩放至 200% 仍可用
- [ ] Tab 顺序合理
- [ ] 提供跳过导航链接

## 工具

**测试工具：**
- Lighthouse 可访问性审计
- axe DevTools 浏览器扩展
- NVDA / JAWS 屏幕阅读器
- 纯键盘导航测试
- 颜色对比度检测（Contrast Ratio、WebAIM）

**自动化测试：**
```bash
npm install -D @axe-core/react
```

```tsx
import { useEffect } from 'react'

if (process.env.NODE_ENV === 'development') {
  import('@axe-core/react').then((axe) => {
    axe.default(React, ReactDOM, 1000)
  })
}
```
