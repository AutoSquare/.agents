---
name: ppt-maker
description: 将素材与结构化幻灯片数据生成为 Vue 16:9 预览页，并在浏览器中导出 PPTX/ZIP。用户说「做 PPT、幻灯片、演示文稿」时默认启用本 Skill。风格须按用户提示词定制，执行 Agent 须显式调用 /ui-ux-pro-max，禁止仅交付模板默认皮肤。学术快出 pptx（答辩、开题、文献综述）用 academic-ppt-builder；仅改 ppt-projects 英文副本。
---

# PPT 制作（ppt-maker）

## 入口

安装后 Cursor 自动发现本 Skill；亦可 `@ppt-maker/SKILL.md` 显式触发。

**禁止**在未启用本 Skill 时执行脚手架或修改 `kit-template/`。

## 与 academic-ppt-builder 分流

| 用户意图 | 选用 |
|----------|------|
| 「做 PPT / 幻灯片 / 演示」（未说明形式） | **ppt-maker**（本 Skill） |
| 答辩、开题、文献综述、要快出 pptx、deck-builder | `academic-ppt-builder` + MCP |
| 融资 Pitch、商业 HTML 演示 | `slides` + `design-system` |

已有 `academic-ppt-builder` 大纲 → 映射为 `slides.js`（见 `.agents/output-templates.md`）。

## 路径约定

| 场景 | 根路径 |
|------|--------|
| **运行时（推荐）** | `%USERPROFILE%\.cursor\skills\ppt-maker\` |
| **沙箱调试** | 工作区 `ppt-maker/` |

脚本占位：`$SKILL = "$env:USERPROFILE\.cursor\skills\ppt-maker"`（沙箱下将 `$SKILL` 换为 `ppt-maker`）。

## 架构速览

| 层级 | 路径 | 规则 |
|------|------|------|
| 开发基座 | `ppt-maker-kit/` 或 `ppt_style/` | **禁止修改**（维护者 sync 到模板） |
| 分发模板 | `{SKILL}/kit-template/` | **禁止修改**（只读复制源） |
| 用户任务副本 | `ppt-projects/{english-slug}/` | **仅在此目录** 写 slides、素材、样式 |

文件夹名必须英文（`a-z0-9-`）；中文标题写在 `src/config/project.js` 与 `src/data/slides.js`。

## 风格定制（必调 ui-ux-pro-max）

**禁止**仅交付模板默认皮肤（Editorial 暖色：`--color-accent-warm: #C2410C` 等）。视觉须来自**用户提示词**（或经追问确认后的描述）。

### 分工

| 角色 | 职责 | 禁止 |
|------|------|------|
| **ppt-maker** | 脚手架、slides、素材、Node/serve、提醒调用 ui-ux-pro-max | 内嵌 Python 设计脚本；代替 ui-ux-pro-max 做检索 |
| **执行 Agent（你）** | 向用户说明并**在本对话调用** `/ui-ux-pro-max`；将结果写入用户副本 | 静默保留默认 `design-tokens.css` 却声称已定制 |
| **ui-ux-pro-max** | `--design-system` 产出 pattern / 配色 / 排版 | 直接改 Vue 文件（由 Agent 映射到副本） |

### 执行步骤（Agent 必做）

1. **整理 `styleBrief`**：从用户消息提取行业、受众、调性、明暗偏好；写入 `.ppt-maker-project.json` 的 `styleBrief`（脚手架可用 `--style-brief` 预填）。
2. **用户未给任何风格描述时**：先追问 1–2 题（例如：行业/场景、冷暖色、正式还是活泼），**确认后再**进入 ui-ux-pro-max；不得静默使用默认 token。
3. **向用户复述** `styleBrief` 并请确认；然后明确告知：**「接下来将在本对话调用 `/ui-ux-pro-max`，根据你的描述生成配色与排版。」**
4. **调用 ui-ux-pro-max**（检测 `~/.cursor/skills/ui-ux-pro-max/SKILL.md`）：
   - 存在 → 在 `ppt-projects/<slug>/` 下执行（查询词用英文更佳）：
     ```powershell
     python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "<styleBrief 英文关键词>" --design-system --persist -p "<slug>" -f markdown
     ```
   - 将 `design-system/MASTER.md` 映射到 `src/styles/design-tokens.css`（主色、背景、强调色、字体变量）；**不改** `SlideFrame` / `CaseCard` 的 DOM 结构。
   - 调用后向用户摘要：采用的 pattern / 主色 / 字体气质（一两句话）。
   - 更新 `.ppt-maker-project.json` 的 `designSystemQuery`。
5. **ui-ux-pro-max 未安装**：提示进入 `.agents` 运行 `powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"`；若继续，须说明「将使用套件默认 Editorial 风格」，**获用户确认**后才可保留默认 token。
6. **跳过 ui-ux-pro-max**：须写明风险 + 用户确认；禁止未调用却声称已按用户风格定制。

## 工作流

### 0. 前置检查

**风格（见上文）** — 在写 `design-tokens.css` 之前完成 `styleBrief` 与 `/ui-ux-pro-max` 调用。

**Node.js**

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\check-node.mjs"
```

- 失败且用户同意（仅 Windows）→ 加 `--install`
- 用户拒绝 → 停止；给 https://nodejs.org 链接

### 1. 脚手架（只复制）

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\slug.mjs" --generate
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\scaffold.mjs" --slug <english-slug> --workspace "<工作区绝对路径>"
# 可选：预填风格
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\scaffold.mjs" --slug <english-slug> --workspace "<工作区绝对路径>" --style-brief "学术答辩，稳重深蓝"
```

- 产出：`ppt-projects/<slug>/` + `.ppt-maker-project.json`
- 目标已存在：默认报错；用户确认后才加 `--force`
- 维护者同步模板：`node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\sync-template.mjs" [--upstream <path>]`

### 2. 在副本内生成内容

阅读 **`ppt-projects/<slug>/docs/slides-schema.md`**（复制自带）。

1. 用户素材 → `public/assets/materials/`（**英文文件名**）
2. 编写 `src/data/slides.js`（中文内容 OK）
3. 更新 `src/config/project.js`（`appTitle` 等）
4. **样式（必做）**：调用 `/ui-ux-pro-max` 后更新 `src/styles/design-tokens.css`

**禁止**编辑 `kit-template/`、`ppt-maker-kit/`；**禁止**未调用 ui-ux-pro-max 却假装已定制。

### 3. 安装依赖并启动预览

在 `ppt-projects/<slug>/`：

```bash
npm install
npm run serve
```

- `serve` 在**后台**运行；从终端日志读取实际 URL（默认端口 8080，占用时可能 8081…）
- 告知用户手动启动命令

### 4. 交付（不自动导出 PPT）

**默认不执行** CLI 导出。用户在浏览器预览页顶栏自行操作：

| 按钮 | 输出 |
|------|------|
| 导出 PowerPoint（可编辑） | `ppt-editable.pptx` |
| 导出像素级 PPT | `ppt-raster.pptx` |
| 导出幻灯片图片 (ZIP) | `ppt-slides.zip` |

**导出前提示**：滚动浏览每一页确保懒加载图片已加载；顶栏选择分辨率（默认 4K）。

用户明确要求离线可编辑 pptx 时，方可在副本内运行 `npm run export:pptx` → `output/`。

## 更多说明

见 [REFERENCE.md](REFERENCE.md)。
