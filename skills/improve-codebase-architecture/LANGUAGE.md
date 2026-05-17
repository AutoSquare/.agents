# Language（措辞）

本技能一切建议共用这套词汇。**精确使用** —— 勿擅自换成「组件」「服务」「API」「边界」。措辞一致本就是目的。

## 术语

**Module（模块）**
具备接口与实现的一切。刻意与规模无关 —— 小到函数，大到贯穿多层的切片都适用。
_不宜_: unit、component、service。

**Interface（接口）**
调用方要 **正确** 使用模块所必须了解的 **全部**：类型签名、不变量、次序约束、错误形态、必填配置与性能特征。
_不宜_: API、signature（过窄——多指仅靠类型表达的表层）。

**Implementation（实现）**
模块内部的代码本体。有别于 **Adapter**：某物可以是小适配器大实现（Postgres repo），也可以是大适配器小实现（内存 fake）。谈接缝时用「adapter」，否则用「implementation」。

**Depth（深度）**
体现在接口上的杠杆 —— 调用方（或测试）每学习一单位接口表面，可驱动多少行为。模块 **deep** 指大量行为藏在小型接口后；**shallow** 指接口复杂度逼近实现复杂度。

**Seam（接缝）** _（Michael Feathers）_
可以在 **不就地编辑该处代码**的情况下改变行为的地点 —— 模块接口 **坐落的位置**。接缝放哪本身是设计决策，与背后塞什么分立。
_不宜_: boundary（易与 DDD bounded context 混淆）。

**Adapter（适配器）**
在具体接缝处满足接口的具象物。描述 **角色**（占哪个槽），不描述体积（内里多大）。

**Leverage（杠杆）**
深度给调用方的东西：单位接口要学的东西换更多能力；一份实现在 N 个调用点与 M 个测试中摊销回报。

**Locality（局部性）**
深度给维护者的东西：改动、缺陷、知识与验证集中到一处而非散在调用方。修一次，全局收益。

## 原则

- **Depth 是接口的属性，而非实现的属性。** Deep 模块内部可由许多小、mock 友好、可替换的部分组成 —— 它们不构成对外接口的一部分。模块可有 **internal seams**（实现私有，自有测试使用）外加对外的 **external seam**。
- **Deletion test.** 想象删掉模块：复杂度凭空消失 ⇒ 没在藏东西（穿堂）；复杂度分散到 N 个调用方 ⇒ 之前在扛事。
- **The interface is the test surface.** 调用方与测试跨同一接缝。若想 **越过**接口去测 ⇒ 模块形态可能错了。
- **One adapter ⇒ 假想接缝；Two adapters ⇒ 真有接缝。** 除非接缝两侧确实有变化，勿引入接缝。

## 关系

- 一个 **Module** 恰有一个 **Interface**（调用方与测试看到的表面）。
- **Depth** 是 **Module** 相对其 **Interface** 的性质。
- **Seam** 是 **Module** 的 **Interface** 坐落之处。
- **Adapter** 位于 **Seam**，并满足 **Interface**。
- **Depth** 为调用方产生 **Leverage**，为维护者产生 **Locality**。

## 弃用的提法

- **用实现行数 / 接口行数比度量深度（Ousterhout 旧提法）**：会奖励把实现灌水。我们以 depth-as-leverage 取代。
- **把「接口」收窄成 TypeScript `interface` 关键字或类的 public 方法**：过窄 —— 此处 interface 涵盖调用方须知的每一条事实。
- **「Boundary」**：易与 DDD bounded context 混淆。说 **seam** 或 **interface**。
