# 环境与维护

## 配置路径

- Cursor 全局 MCP 配置：`%USERPROFILE%\.cursor\mcp.json`
- Codex MCP 配置：通过 `codex mcp add/remove/list/get` 管理，脚本不直接写 `config.toml`
- Cursor 用户级 Skills：`%USERPROFILE%\.cursor\skills`
- Codex 用户级 Skills：`%USERPROFILE%\.codex\skills`
- Codex 全局规则入口：`%USERPROFILE%\.codex\AGENTS.md`
- Codex 按需规则：`%USERPROFILE%\.codex\agent-rules`
- **Cursor User Rules**：手动录入，源文件 `.agents/rules/universal/AGENTS.md`（setup 默认不装 rules）
- **Cursor Project Rules（可选）**：`-ProjectPath` 安装到 `{工程根}/.cursor/rules`
- Cursor 本地 MCP 服务：`%USERPROFILE%\.cursor\mcp-servers`
- Codex 本地 MCP 服务：`%USERPROFILE%\.codex\mcp-servers`
- 迁移包 Skills 副本：`.agents/skills`
- 迁移包 MCP 源码快照：`.agents/mcp-servers-src`
- **Cursor** 写入脚本（非通用 IDE 安装名）：`scripts/setup-cursor-agents.ps1`（在 `.agents` 目录内执行）
- **Codex** 写入脚本：`scripts/setup-codex-agents.ps1`（在 `.agents` 目录内执行）
- **UI/UX 技能同步**（维护者）：`scripts/sync-ui-ux-skills.ps1`（在 `.agents` 目录内执行）
- 安装记录：`MCP与Skills配置记录.md`（若存在）

## 环境变量

```powershell
setx S2_API_KEY "你的 Semantic Scholar API Key"
setx OPENALEX_EMAIL "你的邮箱"
setx CROSSREF_EMAIL "你的邮箱"
setx NCBI_API_KEY "你的 NCBI API Key"
```

- `S2_API_KEY`：Semantic Scholar 高配额，可选。
- `OPENALEX_EMAIL`：OpenAlex polite pool，可选。
- `CROSSREF_EMAIL`：CrossRef polite pool，可选。
- `NCBI_API_KEY`：PubMed 高配额，可选。
- **校园网馆藏**：参见 `campus-net` MCP 与 `CAMPUS_*` 变量（若启用）。
- **`GEMINI_API_KEY`**（可选）：`design` Skill 下 Logo/CIP/图标 **生成** 脚本需要；使用 `setx GEMINI_API_KEY "..."` 或系统环境变量，并执行 `pip install google-genai`。不 patch 脚本读取 `.env` 路径。

## UI/UX 技能维护

真相源为同仓库或 sibling 路径下的 `ui-ux-pro-max-skill/`。更新汉化或模板后，进入 `.agents` 执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\sync-ui-ux-skills.ps1" -Assemble

# 仅复制 .agents 到新机器、无 sibling 仓库时
powershell -ExecutionPolicy Bypass -File ".\scripts\sync-ui-ux-skills.ps1" -UpstreamPath "D:\path\to\ui-ux-pro-max-skill"

# 安装到 Cursor（Skills + MCP；Rules 见终端提醒手动录入 AGENTS.md）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"

# 安装到 Codex（Rules + Skills + MCP；只覆盖 manifest 托管项）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1"

# 可选：Project Rules 到指定工程
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -ProjectPath "D:\GeoPile"
```

**前置**：Python 3（`ui-ux-pro-max`、`design-system` search-slides）；Node.js 18+（`brand`、`design-system`、`ui-styling` 的 `.cjs` 与 shadcn CLI）。

**`banner-design` 限制**：完整生成链引用未打包 Skill `ai-artist`、`ai-multimodal`、`chrome-devtools`；迁入包仅含 SKILL + references。

**Claude Code 手动安装**：若复制到 `~/.claude/skills/`，须将 SKILL 内 `$env:USERPROFILE\.cursor\skills\` 替换为 Claude 用户级路径（含 `ppt-maker`、`ui-ux-pro-max`）。

**Codex 安装**：使用 `setup-codex-agents.ps1` 写入 `%USERPROFILE%\.codex\skills\`；若手动复制 Skill，须将仅适用于 Cursor 的命令路径替换为 Codex 用户级路径。

## karpathy-guidelines 维护

**编辑源**：工作区 sibling `andrej-karpathy-skills/`；**发布副本**：`.agents/skills/karpathy-guidelines/`、`.agents/rules/cursor/karpathy-guidelines.mdc`、`AGENTS.md` §11（禁止手改副本，须 sync）。

```powershell
# andrej-karpathy-skills → .agents（四路同步）
node andrej-karpathy-skills/scripts/sync-to-agents.mjs
node andrej-karpathy-skills/scripts/sync-to-agents.mjs --dry-run

# 安装到 Cursor
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"

# 安装到 Codex
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1"
```

修改四原则时须同步源仓库内 `SKILL.md`、`CLAUDE.md`、`.cursor/rules/karpathy-guidelines.mdc`，再运行上述 sync。

## ppt-maker 维护

**编辑源**：工作区根 `ppt-maker/`（沙箱）；**发布副本**：`.agents/skills/ppt-maker/`（禁止手改，须 sync）。

```powershell
# 沙箱 → .agents 发布副本
node ppt-maker/scripts/sync-to-agents.mjs
node ppt-maker/scripts/sync-to-agents.mjs --dry-run

# 安装到 Cursor
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
```

**刷新 kit-template**（维护者，可选）：

```powershell
node ppt-maker/scripts/sync-template.mjs --upstream "D:\path\to\ppt-maker-kit"
node ppt-maker/scripts/sync-to-agents.mjs
```

**用户任务副本**：每次任务在工作区 `ppt-projects/{english-slug}/`；勿提交进 Git（根 `.gitignore` 已忽略）。

**前置**：Node.js 18+（`npm install` / `npm run serve`）；Python 3 + `ui-ux-pro-max`（风格 `design-tokens.css`）。

**冒烟**：

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\check-node.mjs"
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\slug.mjs" --generate
node "$env:USERPROFILE\.codex\skills\ppt-maker\scripts\check-node.mjs"
```

## 重启要求

- 修改 `%USERPROFILE%\.cursor\mcp.json` 后，需要重启 Cursor 或重新打开 Agent 会话。
- 使用 `codex mcp add/remove` 更新 MCP 后，需要新开 Codex 会话。
- 新增或修改 Skills 后，建议重启 Cursor 或新开 Agent 会话。
- 不要修改 `%USERPROFILE%\.cursor\skills-cursor`，该目录为 Cursor 内置 Skills。

## 迁移安装

将 `.agents/` 复制到新电脑任意项目根目录后，进入 `.agents` 执行 setup；按终端提醒手动录入 User Rules。

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1"
```

安装脚本会优先使用 `.agents/mcp-servers-src/` 内的源码快照；如果源码快照缺失，才从对应 GitHub 仓库克隆。

Codex 脚本的增量边界：只覆盖 `manifest.json` 的 `codexInstallManifest` 声明的同名托管 skill、rule、MCP 源码目录和 MCP 注册；用户自装内容不删除、不卸载。

## 本地 MCP 更新命令

```powershell
# Cursor
Set-Location "$env:USERPROFILE\.cursor\mcp-servers\academic-research-mcp"
git pull
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Set-Location "$env:USERPROFILE\.cursor\mcp-servers\zotero-mcp"
git pull
npm install
npm run build

Set-Location "$env:USERPROFILE\.cursor\mcp-servers\deck-builder"
git pull
npm install
npm run build

# Codex
Set-Location "$env:USERPROFILE\.codex\mcp-servers\academic-research-mcp"
git pull
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Set-Location "$env:USERPROFILE\.codex\mcp-servers\zotero-mcp"
git pull
npm install
npm run build

Set-Location "$env:USERPROFILE\.codex\mcp-servers\deck-builder"
git pull
npm install
npm run build
```

如有 `campus-net-mcp`：在项目侧更新 `.agents/mcp-servers-src/campus-net-mcp` 后再次运行对应平台 setup，或直接覆盖 `%USERPROFILE%\.cursor\mcp-servers\campus-net-mcp` / `%USERPROFILE%\.codex\mcp-servers\campus-net-mcp` 并重装 venv 依赖。

## 排查顺序

1. 确认 Cursor 已重启，或已新开 Codex 会话。
2. Cursor：在 `Settings > Tools & MCP` 确认 MCP 已启用；Codex：执行 `codex mcp list`。
3. Cursor：检查 `mcp.json` 是否为合法 JSON；Codex：用 `codex mcp get <name> --json` 检查配置。
4. 检查本地入口文件是否存在：
   - `%USERPROFILE%\.cursor\mcp-servers\academic-research-mcp\server.py`
   - `%USERPROFILE%\.cursor\mcp-servers\zotero-mcp\dist\index.js`
   - `%USERPROFILE%\.cursor\mcp-servers\deck-builder\build\index.js`
   - `%USERPROFILE%\.codex\mcp-servers\academic-research-mcp\server.py`
   - `%USERPROFILE%\.codex\mcp-servers\zotero-mcp\dist\index.js`
   - `%USERPROFILE%\.codex\mcp-servers\deck-builder\build\index.js`
5. 使用 Zotero MCP 前确认 Zotero Desktop 已启动。
6. UI/UX：`python "%USERPROFILE%\.cursor\skills\ui-ux-pro-max\scripts\search.py" "test" --design-system -n 1` 应能输出结果（终端文案可能仍为英文）。
