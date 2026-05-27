# ppt-maker 示例片段（通用化）

本文件提供 **可迁移** 的 styleBrief 与 `slides.js` 结构片段，供 Agent 快速对齐数据形态与版式意图。文中公司、高校、产品名为 **虚构占位**，实施时整段替换为用户真实品牌与素材路径。

---

## 1. `styleBrief` 示例（创业 SaaS 浅色）

写入 `.ppt-maker-project.json` 的 `styleBrief` 字段或等效配置：

```json
{
  "slug": "demo-pitch-2026",
  "templateVersion": "ppt-maker-kit@0.2.0",
  "styleBrief": "微服务管理类 SaaS，对标国际一线云厂商文档站与控制台气质：浅色模式，极浅灰白底（约 #F8FAFC），高饱和蓝紫渐变作为强调与分割线点缀。现代几何无衬线标题、中高信息密度正文，卡片轻阴影层次，留白受控不显空洞。"
}
```

**蒸馏要点**

- 「浅色」「浅底」「Light Mode」须显式写入，避免默认深色玻璃或暖灰 Editorial。  
- 对标陈述只描述**气质**，不绑定单一商业品牌可复制资产。

---

## 2. `slides.js` 片段 — 封面（cover）

```javascript
{
  id: 1,
  layout: 'cover',
  title: '产品代号',
  subtitle: '端到端指标体系与告警编排',
  description: '代表工程应用集 · 核心能力摘要\n某某大学 · 产学研协作',
  kicker: 'PRODUCT PITCH',
  image: 'hero-visual.png',
  imageAlt: '主视觉',
  partnerLogo: 'logo-university.png', // 可选
  meta: [
    { label: '学院', value: '某某大学某某学院' },
    { label: '应用方向', value: '铁路 · 水电 · 地质灾害' },
    { label: '技术栈', value: 'LiDAR · 遥感 · GNSS' },
    { label: '案例规模', value: '6 项代表工程' },
    { label: '核心能力', value: '结构面解译 · 稳定性量化' },
  ],
}
```

**对称要点**（[LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §1）：

- **推荐 5 项 meta**，与 autosquare-pitch 底栏等宽铺满一致。  
- `CoverLayout` 须 `grid-template-columns: repeat(meta.length, …)`，**禁止** 3 项却用 5 列栅格。  
- Logo：**白底 contain**，勿圆形强裁宽幅 Logo（AP-04）。

---

## 3. `slides.js` 片段 — 目录（catalog）

```javascript
{
  id: 2,
  layout: 'catalog',
  title: '目录',
  subtitle: 'CONTENTS',
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
    { hub: '平台枢纽 / 主题名' },
  ],
}
```

**对称要点**（[LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §2）：

- 预览区 **4 张缩略图 + hub 居中 overlay**（2×2 满格）。  
- **禁止** 仅 3 图 + `{ hub }` 占第四格无图 → 右下角「缺一块」。  
- 左侧 `items` 条数可与 4 图不同；满格对称靠 **catalogPreview 四图**。

导出时目录项若有 hover 动效，宜在模板层为「静态导出态」提供等价视觉。

---

## 4. `slides.js` 片段 — 功能页（features / flow）

```javascript
{
  id: 5,
  layout: 'features',
  headline: '四大能力闭环',
  featureStyle: 'flow',
  features: [
    { title: '采集', body: '多协议探针与边缘聚合' },
    { title: '存储', body: '分层降采样与低成本归档' },
    { title: '分析', body: '统一查询语言与仪表盘' },
    { title: '行动', body: '告警策略与自动化 Runbook' },
  ],
}
```

**可编辑导出**：该页为 **slide5 矩阵** 重点页；layout 须正确区分 `export-layer-fg` 与 `export-layer-bg`，避免卡影被背景 pass 吸收（见 `EXPORT.md`）。

---

## 5. `slides.js` 片段 — 分栏 + 浏览器框（split）

```javascript
{
  id: 6,
  layout: 'split',
  variant: 'browser',
  headline: '控制台真实界面',
  body: '左侧为运行中集群拓扑，右侧为策略模板库；截图随版本迭代替换。',
  mediaSrc: '/assets/materials/screenshot-console.png',
  mediaAlt: '产品控制台截图',
}
```

**版式要点**：截图应 **充满** browser chrome 内框，减少外圈死白（对照 AP-08）。

---

## 6. `slides.js` 片段 — 证据 / 资质（evidence）

```javascript
{
  id: 15,
  layout: 'evidence',
  headline: '资质与合作伙伴',
  stack: [
    { src: '/assets/materials/cert-01.png', caption: '等保备案' },
    { src: '/assets/materials/cert-02.png', caption: '软件著作权' },
    { src: '/assets/materials/cert-03.png', caption: '合作框架协议' },
  ],
  stats: [
    { label: '签约客户', value: '120+' },
    { label: '日均处理事件', value: '4.2 亿' },
  ],
}
```

栈区每图 **略错开露边**；底部表格或统计数字强化「多份材料」叙事（对照 AP-09）。

---

## 7. Layout 对照表（最小索引）

| slide id（示例） | layout | 说明 |
|------------------|--------|------|
| 1 | cover | 主副标题、双 Logo、装饰 sibling |
| 2 | catalog | 条目 + 可选预览缩略 |
| 4～5 | features | flowBar / flow 四卡等；**5 为导出回归锚点** |
| 6+ | split | browser 或图文分栏 |
| 15～17 | evidence | stack + 表或 stats |

完整 18 页级对照见 `kit-template/examples/` 与 [REFERENCE.md](REFERENCE.md) layout 变体索引；新建项目可少于或多于 18 页，但 **每种 layout 至少保留一页** 作导出抽检。

| slide（示例） | layout | 变体 | 蒸馏备注 |
|---------------|--------|------|----------|
| 1 | cover | — | Logo 白底 contain |
| 2 | catalog | 4 preview + hub | **禁止 3+1 空格子** |
| 5 | features | flow 四卡 | **slide5 导出锚点** |
| 6 | split | browser 16:9 | PM-VIS-09 |
| 12 | features | duo | grid-auto-rows auto |
| 13 | features | hub 四卡 | — |
| 14–16 | evidence | stack+table | PM-VIS-06 |
| 18 | statement | brand 对称 | PM-VIS-06 |

---

## 8. Logo 「三件套」约定（占位表述）

泛指路演场景下常见组合（按用户实际素材增减）：

1. **主品牌标识**（深色或单色矢量，浅色底上可读）。  
2. **合作方标识**（高校、实验室、母集团）。  
3. **占位或背书**（如开源基金会、行业标准联盟）— 可无，但不得在封面无理由缺失用户明确要求出现的标识。

数据中对应字段名以 **当前 kit 的 `layouts` 与 slides schema** 为准（见 [`kit-template/docs/slides-schema.md`](kit-template/docs/slides-schema.md)）。

---

## 9. 自定义 Layout 的最小模板提示

新建 `FooLayout.vue` 时：

- 外层内容根节点加 **`export-layer-fg`**。  
- mesh、渐变光晕、`::before` 伪元素-heavy 的装饰：**拆成 canvas 内独立 sibling**，标 **`export-layer-bg`**，勿与正文共用一个将被整段 `display: none` 的父级。  
- 在 SlideFrame / 画布内保持 **16:9** 作画比例；媒体 `object-fit` 与字幕安全区遵从项目 tokens。

---

## 10. 与 EXPORT / VERIFICATION 的联动

- 任意新增 layout 合并前：跑通 `assertExportLayerCoverage`（见 `EXPORT.md`）。  
- 弱模型自检：在完成 **逐页** browser 截图后，对 **slide 5** 执行 ZIP 图层目检（见 [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §4）。

---

## 11. dual 页黄区补丁（溢出时）

若 dual 页卡片顶进页脚，按 [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §3 检查：

1. 删除 `DualCaseLayout` 内嵌 hero  
2. `SlideFrame` 增加 `slide-frame__body`（`flex:1; min-height:0; overflow:hidden`）  
3. `CaseCard` media 去掉固定 `min-height`，desc 可 `line-clamp:2`  

**禁止**为修溢出而改红区 export 引擎。

---

## 12. grill-me 顺序 intake（Pitch 新建 · 每轮 1 题）

Agent 在 scaffold **之前**按序发问；Cursor **`AskQuestion` 每次 `questions` 仅 1 项**。每题附推荐；收答 **停止** 后再发下一题。

| 轮次 | id | 问题 | 选项示例 | 推荐 |
|------|-----|------|----------|------|
| 1/6 | slide_mode | slide 明暗 | light_saas / dark_full / hybrid | hybrid |
| 2/6 | accent | 主强调色 | indigo / cyan / earth / custom | indigo |
| 3/6 | type | 字体 | clash_satoshi / geo_sans / serif_academic | clash_satoshi |
| 4/6 | stage | 预览舞台 | light_border / dark_stage / same_as_slide | light_border |
| 5/6 | density | 信息密度 | medium_high / airy | medium_high |
| 6/6 | scope | 内容范围 | full_pdf / pitch_core / user_spec | 按素材 |

**第 1 轮 AskQuestion 示例**（title 须带 `第 1/6 轮`）：

```json
{
  "title": "Pitch 视觉 · 第 1/6 轮",
  "questions": [
    {
      "id": "slide_mode",
      "prompt": "Slide 明暗（推荐：hybrid）",
      "options": [
        { "id": "hybrid", "label": "浅预览 + dark slide" },
        { "id": "light_saas", "label": "全浅色 SaaS" },
        { "id": "dark_full", "label": "全深色 cinematic" }
      ],
      "allow_multiple": false
    }
  ]
}
```

六轮全部闭合后 **一次** 复述共识表格，写入 `styleBrief`，再 scaffold。用户若说「一次问完」→ Markdown 选票 2–4 题（见 grill-me EXAMPLES §B），**勿** AskQuestion 多题。详见 [PREVIEW-CHROME.md](PREVIEW-CHROME.md) §1。

---

## 13. 双层 `design-tokens.css` 片段（dark slide + 浅外壳）

map 完成后，在 **黄区** `src/styles/design-tokens.css` 追加或调整（勿改 kit-template）：

```css
/* 预览外壳 */
:root {
  color-scheme: light;
  --color-canvas: #F1F5F9;
  --color-stage: #E2E8F0;
  --color-stage-border: #CBD5E1;
  --color-accent: #4F46E5;
  --color-foreground: #0F172A;
}

/* 16:9 画布内 — 与 grill-me 定稿一致 */
.slide-frame__canvas {
  color-scheme: dark;
  --color-background: #050506;
  --color-foreground: #EDEDEF;
  --color-primary: #EDEDEF;
  --color-on-light-surface: #0F172A;
  --color-on-light-muted: #475569;
  --color-accent: #4F46E5;
}
```

`CatalogLayout` 浅底 `.item-title` 等须引用 `--color-on-light-surface`，勿用 slide 浅色 `--color-primary`。

配套黄区：`storyboard.css`（`background: var(--color-stage)`）、`SlideFrame.vue`（accent 细边框）。导出仍由 `export-capture.css` 去掉舞台装饰。

---

*EXAMPLES.md 仅存通用片段；生产环境路径、文件名宜保持英文.*
