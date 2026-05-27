# ppt-maker 可编辑导出契约

本文档约束 **可编辑导出**（PowerPoint 双层整页图、可编辑图层 ZIP）相关行为 Agent 与用户可见结果。预览满意后的目标是：**导出图层语义稳定、预览不被导出过程破坏，且不向已废弃的工程路径 regress**。

**架构裁决（只读红线）**：[ADR-0001-export-core-lock.md](ADR-0001-export-core-lock.md)。任何与 ADR 冲突的临时「捷径」均应拒绝。

---

## 1. 为何不修改导出框架（五段失败史）

会话与归档将可编辑导出演进压缩为下列顺序。**当前 Skill 仅宣传终态方案**；前五步为反面教材，禁止作为「备选实现」重写：

| # | 方案概要 | 失败表现 |
|---|----------|----------|
| 1 | 整页光栅块 + pptxgenjs 绝对定位拼装 | 与浏览器预览像素难以对齐 |
| 2 | Playwright 细粒度多块截图（max_fine） | layer 计数异常 / 透明度错误 / 清晰度不稳定 |
| 3 | 浏览器 `html-to-image` 双 pass + **JS `hideLayers`/`showLayers`（visibility）** | restore 链路缺陷 → **预览空白、前景 PNG 几近全透明** |
| 4 | 对隐藏节点增设 `data-export-layer-hidden` 等 restore 修补 | 预览恢复；**背景 pass 仍将卡片阴影等内容错误烘入底板** |
| 5 | **CSS 显式分层** — `export-layer-fg` / `export-layer-bg` + `export-bg-capture` / `export-fg-capture` | **当前终态**：背景与前景语义由 class 与 CSS 双模式决定，不靠 JS 批量 hide/show |

**结论**：弱模型或非维护者 Agent **不得**为「快点出包」重写 `editableLayerPipeline`、`layerCaptureBrowser` 核心逻辑或回归到 Playwright / JS visibility 管线。应先完成黄区打标与样式排查，仍失败则上报用户或维护者（红区演进须 bump manifest，见 ADR）。

---

## 2. 绿区 / 黄区 / 红区

与 ADR-0001 一致：

| 区域 | 典型路径 / 关注点 | Agent 可操作范围 |
|------|-------------------|------------------|
| **绿区** | `slides.js`（或等价数据）、`design-tokens.css`、拷贝素材 | 内容与 token 可调 |
| **黄区** | 各 `layouts/*.vue`、`SlideFrame` 的装饰 sibling、**`export-layer-*` 打标** | 可改版式与打标以实现分层正确；须在预览与 EXPORT 矩阵下验收 |
| **红区** | `editableLayerPipeline.js`、`layerCaptureBrowser.js`、`captureSlideLayers.js`、`exportEditableImages.js`、`export-capture.css` **双 pass 规则段**、`exportPptx.js` 双层组装、`captureSlides.js` **导出耦合段** | **默认只读**；校验失败需停 handoff |

**问题分流（预览 vs 导出）**

| 现象 | 优先排查 | 禁止 |
|------|----------|------|
| 预览正常、可编辑导出缺层/卡影进背景 | 黄区 `export-layer-fg/bg` 打标；`assertExportLayerCoverage` 报错信息 | 改红区 pipeline；改已验收 layout 观感 |
| 预览正常、像素级导出比例错 | 绿区 tokens / em 缩放；`captureSlides` 预设（红区须维护者） | 为导出改 Vue 版心 |
| 预览本身有问题 | 黄区 layout / 绿区 slides.js | 先修预览再谈导出 |

先 **F5 刷新** 再导出；导出后预览异常亦先 F5（ch07 restore 经验）。

---

## 3. 「仅 CSS 双 pass」语义

引擎统一为 **`html-to-image`**，与像素级导出共享离屏链路，**不使用 Playwright**，**不在背景 pass 用 JS 批量 hide/show**。

1. **`body.export-bg-capture`**：对 `.export-layer-fg` 使用 `display: none`，截取**整页背景** PNG。  
2. **`body.export-fg-capture`**：对 `.export-layer-bg` 使用 `display: none`，`backgroundColor: transparent`，截取**透明前景** PNG。

PPT/ZIP：**每页两张全幅图** — background 在下、foreground 在上。装饰性 mesh、光晕等须为 **`export-layer-bg` 的 sibling 结构**，避免与正文共节点导致一整块被错误的 pass 省略。

详见套件 [`kit-template/docs/开发文档.md`](kit-template/docs/开发文档.md) 中「可编辑导出」一节。

---

## 4. `assertExportLayerCoverage`

- **位置**：浏览器侧 `layerCaptureBrowser.js`。  
- **行为**：在每页导出前遍历 `.slide-frame__canvas` 内需导出的可视内容节点；若存在**未落入** `export-layer-fg` 且非背景装饰免检集合的节点，**抛错并阻塞导出**。  
- **意图**：防止「静默漏层」—— 导出表面上成功但 PPTX 图层缺失。  

Agent 交付新 layout 时必须预见到该断言；不得以注释或跳过调用来绕过。

---

## 5. Slide5 与高变体页的验收矩阵

下列矩阵摘自开发文档的可编辑导出验收表，用作 **ZIP / PPTX** 分层抽检的权威清单。**第 5 页（features + flow / 四卡）**为背景误混入卡影的高发用例：

| Layout 变体 | 代表 slide | 背景 PNG 期望 | 前景 PNG 期望 |
|-------------|-----------|---------------|---------------|
| cover | 1 | 含 mesh / 光晕等装饰；**不含** Logo/主标题块状前景 | Logo、标题等内容完整透明底 |
| catalog | 2 | 无目录条目与预览卡片 | 目录与预览卡片完整 |
| features + flowBar | 4 | 无卡片与 flowBar | 含 flowBar |
| features flow（四卡） | **5** | **不含卡片白板/阴影错误** | **四卡 + 标题**完整 |
| split browser | 6 | 不含截图内核与可读文字（按设计可到背景侧） | browser 边框与截图内容 |
| split 常规 | 7～11 | 无 media / 无主文案 | media 与文案 |
| statement agent | 12 | 无 orbit / 无主文案 | agent 图示 |
| features duo | 13～14 | 无 duo 卡 / hub | duo 卡片与 hub |
| evidence | 15～17 | 无 stack / 表 | stack 与表 |
| statement brand | 18 | 无 brand 面板 | logo 面板 |

**可操作验收步骤**（与开发文档对齐）：

0. 若上次导出后预览异常，先 **F5**。  
1. `npm run serve`，滚动加载全部幻灯片。  
2. 选较低分辨率档位（如 1080p）导出可编辑 PPTX → 预览仍正常、无双重阴影。  
3. 导出可编辑 ZIP → **重点打开 slide 5** 的 background / foreground。  
4. 按上表抽查 cover / catalog / split browser / evidence 等。  
5. 像素级 PPT 与单层 PNG ZIP 仍通过（非可编辑回归）。

---

## 6. 禁止路径（明确否定）

- **Playwright** 或任何 headless 浏览器截图替代 `html-to-image` 主路径。  
- **JS 层**对前景批量 `visibility: hidden` / `display` 切换实现双 pass（终态已废弃）。  
- **未经验证**修改红区文件以「先出包再说」。  
- 用 **整体给 canvas 标 `export-layer-bg`** 等误标导致前景整树被背景 pass 隐藏。

---

## 7. 与 Skill 其他文件的衔接

- **SKILL.md**：声明须阅读本文后再承诺导出相关交付。  
- **REFERENCE.md**：条件分支中「导出不对」→ 查 export 链路与打标，见本文 §2～§5。  
- **VERIFICATION.md**：弱模型回归用例 R3～R6 与本矩阵、红区只读策略对齐。

---

*文档用于 ppt-maker Skill 蒸馏；工程细节以 `kit-template` 与 ADR-0001 为准。*
