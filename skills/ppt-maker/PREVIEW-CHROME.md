# ppt-maker 预览外壳与幻灯片画布分离

弱模型在 **dark cinematic** 等深色 slide 主题下，常把「预览页 UI」与「16:9 幻灯片内容」混用同一套 CSS 变量，导致：舞台与 slide 分不清、目录白底条目文字不可读、用户误以为「内容被改了」。本文件蒸馏自 `deck-zhuanlun` 重建会话。

**何时读**：用户选定 dark slide；调整 `storyboard.css` / 顶栏 / 舞台色；修 catalog 或 cover 浅底 chip 对比度；用户说「预览和 slide 融在一起」或「目录字看不见」。

**前置**：[SKILL.md](SKILL.md) §0 须已完成 **grill-me 视觉 intake**（见 §1）。

---

## 1. 开工前：grill-me + ui-ux-pro-max（硬门禁）

| 错误 | 后果 |
|------|------|
| 未问用户，直接沿用 `autosquare-pitch` 浅蓝皮 | 风格与用户意图不符，返工整 deck |
| 只跑 ui-ux-pro-max，把检索结果当最终定稿 | map 出绿色/暖色等与用户选择冲突 |
| 正文列选项但不发 AskQuestion / 选票 | 用户无法点选，Agent 易跳过等待 |
| AskQuestion 一次多题 | 易报 `questions: Required` 或 UI 空题干 |

**正确顺序**（新建或整 deck 重做）：

```
grill-me 顺序 grill（6 轮 · 每轮 1 题 · AskQuestion questions.length=1）
  → 每轮用户显式选择 → 停止等待 → 下一题
  → 全部闭合后 Agent 一次表格复述共识
  → ui-ux-pro-max --persist（styleBrief 写入用户选择）
  → map-design-system.mjs
  → 若 slide 为 dark：应用本文件 §2 双层 token + §3 舞台
  → scaffold / 写 slides.js
  → validate + 逐页 browser
```

**顺序 grill 维度**（每题附推荐项；详见 [EXAMPLES.md](EXAMPLES.md) §12）：

| 维度 | 示例选项 |
|------|----------|
| slide 明暗 | light SaaS / dark cinematic / 混合（浅外壳+深 slide） |
| 主强调色 | 靛紫 `#4F46E5` / 蓝青 / 用户指定 |
| 字体气质 | Clash+Satoshi / 几何无衬线 / 用户指定 |
| 预览舞台 | 浅灰 `#E2E8F0` + slide 细边框 / 深灰舞台 / 与 slide 同色 |
| 信息密度 | 中高 / 留白型 |

**禁止**：把黄金样例 `autosquare-pitch`、kit 默认 Editorial `#C2410C`、或 Agent 偏好当作用户选择。

**联用**：`grill-me` skill（Cursor：`AskQuestion` **每轮 1 题**；失败见 `grill-me/PLATFORMS.md` §故障排除；无工具时 Markdown 选票 **1 题/轮**）。

---

## 2. 双层 token 架构（PM-PREV-01）

预览页有两层视觉上下文，**必须分离变量**：

| 层 | DOM 锚点 | 职责 |
|----|----------|------|
| **预览外壳** | `:root`、`.storyboard-main`、顶栏、侧栏 | 浅底 UI、滚动区、导出按钮 |
| **幻灯片画布** | `.slide-frame__canvas` | 16:9 内容；导出 capture 只截此区域 |

**反模式**：只改 `:root` 做 dark 主题 → 顶栏、舞台、slide 全黑，slide 与背景无法区分。

**推荐实现**（`src/styles/design-tokens.css`）：

```css
/* 预览外壳 — 浅色系 */
:root {
  color-scheme: light;
  --color-canvas: #F1F5F9;
  --color-stage: #E2E8F0;
  --color-stage-border: #CBD5E1;
  --color-foreground: #0F172A;
  /* …顶栏、侧栏用此处变量… */
}

/* 16:9 画布内 — dark cinematic（与用户 grill-me 定稿一致） */
.slide-frame__canvas {
  color-scheme: dark;
  --color-background: #050506;
  --color-surface: #0a0a0c;
  --color-foreground: #EDEDEF;
  --color-primary: #EDEDEF;        /* slide 内主文字（浅） */
  --color-on-light-surface: #0F172A; /* slide 内白底 chip 标题（深） */
  --color-on-light-muted: #475569;
  /* … */
}
```

**黄区可改文件**（预览 chrome 相关）：

| 文件 | 改动 |
|------|------|
| `design-tokens.css` | `:root` vs `.slide-frame__canvas` 双层 |
| `storyboard.css` | `.storyboard-main { background: var(--color-stage) }` |
| `SlideFrame.vue` | 舞台边框 `border: 1px solid var(--color-accent)`；浅底投影 |
| `nav.css` | 顶栏白底 / 浅灰，与 dark slide 对比 |

**红区**：`export-capture.css` 导出时去掉边框/阴影/舞台 — **勿**为导出改 slide 内 token。

完整片段见 [EXAMPLES.md](EXAMPLES.md) §13。

---

## 3. 深色 slide + 浅色舞台（PM-PREV-02）

用户常选 **slide 内 dark cinematic**，但要求 **预览外壳可读、slide 边界清晰**。

| 元素 | 推荐 token |
|------|------------|
| 页面背景 `--color-canvas` | `#F1F5F9` |
| 滚动舞台 `--color-stage` | `#E2E8F0` |
| slide 外框 | 1px 靛紫（`--color-accent`）+ 轻阴影 |
| slide 内背景 | `#050506`（仅在 `.slide-frame__canvas`） |

**反模式**：舞台也用 `#050506` → 用户反馈「深色 slide 和页面背景分不清」。

---

## 4. slide 内浅底组件的文字色（PM-PREV-03）

**典型踩坑**：`CatalogLayout` 条目为白底 chip，却用 slide 的 `--color-primary`（浅色 `#EDEDEF`）→ 白底上近 invisible；用户以为 **slides.js 内容被改**。

**规则**：

| 表面 | 标题/正文变量 |
|------|----------------|
| dark glass / 深底 | `--color-foreground` / `--color-primary` |
| 白底 / 浅底 chip（仍在 slide 内） | `--color-on-light-surface` / `--color-on-light-muted` |

**须 browser 实看的页型**（改 token 后必查）：

- `catalog` — 左侧条目列表（浅底 chip）
- `cover` — meta 底栏（若浅底）
- `features` / `statement` — 含 `rgba(255,255,255,…)` 浅底块

**禁止**：为修对比度而改 `slides.js` 文案；**只**改 CSS 或 layout 内 `color` 引用。

---

## 5. map-design-system 之后

`map-design-system.mjs` 写入 `:root` 级 token，**不会**自动产生 `.slide-frame__canvas` 覆盖块。

| 用户定稿 | map 后 Agent 须做 |
|----------|---------------------|
| 浅色 slide | 通常可直接用 map 结果；验收浅底非 `#C2410C` |
| dark slide + 浅外壳 | map 后 **追加** §2 的 canvas 块 + `--color-on-light-*`；必要时微调 `:root` 舞台色 |
| map 主色与用户选择冲突 | 以 **grill-me 共识** 为准覆盖 accent；可记 `tokenMapDebt` |

---

## 6. 验收清单（browser）

改 preview / token 后，**逐页**实看（不可只验 dual）：

```
[ ] 浅灰舞台与 dark slide 边界清晰（靛紫细边框可见）
[ ] 顶栏、侧栏为浅色，与 slide 对比足够
[ ] catalog 左侧条目标题在浅底 chip 上可读（非「内容丢了」）
[ ] cover meta 底栏对比度正常
[ ] 导出预览：export-capture 仍只含 slide 画布（无舞台灰边）
[ ] slides.js 未因视觉修复而改动用户文案
```

对照 [VERIFICATION.md](VERIFICATION.md) R10、R11。

---

## 7. 反模式速查

| ID | 现象 | 正确做法 |
|----|------|----------|
| AP-13 | 未 grill-me 即 scaffold，默认 autosquare 皮 | §1 顺序；顺序 grill + 单题 AskQuestion 或选票 |
| AP-14 | 单层 token；catalog 白底字 invisible | §2–§4 双层 + `--color-on-light-surface` |
| AP-15 | 用户说「内容怎么变了」 | 先查 CSS 对比度，勿动 slides.js |
| AP-16 | dark 舞台 + dark slide | §3 浅舞台 + slide 边框 |

---

## 8. 相关文档

- [SKILL.md](SKILL.md) — 工作流 §0 / §2.5
- [VISUAL.md](VISUAL.md) — §2.5 明暗双轨
- [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) — catalog §2.4 浅底条目
- [EXAMPLES.md](EXAMPLES.md) — §12 intake、§13 token 片段
- [REFERENCE.md](REFERENCE.md) — 决策树、AP-13～16
