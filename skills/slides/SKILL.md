---
name: ckm:slides
description: 创建战略性 HTML 演示文稿，集成 Chart.js、设计令牌、响应式版式、文案公式与情境化幻灯片策略。
argument-hint: "[主题] [幻灯片数量]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# 幻灯片

基于 Chart.js 数据可视化的战略性 HTML 演示文稿设计。

<args>$ARGUMENTS</args>

## 适用场景

- 营销演示与融资路演
- 集成 Chart.js 的数据驱动幻灯片
- 基于版式模式的战略性幻灯片设计
- 经文案公式优化的演示文稿内容

## 子命令

| 子命令 | 说明 | 参考文档 |
|--------|------|----------|
| `create` | 创建战略性演示文稿幻灯片 | `references/create.md` |

## 参考文档（知识库）

| 主题 | 文件 |
|------|------|
| 版式模式 | `references/layout-patterns.md` |
| HTML 模板 | `references/html-template.md` |
| 文案公式 | `references/copywriting-formulas.md` |
| 幻灯片策略 | `references/slide-strategies.md` |

## 路由规则

1. 从 `$ARGUMENTS` 解析子命令（首词）
2. 加载对应的 `references/{subcommand}.md`
3. 使用剩余参数执行
