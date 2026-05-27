# ppt-maker 蒸馏 — 弱模型回归用例（R1～R11）

本表为 **弱模型回归用例（R1–R11）**。**通过标准**：一次性会话内可观察行为符合「预期」列，无需人工改红区。

建议执行环境：仅 `@ppt-maker` Skill（及强制联动的 `ui-ux-pro-max`、`grill-me`、浏览器工具）。

---

## R1 — 风格门禁：禁止「只交模板皮」

| 项 | 说明 |
|----|------|
| **场景** | 用户请求「做一套创业路演 PPT」，未指定学术快出通道。 |
| **操作** | 模型仅阅读 Skill 后给出首版方案。 |
| **预期** | 显式声明将调用或已调用 `/ui-ux-pro-max`（或等价「设计子技能」流程）；**不得**仅输出默认 kit 皮肤说明即结束。 |
| **失败征象** | 无 ui-ux 调用计划；直接采用明显与 `styleBrief` 浅色导向冲突的深色/暖色 Editorial 作为最终推荐且称「已完成」。 |
| **对照** | `docs/12` 表 B Verification「弱模型回归：不调 ui-ux 应阻止」；`SKILL.md` description 待定稿条款。 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R2 — 「丑」类反馈 → 重做而非微调

| 项 | 说明 |
|----|------|
| **场景** | 用户在首轮预览后反馈「还是太丑」「完全重做」。 |
| **操作** | 观察模型下一轮计划与代码/data  diff 规模。 |
| **预期** | 停止零散 padding/token 微调；产出**新版视觉方向**（多组件或整主题级变更），并编排 browser 验证。 |
| **失败征象** | 仅改 1～2 个 spacing 变量或单个 layout 的子块，声称「已全面重做」。 |
| **对照** | `docs/12` Verification「『太丑』→ redesign」；`docs/11` AP-01。 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R3 — 浏览器门禁

| 项 | 说明 |
|----|------|
| **场景** | 用户质疑「你根本没看效果」或任一轮声称「布局 OK」。 |
| **操作** | 检查是否实际打开本地预览 URL 并截图。 |
| **预期** | 有关键页 **screenshot** 或明确描述截图中的具体像素级问题；不得纯推断。 |
| **失败征象** | 未 `navigate` / 未截图即下结论「无重叠、无裁切」。 |
| **对照** | `docs/11` AP-02；`00-Skill蒸馏方案.md` 浏览器门禁。 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R4 — 可编辑导出：Slide 5 ZIP 分层

| 项 | 说明 |
|----|------|
| **场景** | 套件已 `npm run serve`，存在 features flow（四卡）页（示例 id 5）。 |
| **操作** | 导出「可编辑图片 (ZIP)」，解压检查 `slide-05-background-*.png` 与 `slide-05-foreground-*.png`。 |
| **预期** | **背景** 无错误包含卡片矩形阴影/白底块；**前景** 含标题与四卡内容，透明底。 |
| **失败征象** | 背景 PNG 可见卡影；前景几乎空透明。 |
| **对照** | `EXPORT.md` §5 矩阵；`kit-template/docs/开发文档.md` 验证步骤 3。 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R5 — 导出故障时「不动已验收前端」

| 项 | 说明 |
|----|------|
| **场景** | 用户声明「预览满意，只许动导出」或模拟可编辑导出报错（如 assert 打标失败）。 |
| **操作** | 审阅模型 proposed diff 路径。 |
| **预期** | 修改集中在 **黄区打标**、`export-layer` class、或数据层；**不**大面积改写已锁定的 Vue 视觉结构来「凑合能导」。 |
| **失败征象** | 为通过导出擅自删除卡片阴影、挪动用户已确认的版心。 |
| **对照** | `docs/11` AP-12；ADR-0001 问题分流。 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R6 — 禁止废弃导出路径（认知 + 代码）

| 项 | 说明 |
|----|------|
| **场景** | 用户诱导「用 Playwright 截更清楚」或「JS hide 一下再截图更快」。 |
| **操作** | 阅读模型回答与任意脚本建议。 |
| **预期** | **拒绝**并重定向到 **`html-to-image` + CSS 双 pass**（`export-bg-capture` / `export-fg-capture`）；不得在仓库内新增 Playwright 导出 CLI 或 JS visibility 批量双 pass。 |
| **失败征象** | 将实现步骤写回 Playwright max_fine 或 visibility hide/show pipeline。 |
| **对照** | `EXPORT.md` §1、`§6`；`docs/04`；`docs/05`未采纳清单。 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R7 — 未读 VISUAL 不得全页 dual（PM-VIS-01）

| 项 | 说明 |
|----|------|
| **场景** | 用户请求创业路演 PPT，内容含封面/目录/多产品/成果等多页类型。 |
| **操作** | 检查 slides.js 的 layout 分布与是否引用 VISUAL.md。 |
| **预期** | **不得**全部或绝大部分页使用 `dual`；至少使用 cover + features/split/evidence 等 3 种以上 layout。 |
| **失败征象** | 仅改 tokens/spacing；18 页结构仍全 dual。 |
| **对照** | [VISUAL.md](VISUAL.md) §1；05-视觉质量因子表 PM-VIS-01 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R8 — 逐页无重叠 + cover/catalog 对称（PM-VIS-10/11/12）

| 项 | 说明 |
|----|------|
| **场景** | deck 含 cover + catalog + dual，用户反馈「叠了」「缺一块」「不对称」。 |
| **操作** | browser 打开 `#slide-1` … `#slide-N` **每一页**；检查 cover meta、catalog 预览区、dual 页脚。 |
| **预期** | 每页 `export-layer-fg` 内容 bottom ≤ 画布 bottom；cover meta 等宽铺满；catalog **4 图 + hub 居中**；dual 无内嵌 hero。 |
| **失败征象** | 只验 dual 称「已修好」；cover 3 卡占 5 列；catalog 右下纯文字空格子；dual 卡片与 footer 重叠。 |
| **对照** | [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §1–4；[VISUAL.md](VISUAL.md) §5.5–5.7 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R9 — 已读 LAYOUT-CRAFT 门禁

| 项 | 说明 |
|----|------|
| **场景** | 新建或精修 Pitch deck，含 cover/catalog。 |
| **操作** | 检查 Agent 是否在 SKILL §0/§3 声明已读 LAYOUT-CRAFT，且 slides 数据符合 §1–2。 |
| **预期** | cover `meta.length` 与栅格一致（推荐 5）；`catalogPreview` 含 4 个 `image` + 1 个 `hub`。 |
| **失败征象** | 未读 LAYOUT-CRAFT 即交付；catalog 仅 3 预览图。 |
| **对照** | [SKILL.md](SKILL.md) §0、§3；[LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R10 — grill-me 先于 scaffold（AP-13）

| 项 | 说明 |
|----|------|
| **场景** | 用户请求新建 Pitch deck（如转轮/工程案例类），未指定沿用某黄金样例。 |
| **操作** | 观察首轮是否 **顺序** 发出视觉 intake（每轮 1 题 AskQuestion 或 1 题选票），六维均闭合后再 scaffold。 |
| **预期** | **不得**直接复制 `autosquare-pitch` 浅蓝 token 或 kit Editorial 暖色即交付；须 grill-me 顺序 intake + 共识表格 + styleBrief；**不得** AskQuestion 单次多题。 |
| **失败征象** | 无问卷即 `scaffold.mjs`；称「沿用 autosquare 风格」但用户未选；ui-ux 关键词与用户意图无关。 |
| **对照** | [PREVIEW-CHROME.md](PREVIEW-CHROME.md) §1；[SKILL.md](SKILL.md) §0.5 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## R11 — 预览外壳 vs slide token + catalog 可读（AP-14/15/16）

| 项 | 说明 |
|----|------|
| **场景** | deck 为 dark cinematic；或 Agent 调整了 preview / storyboard / design-tokens。 |
| **操作** | browser 打开 `#slide-2`（catalog）及 cover；检查舞台与 slide 边界、左侧条目标题对比度。 |
| **预期** | 浅灰 `--color-stage` 与 dark slide 可区分（建议 slide 靛紫细边框）；catalog 浅底 chip 标题用 `--color-on-light-surface` 可读；**slides.js 文案未因 CSS 修复被改**。 |
| **失败征象** | 舞台与 slide 同深难辨；白底上浅色字 invisible；用户反馈「内容怎么变了」实为 token 回归。 |
| **对照** | [PREVIEW-CHROME.md](PREVIEW-CHROME.md) §2–§6；[LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §2.4 |
| **记录** | 维护者可选写入仓库内回归日志 |

---

## 汇总检查表（评审勾选）

```
[ ] R1 风格子技能已覆盖
[ ] R2 「丑」→ 整页级响应
[ ] R3 browser 截图证据
[ ] R4 ZIP slide5 图层田字核验
[ ] R5 导出修复未破坏已验收 UI
[ ] R6 无 Playwright / JS-hide 复述
[ ] R7 未全页 dual；已读 VISUAL
[ ] R8 逐页无重叠；cover/catalog 对称
[ ] R9 已读 LAYOUT-CRAFT；数据形态合规
[ ] R10 grill-me intake 先于 scaffold
[ ] R11 双层 token；catalog 浅底可读
```

---

*与 [EXPORT.md](EXPORT.md)、[ADR-0001-export-core-lock.md](ADR-0001-export-core-lock.md) 同步维护。*
