---
name: to-prd
description: 将当前会话语境整理为 PRD 并发布到项目问题跟踪。用于用户想把当前上下文落成 PRD 时。
---

本技能取用当前会话与对仓库的理解，产出 PRD。**不要访谈用户** —— 只做你已经知道的综合。

若无问题跟踪与分拣标签词典，本应已配置 —— 请先运行 **setup-matt-pocock-skills** 技能。

## 流程

1. 若尚未探索仓库，请先探索当前代码状态。通篇使用项目领域术语，并尊重你所触及区域内的 ADR。

2. 草拟实现所需的、将被新建或修改的主要模块。积极寻找可独立测试、可封装的深层模块。

相对浅层模块而言，深层模块在简单、较少变动、且可测试的接口后封装了大量能力。

与用户确认这些模块是否符合预期；并确认要在哪些模块上编写测试。

3. 使用下方模板撰写 PRD，然后发布到项目问题跟踪。应用 `ready-for-agent` 分拣标签 —— 无需再做额外分拣。

<prd-template>

## 问题陈述（Problem Statement）

从用户视角描述其面临的问题。

## 方案（Solution）

从用户视角描述解决方案。

## 用户故事（User Stories）

**很长**且**编号**的用户故事清单。每条格式：

1. As an <参与者>, I want <能力>, so that <收益>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

列表应极尽详尽，覆盖该功能的各个方面。

## 实现决策（Implementation Decisions）

已做出的实现层面的决策清单，例如：

- 将新建 / 修改的模块
- 这些模块上将修改的接口
- 开发者给出的技术澄清
- 架构决策
- Schema 变更
- API 合约
- 具体交互说明

不要写具体文件路径或代码片段，它们会很快过期。

例外：若原型产出的片段在状态机、reducer、schema、类型形状等方面比长篇叙述更精确地编码了决策，可内嵌在相关决策中，并简述来自原型；只保留承载决策的精华部分 —— 不是完整可运行 demo。

## 测试决策（Testing Decisions）

测试相关决策清单，包括：

- 何谓好测（仅测外部行为，不测实现细节）
- 将要测试哪些模块
- 测试先例（仓库中相似的测试）

## 范围外（Out of Scope）

写明本 PRD 不包含的内容。

## 附注（Further Notes）

关于该功能的其他说明。

</prd-template>
