# CONTEXT.md 格式

## 结构

```md
# {语境名称}

{一两句话说明这是什么语境以及为何独立存在。}

## Language

**Order**：
{对该术语的简练描述}
_Avoid_: Purchase, transaction

**Invoice**：
交付后向客户发出的付款请求。
_Avoid_: Bill, payment request

**Customer**：
下单的个人或组织。
_Avoid_: Client, buyer, account

## Relationships

- 一个 **Order** 产生一条或多条 **Invoice**
- 一条 **Invoice** 恰好隶属于一个 **Customer**

## Example dialogue

> **Dev:** 「当 **Customer** 下 **Order** 时，我们会立刻创建 **Invoice** 吗？」
> **领域专家：** 「不会 —— **Invoice** 只在 **Fulfillment** 确认后生成。」

## Flagged ambiguities

- 「account」曾同时指 **Customer** 与 **User** —— 已厘清：二者是不同概念。
```

## 规则

- **坚持立场：** 同一概念若有多种说法，选最佳作为主词，其余列入 _Avoid_ 作为别名禁区。
- **显式标注冲突：** 若某词含糊，写入「Flagged ambiguities」并给出清晰结论。
- **定义要紧缩：** 每词最多一句话。说清楚它 **是**什么，不谈它做什么。
- **写明关系：** 术语加粗并在明显处表达基数。
- **只收录本项目语境特有的词。**通用编程概念（超时、错误类型、工具范式）哪怕大量使用也不收录。加词前先问：这是本语境独有概念，还是通用编程概念？只收录前者。
- **自然簇出现时分子标题；**若所有词同属一块领域，平铺列表亦可。
- **写示例对话：** 开发与领域专家的来回，示范术语如何在自然句式中协作并厘清邻近概念边界。

## 单语境与多语境仓库

**单语境（多数）：** 根目录一个 `CONTEXT.md`。

**多语境：** 根目录 `CONTEXT-MAP.md` 列出各语境的路径与彼此关系：

```md
# 语境地图（Context Map）

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — 接收并跟踪客户订单
- [Billing](./src/billing/CONTEXT.md) — 生成发票并处理支付
- [Fulfillment](./src/fulfillment/CONTEXT.md) — 管理仓库拣货与发货

## Relationships

- **Ordering → Fulfillment**：Ordering 发出 `OrderPlaced`；Fulfillment 消费后开始拣货
- **Fulfillment → Billing**：Fulfillment 发出 `ShipmentDispatched`；Billing 消费后生成 Invoice
- **Ordering ↔ Billing**：共享 `CustomerId`、`Money` 等类型
```

技能据此推断结构：

- 若存在 `CONTEXT-MAP.md`，先读它以定位语境
- 若仅有根级 `CONTEXT.md`，为单语境
- 若都不存在，在首个术语定稿时惰式创建根 `CONTEXT.md`

多语境下推断当前议题属于哪一个；不清晰则发问。
