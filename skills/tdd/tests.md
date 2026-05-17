# 好测试与坏测试

## 好测试

**集成风格：** 经由真实接口，而非 mock 内部零件。

```typescript
// GOOD: Tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

特征：

- 测用户 / 调用方在乎的行为
- 只用公开 API
- 内部 refactor 后仍能活
- 描述 WHAT，非 HOW
- 每条测试一则逻辑断言

## 坏测试

**绑实现细节的测试：** 与内部结构耦合。

```typescript
// BAD: Tests implementation details
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

红旗：

- mock 内部协作方
- 测试私有方法
- 断言调用次数 / 次序
- 行为未改 refactor 却让测试红灯
- 测试名描述 HOW 不是 WHAT
- 绕过接口用外部手段验证

```typescript
// BAD: Bypasses interface to verify
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: Verifies through interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```
