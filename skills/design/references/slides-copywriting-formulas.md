# 文案公式

25 条用于撰写说服性幻灯片文案的公式。

## 核心公式

### PAS（Problem-Agitate-Solution，问题–激化–解决）
**适用：** 问题页、痛点页
**结构：** 问题 → 激化 → 解决
**模板：**「[痛点]？每 [时间周期]，[后果]。[解决方案] 可解决此问题。」

### AIDA（Attention-Interest-Desire-Action，注意–兴趣–欲望–行动）
**适用：** CTA、收尾页
**结构：** 注意 → 兴趣 → 欲望 → 行动
**模板：**「[醒目陈述]。[利益细节]。[社会证明]。[CTA]。」

### FAB（Features-Advantages-Benefits，功能–优势–利益）
**适用：** 功能页、产品展示
**结构：** 功能 → 优势 → 利益
**模板：**「[功能] 让你 [优势]，从而 [利益]。」

### Cost of Inaction（不作为成本）
**适用：** 激化页、紧迫性页
**结构：** 现状 → 损失 → 时间衰减
**模板：**「若不采用 [解决方案]，你每 [时间周期] 将损失 [金额]。」

### Before-After-Bridge（前–后–桥接）
**适用：** 转型页、案例页
**结构：** 之前 → 之后 → 桥接
**模板：**「[之前的痛点]。[期望的之后状态]。[你的解决方案] 是桥梁。」

## 公式与幻灯片类型映射

| 幻灯片类型 | 主公式 | 情绪 |
|------------|--------|------|
| 标题 / 钩子 | AIDA、Hook | curiosity |
| 问题 | PAS、Agitate | frustration |
| 成本 / 风险 | Cost of Inaction | fear |
| 解决方案 | FAB、BAB | hope |
| 功能 | FAB | confidence |
| 增长数据 | Proof Stack | trust |
| 社会证明 | Testimonial | trust |
| 定价 | Value Stack | confidence |
| CTA | AIDA、Urgency | urgency |

## 标题模式

### 强词模式
- 「停止 [不良行为]」
- 「在 [时间周期] 内获得 [期望结果]」
- 「[形容词] 的 [行动] 方式」
- 「为何 [受众] 选择 [产品]」
- 「[数字] 种实现 [目标] 的方法」

### 对比模式
- 「[旧方式] 已过时，认识 [新方式]。」
- 「不要 [错误做法]，改为 [正确做法]。」
- 「从 [痛点] 到 [利益]。」

### 社会证明模式
- 「[数字]+ [用户/企业] 信赖 [产品]」
- 「与 [知名公司]、[知名公司] 同行」
- 「见于 [媒体/刊物]」

## 检索命令

```bash
# 按幻灯片类型查找公式
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "problem agitation" -d copy

# 获取与情绪匹配的公式
python "$env:USERPROFILE\.cursor\skills\design-system\scripts\search-slides.py" "urgency cta" -d copy
```

## 速查表

| 需求 | 推荐公式 |
|------|----------|
| 制造紧迫感 | Cost of Inaction、Scarcity |
| 建立信任 | Social Proof、Testimonial |
| 展示价值 | FAB、Value Stack |
| 驱动行动 | AIDA、CTA |
| 讲述故事 | BAB、Story Arc |
| 呈现数据 | Proof Stack |
