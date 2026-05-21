# 幻灯片策略

15 种经过验证的演示文稿结构，含情绪弧线。

## 策略选择

| 策略 | 页数 | 目标 | 受众 |
|------|------|------|------|
| YC Seed Deck | 10–12 | 种子轮融资 | VC |
| Guy Kawasaki | 10 | 20 分钟路演 | 投资人 |
| Series A | 12–15 | A 轮融资 | 成长期 VC |
| Product Demo | 5–8 | 展示价值 | 潜在客户 |
| Sales Pitch | 7–10 | 促成成交 | 合格线索 |
| Nancy Duarte Sparkline | 可变 | 转变认知 | 通用 |
| Problem-Solution-Benefit | 3–5 | 快速说服 | 时间紧迫受众 |
| QBR | 10–15 | 向利益相关方汇报 | 管理层 |
| Team All-Hands | 8–12 | 团队对齐 | 员工 |
| Conference Talk | 15–25 | 思想领导力 | 参会者 |
| Workshop | 20–40 | 技能传授 | 学员 |
| Case Study | 8–12 | 证明价值 | 潜在客户 |
| Competitive Analysis | 6–10 | 战略决策 | 内部团队 |
| Board Meeting | 15–20 | 向董事会汇报 | 董事 |
| Webinar | 20–30 | 获取线索 | 报名用户 |

## 常见结构

### YC Seed Deck（10 页）
1. 标题 / 钩子
2. 问题
3. 解决方案
4. 增长数据
5. 市场
6. 产品
7. 商业模式
8. 团队
9. 财务
10. 融资诉求

**情绪弧线：** curiosity→frustration→hope→confidence→trust→urgency

### Sales Pitch（9 页）
1. 个性化钩子
2. 对方痛点
3. 不作为成本
4. 你的解决方案
5. 证明 / 案例
6. 差异化
7. 定价 / ROI
8. 异议处理
9. CTA + 后续步骤

**情绪弧线：** connection→frustration→fear→hope→trust→confidence→urgency

### Product Demo（6 页）
1. 钩子 / 问题
2. 解决方案概览
3. 现场演示 / 截图
4. 核心功能
5. 利益 / 定价
6. CTA

**情绪弧线：** curiosity→frustration→hope→confidence→urgency

## Duarte Sparkline 模式

在「What Is」（当前痛点）与「What Could Be」（更好未来）之间交替：

```
What Is → What Could Be → What Is → What Could Be → New Bliss
(痛点)     (希望)         (痛点)     (希望)         (收束)
```

在 1/3 与 2/3 位置打破模式，可形成参与峰值。

## 检索命令

```bash
# 按目标查找策略
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "investor pitch" -d strategy

# 获取情绪弧线
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "series a funding" -d strategy --json
```

## 按情境匹配策略

| 情境 | 推荐策略 |
|------|----------|
| 融资 | YC Seed、Series A、Guy Kawasaki |
| 销售产品 | Sales Pitch、Product Demo |
| 内部汇报 | QBR、All-Hands、Board Meeting |
| 公开演讲 | Conference Talk、Workshop |
| 证明价值 | Case Study、Competitive Analysis |
| 获取线索 | Webinar |
