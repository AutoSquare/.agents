---
name: ppt-maker
description: 将素材与结构化 slides 数据生成为 Vue 16:9 预览页，并在浏览器中导出可编辑/像素级 PPTX 与 ZIP。在用户说做 PPT、幻灯片、演示文稿、路演或 Pitch 时启用；开工前须 grill-me 顺序 intake（AskQuestion 每轮仅 1 题）再 ui-ux-pro-max + map-design-system；dark slide 须分离预览外壳与 .slide-frame__canvas token（PREVIEW-CHROME.md）；交付前逐页 browser 实看；cover/catalog/dual 遵守 LAYOUT-CRAFT.md；可编辑导出遵守 EXPORT.md。学术快出 pptx 用 academic-ppt-builder。
---

# PPT 制作（ppt-maker）

弱模型遵循本 Skill 及 [EXPORT.md](EXPORT.md) 应可达高质量 Pitch 交付（浅色系、多 layout、CSS 双 pass 可编辑导出）。

## 入口与分流

| 用户意图 | 选用 |
|----------|------|
| 做 PPT / 幻灯片 / 路演 / Pitch | **本 Skill** |
| 答辩、开题、文献综述、要快 pptx | `academic-ppt-builder` + MCP |

**禁止**修改 `kit-template/`；**仅**在 `ppt-projects/{english-slug}/` 写入。

## 文档（一层引用）

| 文件 | 用途 |
|------|------|
| [VISUAL.md](VISUAL.md) | **好看因子**：layout 分型、质感、密度、browser 门禁 |
| [PREVIEW-CHROME.md](PREVIEW-CHROME.md) | **预览外壳**：grill-me intake、双层 token、浅舞台+深 slide |
| [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) | **版式工艺**：cover/catalog/dual 对称、flex 链、逐页验收 |
| [REFERENCE.md](REFERENCE.md) | layout 选型、反模式决策树、脚本 |
| [EXPORT.md](EXPORT.md) | 导出三区、双 pass、红区锁定 |
| [EXAMPLES.md](EXAMPLES.md) | styleBrief、slides 片段 |
| [VERIFICATION.md](VERIFICATION.md) | 弱模型回归 R1–R11 |
| [发布说明.md](发布说明.md) | 版本、安装、发布检查清单 |

## 路径

- 运行时：`%USERPROFILE%\.cursor\skills\ppt-maker\`
- 沙箱：`ppt-maker/`（维护者编辑源）

## 工作流

### 0. 前置

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\check-node.mjs"
```

- [ ] Node ≥ 18
- [ ] 已读 [VISUAL.md](VISUAL.md)（**禁止**全页 dual）
- [ ] 已读 [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md)（cover 5 meta / catalog 4 图 + hub / dual 禁 hero）
- [ ] 已读 [PREVIEW-CHROME.md](PREVIEW-CHROME.md)（dark slide 或调整预览 UI 时）

**AP-01/02/03 门禁（蒸馏 ch02）**：用户说「丑」→ 不得微调 spacing；交付前必须 browser screenshot；禁止 Editorial 默认 `#C2410C`。

### 0.5 视觉 intake（必做 · 先于 scaffold）

**禁止**未获用户显式选择即开工；**禁止**默认沿用 `autosquare-pitch` 或 kit 暖色皮。

1. 调用 **`/grill-me`**，模式 **顺序 grill**（**每轮 1 题**，共 6 轮，见下表）。
2. 通道：Cursor **`AskQuestion` 每次仅 1 题**（`questions.length === 1`）；无工具或工具报错时用 **Markdown 选票（当前 1 题）** 并 **停止等待**（见 grill-me `PLATFORMS.md` §故障排除）。
3. **每轮**收答后再发下一题；**全部闭合后**用 **一次表格**复述共识，再写入 `styleBrief`。
4. 题目顺序与选项 → [EXAMPLES.md](EXAMPLES.md) §12、[PREVIEW-CHROME.md](PREVIEW-CHROME.md) §1。

| 轮次 | id | 主题 |
|------|-----|------|
| 1/6 | `slide_mode` | slide 明暗 |
| 2/6 | `accent` | 主强调色 |
| 3/6 | `type` | 字体 |
| 4/6 | `stage` | 预览舞台 |
| 5/6 | `density` | 信息密度 |
| 6/6 | `scope` | 内容范围（PDF 全量 / 精简路演 / 用户指定） |

- [ ] 六维均有用户显式选择（非 Agent 偏好、非黄金样例默认值）
- [ ] AskQuestion **未**单次多题；工具失败已单题重试或选票降级
- [ ] 已全部闭合后复述共识表格

**大改 / 精修前**：CreatePlan + 再次 `/grill-me`（仍顺序 grill，见 REFERENCE）。

### 1. 脚手架

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\slug.mjs" --generate
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\scaffold.mjs" --slug <slug> --workspace "<绝对路径>" --style-brief "<描述>"
```

产出含 `export-core.manifest.json`（红区 checksum）。

- [ ] slug 纯英文
- [ ] 未改 kit-template

### 2. 风格（必做）

1. 对话调用 **`/ui-ux-pro-max`**（关键词须对齐 §0.5 共识）：

```powershell
cd ppt-projects/<slug>
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "<英文关键词>" --design-system --persist -p "<slug>" -f markdown
```

2. **全自动映射 token**：

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\map-design-system.mjs" --project ppt-projects/<slug>
```

3. 更新 `.ppt-maker-project.json` 的 `designSystemQuery`。

4. **预览外壳与 slide 分离**（§0.5 若含 dark slide 或「浅外壳+深 slide」）→ [PREVIEW-CHROME.md](PREVIEW-CHROME.md) §2–§4：
   - `:root` 浅色预览变量（`--color-stage` 等）
   - `.slide-frame__canvas` 覆盖 dark slide 变量
   - `--color-on-light-surface` 供 catalog/cover 浅底 chip
   - `storyboard.css` / `SlideFrame.vue` 舞台边框

- [ ] ui-ux-pro-max 已调用
- [ ] map 脚本 exit 0
- [ ] accent 与用户 grill-me 选择一致（map 冲突以用户为准）
- [ ] dark slide 已双层 token；catalog 浅底文字可读（browser 验 `#slide-2`）

### 3. 内容与 layout

1. 素材 → `public/assets/materials/`（英文文件名）
2. 编写 `src/data/slides.js`（`layout`: cover / catalog / features / split / evidence / statement / dual）
3. 更新 `src/config/project.js`

**dual 非必须**；优先 7 内置 layout。新增 layout 须复制骨架 + `export-layer` 打标（见 EXAMPLES）。

**cover / catalog 数据门禁**（见 [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md)）：

- cover：`meta` 建议 **5 项**；栅格列数 = `meta.length`（禁止 3 项占 5 列栅格）
- catalog：`catalogPreview` 须 **4 张 preview 图 + hub**（2×2 对称）；禁止 3 图 + 纯文字空格子

- [ ] 文案与用户素材一致
- [ ] layout 字段合法
- [ ] cover/catalog 满足对称数据形态

### 4. 校验与预览

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\validate-project.mjs" --project ppt-projects/<slug>
```

```bash
cd ppt-projects/<slug>
npm install
npm run serve
```

- [ ] validate 通过（含红区 checksum）
- [ ] **逐页 browser 实看**（AP-02）：`#slide-1` … `#slide-N` 每页截图或 CDP，非只抽 dual
- [ ] 预览舞台与 slide 边界清晰；catalog 浅底条目可读（R11 / AP-14）
- [ ] 无重叠（AP-06）、cover meta 等宽、catalog 四格满图（见 [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) §4）
- [ ] 懒加载图已滚动加载
- [ ] 视觉修复未误改 `slides.js` 文案（AP-15）

### 5. 交付

默认**不代点**导出。用户于预览顶栏操作：

| 按钮 | 输出 |
|------|------|
| 导出 PowerPoint（可编辑） | `ppt-editable.pptx` |
| 导出可编辑图片 (ZIP) | `ppt-editable-layers.zip` |
| 导出像素级 PPT | `ppt-raster.pptx` |
| 导出幻灯片图片 (ZIP) | `ppt-slides.zip` |

导出问题 → 只查 [EXPORT.md](EXPORT.md) 黄区打标；**禁止**改红区引擎。

## 用户说「丑」

停止微调 → 整页 redesign + ui-ux 重做 → browser 验证（PM-AP01）。

## 维护者

```powershell
node ppt-maker/scripts/sync-to-agents.mjs
cd .agents
powershell -ExecutionPolicy Bypass -File .\scripts\setup-cursor-agents.ps1
```

详见 [README.md](README.md)、[发布说明.md](发布说明.md)。
