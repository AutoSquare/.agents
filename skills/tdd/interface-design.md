# 面向可测试性的接口设计

好接口令测试水到渠成：

1. **接受依赖，不在内部创建**

   ```typescript
   // Testable
   function processOrder(order, paymentGateway) {}

   // Hard to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **返回结果，不产生副作用**

   ```typescript
   // Testable
   function calculateDiscount(cart): Discount {}

   // Hard to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **表面积要小**
   - 方法少则所需测试也少
   - 参数少则测试装配更简单
