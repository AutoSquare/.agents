# 何时 Mock

仅在 **系统边界** mock：

- 外部 API（支付、邮件等）
- 数据库（有时 —— 更偏好测试库）
- 时间 / 随机性
- 文件系统（有时）

不要 mock：

- 你自己的类 / 模块
- 内部协作方
- 你掌控的一切

## 为可 Mock 设计

在系统边界设计 **易于 mock** 的接口：

**1. 使用依赖注入**

把外部依赖从外部传入，而非内部自建：

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. SDK 形态优于泛化 fetcher**

为每种外部操作建专用函数，而非单函数 + 内部分支：

```typescript
// GOOD: Each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: Mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

SDK 方式的收益：

- 每个 mock 只返回单一形状
- 测试装配无内部分支
- 更易看出覆盖了哪些端点
- 每个端点独立类型安全
