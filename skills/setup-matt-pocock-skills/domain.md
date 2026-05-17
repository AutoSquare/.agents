# 领域文档（Domain Docs）

工程技能探索代码库时应如何消费本仓库的领域文档。

## 动手探索前先读这些

- 根目录 **`CONTEXT.md`**；或
- 若存在根目录 **`CONTEXT-MAP.md`** —— 它指向每个语境各自的 `CONTEXT.md`。与当前议题相关的都读。
- **`docs/adr/`** —— 读即将触及区域内的 ADR。多语境仓库还要查 `src/<context>/docs/adr/` 的语境专属决策。

若上述文件不存在，**静默继续**。不必强调缺失；不必主动建议预先创建。生产方技能（**grill-with-docs** 技能）会在术语或决策真正落地时惰式创建。

## 文件结构

单语境（多数仓库）：

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多语境（根目录存在 `CONTEXT-MAP.md`）：

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← 全局决策
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← 该语境专有决策
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用术语表词汇

当你在输出中为领域概念命名（工单标题、重构提案、假设、测试名等），采用 `CONTEXT.md` 定义的术语。不要漂移去用语境表明确要求避免的同义词。

若所需概念尚未入表 —— 这是信号：要么你在发明项目不用的语言（再想想），要么确有缺口（记下待 **grill-with-docs** 技能 填补）。

## 标注与 ADR 冲突

若你的输出与既有 ADR 矛盾，要明确摊开，而非默默覆盖：

> _与 ADR-0007（事件溯源订单）相悖 —— 但值得重开议题，因为…_
