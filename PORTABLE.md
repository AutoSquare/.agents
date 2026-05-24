# `.agents` 迁移说明（Cursor 细节）

> **多平台安装**（Claude Code、OpenCode、Trea）见 [`README.md`](README.md)。

本目录是可单独迁移的智能体配置包。复制 `.agents/` 到其他账号或其他电脑后，可恢复当前使用的 Skills 与 MCP 配置。

## 包含内容

- `skills/`：完整 Skills 副本，包含 mattpocock 适配技能、文献检索技能、PPT 技能（`ppt-maker`、`academic-ppt-builder`）、**UI/UX 设计技能族（7 个）**、**Karpathy 编码准则（`karpathy-guidelines`）** 和辅助工作流技能。
- `mcp-servers-src/`：本地型 MCP 服务源码快照，包含 `academic-research-mcp`、`zotero-mcp`、`deck-builder`、`campus-net-mcp`；不包含 `.git`、`node_modules`、`.venv` 等机器依赖目录。
- `scripts/setup-cursor-agents.ps1`：**仅限 Cursor**：将 `skills/` 复制到 `%USERPROFILE%\.cursor\skills\`，并写入 `%USERPROFILE%\.cursor\mcp.json`。
- `scripts/sync-ui-ux-skills.ps1`：**维护者**：从 `ui-ux-pro-max-skill` 同步 7 个 UI/UX Skill 到 `.agents/skills/`（含 Cursor 路径改写）。
- `mcp.template.json`：MCP 配置模板，使用 `{{USERPROFILE}}` 占位。
- `manifest.json`：Skills 与 MCP 来源清单。
- `mcp.md`、`skills.md`、`workflows.md`、`output-templates.md`、`environment.md`：给智能体读取的规范文档。

## 新电脑安装步骤

1. 安装基础工具：
   - Git
   - Node.js 与 npm
   - Python
   - Cursor

2. 将整个 `.agents/` 文件夹复制到任意项目根目录（UI/UX Skill 已随包附带，**无需** sibling 的 `ui-ux-pro-max-skill` 即可安装）。

3. 在 PowerShell 中执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -OverwriteSkills
```

4. 按需设置环境变量（示例）：

```powershell
setx S2_API_KEY "你的 Semantic Scholar API Key"
setx OPENALEX_EMAIL "你的邮箱"
setx CROSSREF_EMAIL "你的邮箱"
setx NCBI_API_KEY "你的 NCBI API Key"
setx GEMINI_API_KEY "你的 Gemini API Key"
```

（`GEMINI_API_KEY` 仅在使用 `design` 生成 Logo/CIP/图标时需要；`ui-ux-pro-max` 检索不需要。）

5. 重启 Cursor，在 `Settings > Tools & MCP` 确认 MCP 服务启用。

6. （可选）验证 `ppt-maker`：

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\check-node.mjs"
```

## 维护 UI/UX 技能（可选）

若本机仍有 `ui-ux-pro-max-skill` 源码并修改汉化，在仓库根执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\sync-ui-ux-skills.ps1" -Assemble
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -OverwriteSkills
```

## 安装脚本行为

- 将 `.agents/skills/*` 复制到 `C:\Users\<当前用户>\.cursor\skills\`。
- 优先从 `mcp-servers-src/` 复制源码并安装以下本地 MCP；若源码快照缺失，则从 GitHub 克隆：
  - `academic-research-mcp`
  - `zotero-mcp`
  - `deck-builder`
  - `campus-net-mcp`（随包附带，仅从 bundled 拷贝）
- 写入或更新 `C:\Users\<当前用户>\.cursor\mcp.json`**（不再注册 `brave-search`）；若曾在旧版本配置中遗留该条目，本会话会移除。
- 如果已有 `mcp.json`，默认创建备份：`mcp.json.bak-时间戳`。
- 默认不覆盖已存在的同名 Skill；使用 `-OverwriteSkills` 可覆盖。

## 可选参数

```powershell
# 只安装 Skills 和写入 MCP 配置，不克隆或构建 MCP 服务
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -SkipMcpInstall

# 覆盖当前账号中已有的同名 Skills
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -OverwriteSkills
```

## 注意事项

- `zotero` 需要本机启动 Zotero Desktop；写入能力需要 Zotero 本地桥接插件。
- `academic-research` 基础检索不强制 API Key，但设置可选环境变量能提高配额或稳定性。
- 迁移包不修改 Cursor 内置目录 `~/.cursor/skills-cursor/`。
- **补充网页检索**：本包未内置网页搜索 MCP；需要时由用户使用浏览器或由其他已自行配置的 MCP 承担。
