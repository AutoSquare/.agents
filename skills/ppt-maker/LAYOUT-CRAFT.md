# ppt-maker 版式工艺手册

弱模型在 **tokens 已 map、layout 已选型** 之后，仍常因 **对称、溢出、数据与网格不匹配** 交付「能跑但难看」的 deck。本文件蒸馏自 `deck-zhuanlun` 修版与 `autosquare-pitch` 黄金样例，补 [VISUAL.md](VISUAL.md) 未展开的 **逐 layout 工艺**。

**何时读**：编写/精修 `cover`、`catalog`、`dual` 页；用户说「缺一块」「不对称」「叠了」；browser 实看前自检。

---

## 0. 模块地图（zoom-out）

```
用户 PDF / 图片素材
       ↓
grill-me 视觉 intake → styleBrief（用户显式选择）
       ↓
ui-ux-pro-max → MASTER.md
       ↓
map-design-system.mjs → design-tokens.css（+ dark 时 .slide-frame__canvas 覆盖）
       ↓
scaffold.mjs → ppt-projects/{slug}/          ← 黄区（Agent 可改）
       ↓
slides.js（layout + 字段） + project.js
       ↓
SlideFrame（16:9 画布 · header/body/footer）
       ├── CoverLayout / CatalogLayout / …
       └── export-layer-fg | export-layer-bg
       ↓
SlideStoryboard（预览 scroll · 非页内重叠）
       ↓
validate-project.mjs
       ↓
导出引擎（红区 · 见 EXPORT.md）

黄金样例：`kit-template/examples/zhuanlun/`（数据形态）；完整视觉参考见维护者仓库 `autosquare-pitch` 归档（若有）
反模式：REFERENCE AP-01～12 · PM-VIS-01～09
```

| 术语 | 含义 |
|------|------|
| **黄区** | `ppt-projects/{slug}/` 内 Vue、slides、tokens |
| **红区** | `export-core`、capture 管线；Agent 禁止改 |
| **hub** | 目录预览区居中叠层徽章（如「AutoSquare Agent」） |
| **flex 链** | 画布内 `flex:1; min-height:0; overflow:hidden` 父子传递 |

---

## 1. 封面（cover）

### 1.1 对称规则（AP-07）

- 底部 **meta 卡** 须 **等宽铺满** 画布底栏：`grid-template-columns: repeat(meta.length, minmax(0, 1fr))`。
- **禁止** 写死 `repeat(5, 1fr)` 却只填 3 项 → 左侧三卡、右侧大空。
- **推荐** 与 AutoSquare 一致：**5 项 meta**（学院 / 方向 / 技术栈 / 规模 / 能力等），叙事完整且对称。

### 1.2 数据示例

```javascript
meta: [
  { label: '学院', value: '某某大学某某学院' },
  { label: '应用方向', value: '铁路 · 水电 · 地质灾害' },
  { label: '技术栈', value: 'LiDAR · 遥感 · GNSS' },
  { label: '案例规模', value: '6 项代表工程' },
  { label: '核心能力', value: '结构面解译 · 稳定性量化' },
],
```

### 1.3 黄区实现要点

- `CoverLayout`：`cover-meta` 用 `:style="metaGridStyle"` 绑定列数。
- 主视觉 `AssetImage` + `hero-logo`；宽幅 Logo **白底 contain**，勿圆形强裁（AP-04）。

---

## 2. 目录（catalog）

### 2.1 对称规则

- 右侧预览采用 **2×2 四格缩略图 + hub 居中 overlay**（AutoSquare 标准），**禁止** 3 图 + 1 纯文字格 → 右下角「缺一块」。
- `catalogPreview` 数据：**4 个 `{ label, image }` + 1 个 `{ hub: '…' }`**。
- 左侧 `items` 条数可与预览图数量不同（如 3 章 + 4 预览），但 **预览区必须满格对称**。

### 2.2 数据示例

```javascript
items: [
  { number: '01', title: '章节 A · 章节 B' },
  { number: '02', title: '章节 C · 章节 D' },
  { number: '03', title: '章节 E · 章节 F' },
],
catalogPreview: [
  { label: '案例 A', image: 'case-a.png' },
  { label: '案例 B', image: 'case-b.png' },
  { label: '案例 C', image: 'case-c.png' },
  { label: '案例 D', image: 'case-d.png' },
  { hub: '平台 / 主题枢纽名' },
],
```

### 2.3 布局/CSS 要点

- `catalog-preview-grid--quad`：`grid-template-rows: 1fr 1fr`；hub `position:absolute; left:50%; top:50%; transform:translate(-50%,-50%)`。
- 整页 `min-height:0; overflow:hidden`；预览图 `max-height` 约束，防裁切底边（AP-06）。

### 2.4 浅底条目文字（dark slide）

左侧 `items` 常为 **白底 chip**。slide 画布为 dark 时，`--color-primary` 多为浅色，**不可**用于 chip 标题 — 须用 `.slide-frame__canvas` 内 `--color-on-light-surface`（见 [PREVIEW-CHROME.md](PREVIEW-CHROME.md) §4）。browser 必验 `#slide-2`。

---

## 3. 双栏案例（dual）

### 3.1 禁止项

- **禁止** 在 `DualCaseLayout` 内嵌大块 hero（章节标题 + theme）—— 抢 flex 高度，卡片顶进页脚。
- **禁止** 给 dual 卡片再套 `glass-card` 双层壳（额外 padding）。
- **禁止** `CaseCard__media` 写死 `min-height:140px` + `AssetImage` `min-height:120px` 且不截断 body。

### 3.2 正确结构（AutoSquare / kit 原版）

- 章节信息 → `SlideFrame` 顶栏（badge + 单行 title/theme）。
- `DualCaseLayout` → 仅双栏 grid + `CaseCard`。
- **flex 链**：`slide-frame__body` → layout → `case-card` → media（`flex:1; min-height:0`）+ body（`line-clamp` / 减 metadata 行）。

### 3.3 SlideFrame 黄区补丁（dual 页）

```html
<div class="slide-frame__body">
  <component :is="layoutComponent" … />
</div>
```

```css
.slide-frame__body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
```

---

## 4. 逐页 browser 验收（AP-02 / AP-06）

声称「修好了」前 **每一页** 检查，不可只抽 dual 页。

### 4.1 清单

```
[ ] 打开 #slide-1 … #slide-N 每一页
[ ] 截图或 CDP 量测：export-layer-fg 最底元素 bottom ≤ 画布 bottom
[ ] dual 页：卡片底与 footer 顶 overlap ≤ 0
[ ] catalog：4 预览格均有图；hub 居中不挡 label 可读
[ ] catalog：浅底条目标题可读（dark slide 时 --color-on-light-surface）
[ ] 预览舞台与 slide 边界清晰（改 token 后）
[ ] cover：meta 卡等宽铺满
[ ] storyboard 滚动时相邻页同时可见 ≠ 页内重叠（勿混淆）
```

### 4.2 CDP 量测片段（可选）

对每页执行：`contentBottom - canvasBottom ≤ 1`（见 VERIFICATION R8）。

---

## 5. 与 EXPORT 边界

版式工艺通过后再导出。导出层问题 → [EXPORT.md](EXPORT.md)，**禁止**为导出牺牲已验收对称与无重叠。

---

## 6. 相关文档

- [VISUAL.md](VISUAL.md) — PM-VIS 因子总览
- [PREVIEW-CHROME.md](PREVIEW-CHROME.md) — grill-me、双层 token
- [EXAMPLES.md](EXAMPLES.md) — cover/catalog 数据片段
- [VERIFICATION.md](VERIFICATION.md) — R8/R9 回归
- 黄金样例：`kit-template/examples/zhuanlun/`
