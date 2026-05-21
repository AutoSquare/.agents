# 设计路由指南

各设计子技能的使用场景。

## 技能总览

| 技能 | 用途 | 关键文件 |
|------|------|----------|
| brand | 品牌识别、语调、资产 | SKILL.md + 10 篇参考 + 3 个脚本 |
| design-system | 令牌架构、规格 | SKILL.md + 7 篇参考 + 2 个脚本 |
| ui-styling | 组件实现 | SKILL.md + 7 篇参考 + 2 个脚本 |
| logo-design | AI Logo 生成（55 风格、30 色板） | SKILL.md + 4 篇参考 + 2 个脚本 |
| cip-design | 企业识别系统 CIP（50 项交付物） | SKILL.md + 3 篇参考 + 3 个脚本 |
| slides | 集成 Chart.js 的 HTML 演示文稿 | SKILL.md + 4 篇参考 |
| banner-design | 社交/广告/网页/印刷横幅（22 风格） | SKILL.md + 1 篇参考 |
| icon-design | SVG 图标生成（15 风格，Gemini 3.1 Pro） | SKILL.md + 1 篇参考 + 1 个脚本 |

## 按任务类型路由

### 品牌识别任务
**→ brand**

- 定义品牌色彩与字体
- 制定 Logo 使用规范
- 确立品牌语调
- 整理与校验资产
- 创建信息框架
- 审计品牌一致性

### 令牌系统任务
**→ design-system**

- 创建设计令牌 JSON
- 生成 CSS 变量
- 定义组件规格
- 映射令牌到 Tailwind 配置
- 校验代码中的令牌使用
- 记录状态与变体

### 实现任务
**→ ui-styling**

- 添加 shadcn/ui 组件
- 用 Tailwind 类编写样式
- 实现深色模式
- 创建响应式版式
- 构建可访问组件

### Logo 设计任务
**→ logo-design**

- 用 AI（Gemini Nano Banana）创建 Logo
- 检索 Logo 风格、色板、行业指南
- 生成设计简报
- 探索 55+ 风格（极简、复古、奢华、几何等）

### 企业识别系统（CIP）任务
**→ cip-design**

- 生成 CIP 交付物（名片、信纸、标识、车辆、服装等）
- 创建含行业/风格分析的 CIP 简报
- 有/无 Logo 生成样机（Gemini Flash/Pro）
- 由 CIP 样机渲染 HTML 演示文稿

### 演示文稿任务
**→ slides**

- 创建战略性 HTML 演示文稿
- 用 Chart.js 做数据可视化
- 将文案公式应用于幻灯片内容
- 使用版式模式与设计令牌

### 横幅设计任务
**→ banner-design**

- 为社交媒体设计横幅（Facebook、Twitter、LinkedIn、YouTube、Instagram）
- 创建广告横幅（Google Ads、Meta Ads）
- 网站 Hero 横幅与页眉
- 印刷横幅与封面
- 22 种美术指导风格（极简、粗体字、渐变、玻璃拟态等）

### 图标设计任务
**→ icon-design**

- 用 AI（Gemini 3.1 Pro Preview）生成 SVG 图标
- 批量生成多风格图标变体
- 多尺寸导出（16px、24px、32px、48px）
- 15 种风格：outlined、filled、duotone、rounded、sharp、gradient 等
- 12 个类别：导航、操作、通信、媒体、商务、数据

## 按问题类型路由

| 问题 | 技能 |
|------|------|
| 「这里该用什么颜色？」 | brand |
| 「如何为 X 创建令牌？」 | design-system |
| 「如何做一个按钮组件？」 | ui-styling |
| 「这符合品牌吗？」 | brand |
| 「这里该用 CSS 变量吗？」 | design-system |
| 「如何加深色模式？」 | ui-styling |
| 「为我的品牌做个 Logo」 | logo-design |
| 「生成名片样机」 | cip-design |
| 「做个融资路演」 | slides |
| 「设计完整品牌识别包」 | cip-design |
| 「什么 Logo 风格适合我的行业？」 | logo-design |
| 「设计 Facebook 封面」 | banner-design |
| 「为 Google 做广告横幅」 | banner-design |
| 「做网站 Hero 横幅」 | banner-design |
| 「生成设置图标」 | icon-design |
| 「为应用做 SVG 图标集」 | icon-design |
| 「设计图标套装」 | icon-design |

## 多技能工作流

### 新项目启动

```
1. brand → 定义识别
   - 色彩、字体、语调

2. design-system → 创建令牌
   - 原始层、语义层、组件层

3. ui-styling → 实现
   - 配置 Tailwind、添加组件
```

### 设计系统迁移

```
1. brand → 审计现状
   - 提取品牌色、字体

2. design-system → 形式化令牌
   - 建立三层架构

3. ui-styling → 更新代码
   - 替换硬编码值
```

### 组件创建

```
1. design-system → 查阅规格
   - 按钮状态、尺寸、变体

2. ui-styling → 实现
   - 用 shadcn/ui + Tailwind 构建
```

## 技能依赖

```
brand
    ↓（色彩、字体）
design-system
    ↓（令牌、规格）
ui-styling
    ↓（组件）
应用代码
```

## 快捷命令

**品牌：**
```bash
node "$env:USERPROFILE\.cursor\skills\brand\scripts\inject-brand-context.cjs"
node "$env:USERPROFILE\.cursor\skills\brand\scripts\validate-asset.cjs" <path>
```

**令牌：**
```bash
node "$env:USERPROFILE\.cursor\skills\design-system\scripts\generate-tokens.cjs" -c tokens.json
node "$env:USERPROFILE\.cursor\skills\design-system\scripts\validate-tokens.cjs" -d src/
```

**组件：**
```bash
npx shadcn@latest add button card input
```

## 何时组合多个技能

**八个全用** 当：
- 从零搭建完整品牌包（Logo → CIP → 演示文稿）

**brand + design-system + ui-styling** 当：
- 设计系统搭建与落地实现

**logo-design + cip-design** 当：
- 含交付物样机的完整品牌识别包

**logo-design + cip-design + slides** 当：
- 品牌路演：生成 Logo、CIP 样机、制作演示文稿

**banner-design + brand** 当：
- 全平台品牌化社交横幅

**icon-design + design-system** 当：
- 与设计令牌、组件规格一致的自定义图标集

**brand + design-system** 当：
- 仅定义设计语言、不涉及实现

**design-system + ui-styling** 当：
- 在代码中落地既有品牌
- 构建组件库
