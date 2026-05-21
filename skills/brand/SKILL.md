---
name: ckm:brand
description: 品牌调性、视觉识别、信息框架、资产管理与一致性规范。在用户需要品牌内容、语气指南、营销素材、品牌合规或风格手册时使用。
argument-hint: "[update|review|create] [args]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# 品牌

品牌识别、调性、信息传达、资产管理与一致性框架。

## 适用范围

- 品牌调性定义与内容语气指导
- 视觉识别标准与风格手册编制
- 信息框架搭建
- 品牌一致性审查与审计
- 资产组织、命名与审批
- 色板管理与字体规范

## 快速开始

**向提示词注入品牌上下文：**
```bash
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json
```

**校验资产：**
```bash
node scripts/validate-asset.cjs <asset-path>
```

**提取或比对颜色：**
```bash
node scripts/extract-colors.cjs --palette
node scripts/extract-colors.cjs <image-path>
```

## 品牌同步工作流

```bash
# 1. 编辑 docs/brand-guidelines.md（或使用 /brand update）
# 2. 同步至设计令牌
node scripts/sync-brand-to-tokens.cjs
# 3. 验证
node scripts/inject-brand-context.cjs --json | head -20
```

**同步涉及文件：**
- `docs/brand-guidelines.md` → 权威来源
- `assets/design-tokens.json` → 令牌定义
- `assets/design-tokens.css` → CSS 变量

## 子命令

| 子命令 | 说明 | 参考文档 |
|--------|------|----------|
| `update` | 更新品牌识别并同步至全部设计系统 | `references/update.md` |

## 参考文档

| 主题 | 文件 |
|------|------|
| 调性框架 | `references/voice-framework.md` |
| 视觉识别 | `references/visual-identity.md` |
| 信息框架 | `references/messaging-framework.md` |
| 一致性 | `references/consistency-checklist.md` |
| 指南模板 | `references/brand-guideline-template.md` |
| 资产组织 | `references/asset-organization.md` |
| 色板管理 | `references/color-palette-management.md` |
| 字体规范 | `references/typography-specifications.md` |
| Logo 使用 | `references/logo-usage-rules.md` |
| 审批清单 | `references/approval-checklist.md` |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/inject-brand-context.cjs` | 提取品牌上下文供提示词注入 |
| `scripts/sync-brand-to-tokens.cjs` | 同步 brand-guidelines.md → design-tokens.json/css |
| `scripts/validate-asset.cjs` | 校验资产命名、尺寸与格式 |
| `scripts/extract-colors.cjs` | 提取颜色并与色板比对 |

## 模板

| 模板 | 用途 |
|------|------|
| `templates/brand-guidelines-starter.md` | 新品牌完整入门模板 |

## 路由

1. 从 `$ARGUMENTS` 解析子命令（首词）
2. 加载对应 `references/{subcommand}.md`
3. 使用剩余参数执行
