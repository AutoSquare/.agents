# `.agents` 迁移说明（Cursor 细节）

> **多平台安装**（Claude Code、OpenCode、Trea）见 [`README.md`](README.md)。

本目录是可单独迁移的智能体配置包。复制 `.agents/` 到其他账号或其他电脑后，可恢复当前使用的 Skills 与 MCP 配置。

## 包含内容

- `skills/`：完整 Skills 副本，包含 mattpocock 适配技能、文献检索技能、PPT 技能（`ppt-maker`、`academic-ppt-builder`）、**UI/UX 设计技能族（7 个）**、**Karpathy 编码准则（`karpathy-guidelines`）**、**CAD 出图调试（`cad-structure-layout-debug`）** 和辅助工作流技能。
- `mcp-servers-src/`：本地型 MCP 服务源码快照，包含 `academic-research-mcp`、`zotero-mcp`、`deck-builder`、`campus-net-mcp`；不包含 `.git`、`node_modules`、`.venv` 等机器依赖目录。
- `scripts/setup-cursor-agents.ps1`：**仅限 Cursor**：默认安装 Skills + MCP；Rules 默认不装（User 手动录入 AGENTS.md）；可选 `-ProjectPath` 安装 `.mdc` 到指定工程。
- `scripts/sync-ui-ux-skills.ps1`：**维护者**：从 `ui-ux-pro-max-skill` 同步 7 个 UI/UX Skill 到 `.agents/skills/`（含 Cursor 路径改写）。
- `mcp.template.json`：MCP 配置模板，使用 `{{USERPROFILE}}` 占位。
- `manifest.json`：Skills 与 MCP 来源清单。
- `mcp.md`、`skills.md`、`workflows.md`、`output-templates.md`、`environment.md`：给智能体读取的规范文档。

## 新电脑安装步骤

1. 安装基础工具：
   - Git
   - Node.js 与 npm
   - Python 3.10+（若 PATH 中 `python` 是旧版本，安装脚本会优先通过 Windows `py` 启动器选择 3.10+）
   - Cursor

2. 将整个 `.agents/` 文件夹复制到任意项目根目录（UI/UX Skill 已随包附带，**无需** sibling 的 `ui-ux-pro-max-skill` 即可安装）。

3. 进入 `.agents` 目录，在 PowerShell 中执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
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

5. 重启 Cursor，在 `Settings > Tools & MCP` 确认 MCP 服务启用；按终端提醒将 [`rules/universal/AGENTS.md`](rules/universal/AGENTS.md) 各节录入 **User Rules**。

6. （可选）为某工程安装 Project Rules：

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -ProjectPath "D:\GeoPile"
```

7. （可选）验证 `ppt-maker`：

```powershell
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\check-node.mjs"
```

8. （可选）验证 `cad-structure-layout-debug`（需 Python 3.10+ 与 `pip install ezdxf matplotlib pillow`）：

```powershell
$skill = "$env:USERPROFILE\.cursor\skills\cad-structure-layout-debug"
py -3.10 "$skill\examples\minimal_engineering_drawing\generate.py" --out "$skill\out\minimal.dxf"
py -3.10 "$skill\scripts\dxf_smoke_check.py" --dxf "$skill\out\minimal.dxf" --min-entities 10
py -3.10 "$skill\scripts\render_dxf_preview.py" --dxf "$skill\out\minimal.dxf" --png "$skill\out\minimal.png"
```

详见已安装目录内 `README-cursor.md`。

## 维护 UI/UX 技能（可选）

若本机仍有 `ui-ux-pro-max-skill` 源码并修改汉化，进入 `.agents` 后执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\sync-ui-ux-skills.ps1" -Assemble
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
```

## 安装脚本行为

- 读取 [`manifest.json`](manifest.json) 的 `installManifest`，**仅增量替换托管 Skills**（同名 skill 目录）。
- **默认不安装 Rules**；结束时输出 AGENTS.md 手动录入提醒。
- 提供 `-ProjectPath` 时：将托管 14 个 `.mdc` 增量复制到 `{ProjectPath}\.cursor\rules\`。
- 优先从 `mcp-servers-src/` 复制源码并安装以下本地 MCP；若源码快照缺失，则从 GitHub 克隆：
  - `academic-research-mcp`
  - `zotero-mcp`
  - `deck-builder`
  - `campus-net-mcp`（随包附带，仅从 bundled 拷贝）
- Python MCP 依赖安装使用 `pip --no-cache-dir`，并按进程退出码判断失败；pip 缓存损坏产生的 stderr 警告只进入详细日志，不中断脚本。
- MCP 依赖安装会显示当前子步骤和 `pip` / `npm` 输出；Python MCP 会在写入依赖标记前检查 `mcp` 模块是否真实可导入，避免 `.venv` 半安装后重复卡住。`pip install` 使用 `--timeout 30 --retries 3 --prefer-binary`。
- 写入或更新 `C:\Users\<当前用户>\.cursor\mcp.json`（不再注册 `brave-search`）；若曾在旧版本配置中遗留该条目，脚本会移除。
- 如果已有 `mcp.json`，默认创建备份：`mcp.json.bak-时间戳`。
- **不删除**目标目录中 manifest 未列出的 skill 或 rule 文件。

## 可选参数

以下命令均在 `.agents` 目录内执行：

```powershell
# 只安装 Skills 和写入 MCP 配置，不克隆或构建 MCP 服务
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -SkipMcpInstall

# 预览将更新的托管 Skills
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -WhatIf

# 跳过 Skills 更新
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -SkipSkillUpdate

# 安装 Project Rules 到指定工程
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -ProjectPath "D:\GeoPile"

# 调试：不清屏，末尾展开全部安装细节
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -Verbose -SkipMcpInstall

# CI/重定向：保留进度输出，摘要追加在末尾
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -NoClearScreen -SkipMcpInstall

# 禁用摘要着色（重定向到文件时亦自动禁用）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -NoColor -SkipMcpInstall
```

| 参数 | 说明 |
|------|------|
| `-SkipMcpInstall` | 只装 Skills 与 MCP 配置，不构建 MCP 服务 |
| `-WhatIf` | 预览将更新的项，不写盘；输出预览摘要 |
| `-SkipSkillUpdate` | 跳过 Skills 增量更新 |
| `-ProjectPath` | 将托管 `.mdc` 安装到指定工程 `.cursor/rules/` |
| `-Verbose` | 结束时不清屏，并展开缓冲中的详细日志 |
| `-NoClearScreen` | 跳过清屏，摘要追加在进度输出之后 |
| `-NoColor` | 禁用摘要分层着色；输出重定向时亦自动禁用 |

## 注意事项

- `zotero` 需要本机启动 Zotero Desktop；写入能力需要 Zotero 本地桥接插件。
- `academic-research` 基础检索不强制 API Key，但设置可选环境变量能提高配额或稳定性。
- 迁移包不修改 Cursor 内置目录 `~/.cursor/skills-cursor/`。
- **补充网页检索**：本包未内置网页搜索 MCP；需要时由用户使用浏览器或由其他已自行配置的 MCP 承担。
