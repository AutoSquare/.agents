---
name: migrate-to-shoehorn
description: 将测试文件中的 `as` 类型断言迁移到 @total-typescript/shoehorn。用于用户提到 shoehorn、想用类型安全替代测试里的 `as`、或需要局部测试数据。
---

# Migrate to Shoehorn（迁移到 shoehorn）

## 为何用 shoehorn？

`shoehorn` 让你在测试里传 **partial 数据** 仍保持 TypeScript 满意，用类型安全替代粗暴 `as`。

**仅测试代码。** 生产代码禁止使用 shoehorn。

测试里滥用 `as` 的问题：

- 训练上会避免用它
- 必须手写目标类型
- 刻意错误数据要双 `as`（`as unknown as Type`）

## 安装

```bash
npm i @total-typescript/shoehorn
```

## 迁移模式

### 大对象只需少数字段

之前：

```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...20 more properties
};

it("gets user by id", () => {
  // 只关心 body.id 却要捏造整颗 Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...fake all 20 properties
  });
});
```

之后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

it("gets user by id", () => {
  getUser(
    fromPartial({
      body: { id: "123" },
    }),
  );
});
```

### `as Type` → `fromPartial()`

之前：

```ts
getUser({ body: { id: "123" } } as Request);
```

之后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```

### `as unknown as Type` → `fromAny()`

之前：

```ts
getUser({ body: { id: 123 } } as unknown as Request); // 故意类型错误
```

之后：

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## 选型

| 函数 | 用途 |
| ---- | ---- |
| `fromPartial()` | 传仍能通过类型检查的 partial |
| `fromAny()` | 传刻意错误的数据（保留补全体验） |
| `fromExact()` | 强求完整对象（可后续换 `fromPartial`） |

## 工作流

1. **澄清需求** —— 询问用户：
   - 哪些测试文件因 `as` 抓狂？
   - 是否巨型对象只有少数字段要紧？
   - 是否需要刻意坏数据测错误路径？

2. **安装并迁移：**
   - [ ] `npm i @total-typescript/shoehorn`
   - [ ] 找测试里的断言：`grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] `as Type` → `fromPartial()`
   - [ ] `as unknown as Type` → `fromAny()`
   - [ ] import `@total-typescript/shoehorn`
   - [ ] 跑类型检查确认
