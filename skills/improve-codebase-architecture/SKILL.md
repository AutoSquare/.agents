---
name: improve-codebase-architecture
description: 结合 CONTEXT.md 中的领域用语与 docs/adr/ 中的既定决策，发现代码库的「加深」机会。在用户想改进架构、寻找重构切口、收紧高耦合模块、或提升可测性与 AI 可导航性时使用。
---

# Improve Codebase Architecture（改进代码库架构）

呈现架构摩擦，并提案 **deepening opportunities（加深机会）** —— 把浅层模块加深为深层模块的重构。目标是可测试性与可被 AI 导航。

## 术语表

每条建议中 **精确**使用下列词 —— 不要漂移去说「组件」「服务」「API」「边界」。完整定义见 [LANGUAGE.md](LANGUAGE.md)。

- **Module（模块）** —— 有接口与实现的任何东西（函数、类、包、切片）。
- **Interface（接口）** —— 调用方正确使用模块所需的 **一切**：类型、不变量、错误形态、次序、配置。不仅是类型签名。
- **Implementation（实现）** —— 其内部代码。
- **Depth（深度）** —— 体现在接口上的杠杆：大量行为藏在小型接口背后。**Deep（深）** = 杠杆高。**Shallow（浅）** = 接口复杂度几乎与实现持平。
- **Seam（接缝）** —— 接口坐落之处；可不改原位即可改变行为的位置。（用这个词，不要说「boundary」。）
- **Adapter（适配器）** —— 在接缝处满足接口的具体物。
- **Leverage（杠杆）** —— 深度带给调用方的东西。
- **Locality（局部性）** —— 深度带给维护者的东西：改动、缺陷、知识集中到一处。

关键原则（完整列表亦在 [LANGUAGE.md](LANGUAGE.md)）：

- **Deletion test（删除测验）**：想象删掉该模块。若复杂度随之消失，它是穿堂风；若在 N 个调用方复燃，则在承担职责。
- **The interface is the test surface（接口即测试切面）。**
- **One adapter = hypothetical seam；Two adapters = real seam.**

本技能 **受**项目领域模型 **启发**：领域语言为好接缝命名；ADR 记下本技能不应重开的决策。

## 流程

### 1. 探索

先读项目的领域术语表与将触及区域内的 ADR。

再用 Agent 工具 `subagent_type=Explore` 漫步代码库。勿死守启发式 —— 有机探索并记录感到摩擦之处：

- 理解一个概念是否要在许多小模块间跳来跳去？
- 何处模块 **浅** —— 接口复杂度几乎等价实现？
- 是否为了可测而把纯函数抽出来，但真正 bug 藏在调用编排里（缺少 **locality**）？
- 何处紧耦合模块在接缝渗露？
- 哪些区域未测或现有接口难以测？

对可疑浅模块做 **删除测验**：删掉它会 **集中** 复杂度，还是仅 **挪动**？“会集中”即你要的信号。

### 2. 展示候选

以编号列出加深机会。每条包含：

- **Files** —— 涉及哪些文件 / 模块
- **Problem** —— 当前架构为何制造摩擦
- **Solution** —— 将如何改变的通俗说明
- **Benefits** —— 用 locality 与 leverage 解释，亦说明测试如何改善

**领域概念用 CONTEXT.md 词汇；架构措辞用 [LANGUAGE.md](LANGUAGE.md)**。若 `CONTEXT.md` 定义了「Order」，就说「订单摄入模块」，而非「FooBarHandler」，也非「Order 微服务」。

**与 ADR 冲突**：仅在摩擦足够大到值得重审时提出；清楚标注（如 _「与 ADR-0007 相悖 —— 但值得重开，因为…」_）。不要罗列 ADR 禁掉的每一个空想重构。

勿在此阶段 Proposal 接口。反问用户：「你想深入哪一个？」

### 3. 质询循环

用户选定候选后进入质询。与其一起走设计树 —— 约束、依赖、加深后模块的形态、接缝背后是什么、哪些测试仍可存活。

决议显现时的副作用就地发生：

- **要把加深模块冠以 CONTEXT.md 尚未收录的概念？** 把术语加入 `CONTEXT.md` —— 纪律同 **grill-with-docs** 技能（见 [CONTEXT-FORMAT.md](../grill-with-docs/CONTEXT-FORMAT.md)）。文件不存在则惰式创建。
- **会话中某词变清晰？** 当即更新 `CONTEXT.md`。
- **用户以承载理由拒绝候选？** 可提议 ADR，措辞类似：_「要不要记成 ADR，免得未来架构检视再提同样的建议？」_ 仅当理由真的需要被未来探索者读到才提议 —— 跳过「暂时不值」之类 ephemeral 理由以及自明理由。格式见 [ADR-FORMAT.md](../grill-with-docs/ADR-FORMAT.md)。
- **想为加深模块探索备选接口？** 见 [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md)。
