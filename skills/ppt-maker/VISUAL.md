# ppt-maker 视觉质量手册

弱模型交付 Pitch 类 PPT 时，**好看**来自可执行决策链，而非「审美灵感」。本文件蒸馏自 AutoSquare 会话 **L1–570 丑→好看** 转折。

**前置**：须已完成 [SKILL.md](SKILL.md) §0.5 grill-me intake，并完成 ui-ux-pro-max + map-design-system。dark slide 须读 [PREVIEW-CHROME.md](PREVIEW-CHROME.md)。

---

## 1. Layout 分型（PM-VIS-01）

**禁止**将 18 页（或全部页）塞进 `DualCaseLayout`。dual 仅用于双栏案例对比。

| 页型 | layout | 何时用 |
|------|--------|--------|
| 封面 | `cover` | 主副标题 + Logo |
| 目录 | `catalog` | 章节索引 |
| 多卡/流程 | `features` | flowBar、duoPanel、四卡 |
| 图文/截图 | `split` | 产品图；`imageFrame: 'browser'` 为官网整页 |
| 证书/成果 | `evidence` | stack 叠露边 + stats/table |
| 金句/封底 | `statement` | agentFlow、brandLogos |
| 双栏案例 | `dual` | 明确 A/B 对比时 |

用户说「丑 / 两栏不必遵守」→ **停止微调**，按上表重做多 layout，而非只调 spacing。

---

## 2. 质感与 token（PM-VIS-02、03）

1. 写入 **styleBrief**（浅色、创业科技、对标 SaaS 文档站气质）。  
2. 调用 **ui-ux-pro-max** 生成 `design-system/*/MASTER.md`。  
3. 运行 **map-design-system.mjs** → `design-tokens.css`。

**浅色系验收**：背景约 `#F8FAFC`；**禁止**保留 kit 默认 Editorial 暖色 `#C2410C`。

**层次**（非死白底）：

- 页面级：浅底 + 柔和环境光（mesh / 浅蓝光晕 sibling，标 `export-layer-bg`）  
- 内容块：`glass-card` 轻阴影与圆角  
- 强调：蓝紫渐变用于 kicker、分割线、小标签  

只换 token、不改 layout 密度 → **不足以**从「丑」变「好看」。

### 2.5 明暗双轨（PM-PREV-01～03）

用户经 grill-me 选定 **dark cinematic** 时，常见组合为 **浅灰预览舞台 + slide 内深底**（非整页全黑）。

| 层 | 变量锚点 | 要点 |
|----|----------|------|
| 预览外壳 | `:root`、`--color-stage` | 约 `#E2E8F0` 舞台；顶栏白底 |
| slide 画布 | `.slide-frame__canvas` | 深底 `#050506`；accent 与用户定稿一致 |
| slide 内浅底 chip | `--color-on-light-surface` | catalog 条目、cover meta **禁止**用 slide 浅色 `--color-primary` |

改 preview token 后须 browser 验 **catalog**（`#slide-2`）与 cover meta，避免「字看不见像内容被改」。详见 [PREVIEW-CHROME.md](PREVIEW-CHROME.md)。

---

## 3. 信息密度（PM-VIS-05、08）

用户否「留白过重 / 缺高级感」时：

- 增加 **卡片层次**（features flow、duo、hub）与 **叙事区块**  
- 减少单侧大块空 canvas  
- 大改前用 **CreatePlan + grill-me** 列清单，一次到位  

**禁止**仅改 `padding` 或单个 `--slide-gap` 声称「已全面重做」。

---

## 4. Browser 实看门禁（PM-VIS-04）

声称「布局 OK / 已交付」前：

1. `npm run serve`  
2. **browser** 打开预览 URL  
3. **逐页** screenshot / CDP（`#slide-1` … `#slide-N`，不可只查 dual）  
4. 按截图修：重叠、裁切、NaN 导航、懒加载未加载、**cover 底栏偏左、catalog 右下角空位**、**catalog 浅底条目不可读（token 回归）**、**dark slide 与舞台融在一起**  

无截图 → 不得下结论。

---

## 5. 逐页 craft（PM-VIS-06、09）

### 5.1 官网 / 产品截图（split + browser）

- `layout: 'split'`，`imageFrame: 'browser'`  
- 容器 **16:9**；截图 `cover` 填满 chrome 内框  
- **禁止** browser 模式叠加 HUD 十字准星 + 白底 glass-card 打架（ch03 审查结论）

### 5.2 证据 / 资质（evidence）

- 多图 **stack 露边**，不必每张完整展开  
- 配 **stats 或 table** 体现「份数/奖项」  

### 5.3 对称 brand（statement）

- 左右 panel **镜像**宽度与内边距  
- 合作 Logo 居中或对称轴明确（用户 L543「对称！！！」）

### 5.4 Features 变体

- **flow**：四卡 + flowBar（slide5 导出回归锚点）  
- **duo**：双卡 + hub；禁用 `grid-auto-rows: 1fr` 压扁（ch04 L230）

### 5.5 封面 meta 对称（PM-VIS-10）

- 底部 meta 卡 **等宽铺满**；列数 = `meta.length`（见 [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §1）  
- **推荐 5 项**（对标 autosquare-pitch）；3 项 + `repeat(5,1fr)` 为典型丑版反例  

### 5.6 目录预览对称（PM-VIS-11）

- **4 预览图 + hub 居中 overlay**（2×2 满格）  
- **禁止** 3 图 + hub 占独立空格子 → 「缺一块」  
- 数据与 CSS 见 [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §2  

### 5.7 dual 溢出链（PM-VIS-12）

- **禁止** `DualCaseLayout` 内嵌 hero / 双层 glass-card  
- 章节标题 → `SlideFrame` 顶栏；`slide-frame__body` 传递 `min-height:0`  
- `CaseCard` media 勿写死 min-height；desc/metadata 控密度（见 [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §3）  

---

## 6. 素材感知 UI（PM-VIS-07）

| 素材 | 做法 |
|------|------|
| 宽幅 Logo | 白底或高对比容器 + `object-fit: contain` |
| 外发光 Logo | 勿塞 dark-glass 导致字 invisible；勿圆形强裁 |
| 必用 Logo 三件套 | 主标识 + 合作方 + 用户指定项（L1） |
| 懒加载图 | 导出前 **滚动** storyboard 加载全部素材 |

素材路径英文 → `public/assets/materials/`；文案中文在 `slides.js`。

---

## 7. 与 EXPORT 边界

视觉满意后导出仍须 [EXPORT.md](EXPORT.md) 三区契约。导出不对 → **先**查黄区打标，**禁止**为凑合导出破坏已验收版式。

---

## 8. 相关文档

- [REFERENCE.md](REFERENCE.md) — 决策树、AP 反模式  
- [PREVIEW-CHROME.md](PREVIEW-CHROME.md) — grill-me intake、双层 token、浅舞台  
- [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) — cover/catalog/dual 工艺与逐页验收  
- [EXAMPLES.md](EXAMPLES.md) — styleBrief 与 slides 片段  
- [VERIFICATION.md](VERIFICATION.md) — R1/R2/R7/R10/R11 回归  
