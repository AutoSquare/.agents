# Deepening（加深）

在已知依赖前提下，如何把一簇浅模块安全加深。前置词汇见 [LANGUAGE.md](LANGUAGE.md) —— **module**、**interface**、**seam**、**adapter**。

## 依赖类别

评估加深候选时对其依赖归类。类别决定如何通过接缝测试加深后的模块。

### 1. In-process（进程内）

纯计算、内存状态、无 I/O。永远可加深 —— 合并模块并直接透过新接口测试。无需适配器。

### 2. Local-substitutable（可本地替换）

存在本地测试替身（Postgres 的 PGLite、内存文件系统等）。若替身可得则可加深。加深模块在测试套件中跑替身；接缝对内；模块对外接口不出现 port。

### 3. Remote but owned（远程但自有）（Ports & Adapters）

你自己的跨网络服务（微服务、内部 API）。在接缝定义 **port**（接口）；加深模块拥有逻辑；传输以 **adapter** 注入。测试用内存 adapter；生产用 HTTP/gRPC/队列 adapter。

建议句式类似：_「在接缝定义 port；生产 HTTP adapter、测试内存 adapter，使逻辑常驻单一 deep module，即便跨网部署。」_

### 4. True external（真外部）（Mock）

不可控三方（Stripe、Twilio 等）。加深模块将外部依赖作为注入 port；测试提供 mock adapter。

## 接缝纪律

- **One adapter ⇒ 假想接缝；Two adapters ⇒ 真接缝。** 除非至少两套 adapter（通常为生产 + 测试），勿引入 port。单适配器接缝只是迂回。
- **Internal vs external seams.** Deep 可有内部接缝（实现私有）与对外接缝。不要因为测试使用就把内部接缝暴露进对外接口。

## 测试策略：替换而非叠层

- 浅模块上的旧单测一旦被加深模块接口级测试取代 —— **删除**。
- 在加深模块接口写新测试。**接口即测试切面。**
- 断言透过接口的可观察结果，而非内部状态。
- 测试应扛住内部重构 —— 描述行为而非实现。若实现一改测试就得改 ⇒ 在测接缝 **背后**之物。
