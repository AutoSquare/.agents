更新品牌色彩、字体与风格，并自动同步至全部设计系统文件。

<args>$ARGUMENTS</args>

## 概述

本命令系统性地更新：
1. `docs/brand-guidelines.md` — 可读性品牌文档
2. `assets/design-tokens.json` — 令牌权威来源
3. `assets/design-tokens.css` — 生成的 CSS 变量

## 工作流

### 步骤 1：收集品牌输入

使用 `AskUserQuestion` 收集：

**主题选择：**
- 主题名称（如 "Ocean Professional"、"Electric Creative"、"Forest Calm"）

**主色：**
- 颜色名称（如 "Ocean Blue"、"Coral"、"Forest Green"）
- 十六进制值（如 #3B82F6）

**辅色：**
- 颜色名称（如 "Golden Amber"、"Electric Purple"）
- 十六进制值

**强调色：**
- 颜色名称（如 "Emerald"、"Neon Mint"）
- 十六进制值

**品牌氛围（用于 AI 图像生成）：**
- 氛围关键词（如 "professional, trustworthy, premium" 或 "bold, creative, energetic"）

### 步骤 2：更新品牌指南

编辑 `docs/brand-guidelines.md`：

1. **快速参考表** — 更新颜色名称与十六进制值
2. **品牌概念** — 更新主题名称与描述
3. **色板** — 更新主色、辅色、强调色及色阶
4. **AI 图像生成** — 更新基础提示词、关键词与氛围描述

### 步骤 3：同步至设计令牌

运行同步脚本：
```bash
node "$env:USERPROFILE\.cursor\skills\brand\scripts\sync-brand-to-tokens.cjs"
```

将执行：
- 以新颜色名称与数值更新 `assets/design-tokens.json`
- 重新生成 `assets/design-tokens.css` 中的 CSS 变量

### 步骤 4：验证同步

确认全部文件已更新：
```bash
# Check brand context extraction
node "$env:USERPROFILE\.cursor\skills\brand\scripts\inject-brand-context.cjs" --json | head -30

# Check CSS variables
grep "primary" assets/design-tokens.css | head -5
```

### 步骤 5：输出报告

汇总如下：
- 主题：[name]
- 主色：[name]（[hex]）
- 辅色：[name]（[hex]）
- 强调色：[name]（[hex]）
- 已更新文件：brand-guidelines.md、design-tokens.json、design-tokens.css

## 修改文件

| 文件 | 用途 |
|------|------|
| `docs/brand-guidelines.md` | 可读性品牌文档 |
| `assets/design-tokens.json` | 令牌定义（primitive→semantic→component） |
| `assets/design-tokens.css` | UI 组件 CSS 变量 |

## 联动技能

- `brand` — 品牌上下文提取与同步
- `design-system` — 令牌生成

## 示例

```bash
# Interactive mode
/brand:update

# With theme hint
/brand:update "Ocean Professional"

# Quick preset
/brand:update "midnight purple"
```

## 颜色预设

若用户指定预设名称，使用以下默认值：

| 预设 | 主色 | 辅色 | 强调色 |
|------|------|------|--------|
| ocean-professional | #3B82F6 Ocean Blue | #F59E0B Golden Amber | #10B981 Emerald |
| electric-creative | #FF6B6B Coral | #9B5DE5 Electric Purple | #00F5D4 Neon Mint |
| forest-calm | #059669 Forest Green | #92400E Warm Brown | #FBBF24 Sunlight |
| midnight-purple | #7C3AED Violet | #EC4899 Pink | #06B6D4 Cyan |
| sunset-warm | #F97316 Orange | #DC2626 Red | #FACC15 Yellow |

## 重要事项

- **始终同步三个文件** — 禁止仅更新 brand-guidelines.md
- **验证提取结果** — 更新后运行 inject-brand-context.cjs 确认
- **测试图像生成** — 可选生成测试图像以验证品牌应用效果
