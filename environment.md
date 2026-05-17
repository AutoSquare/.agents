# 环境与维护

## 配置路径

- 全局 MCP 配置：`C:\Users\25705\.cursor\mcp.json`
- 用户级 Skills：`C:\Users\25705\.cursor\skills`
- 本地 MCP 服务：`C:\Users\25705\.cursor\mcp-servers`
- 迁移包 Skills 副本：`.agents/skills`
- 迁移包 MCP 源码快照：`.agents/mcp-servers-src`
- **Cursor** 写入脚本（非通用 IDE 安装名）：`.agents/scripts/setup-cursor-agents.ps1`
- 安装记录：`MCP与Skills配置记录.md`

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
- **校园网馆藏**：参见 `campus-net` MCP 与 `environment` 段落中的 `CAMPUS_*`（若启用）。

## 重启要求

- 修改 `C:\Users\25705\.cursor\mcp.json` 后，需要重启 Cursor 或重新打开 Agent 会话。
- 新增或修改 Skills 后，建议重启 Cursor 或新开 Agent 会话。
- 不要修改 `C:\Users\25705\.cursor\skills-cursor`，该目录为 Cursor 内置 Skills。

## 迁移安装

将 `.agents/` 复制到新电脑任意项目根目录后执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -OverwriteSkills
```

安装脚本会优先使用 `.agents/mcp-servers-src/` 内的源码快照；如果源码快照缺失，才从对应 GitHub 仓库克隆。

## 本地 MCP 更新命令

```powershell
Set-Location "C:\Users\25705\.cursor\mcp-servers\academic-research-mcp"
git pull
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Set-Location "C:\Users\25705\.cursor\mcp-servers\zotero-mcp"
git pull
npm install
npm run build

Set-Location "C:\Users\25705\.cursor\mcp-servers\deck-builder"
git pull
npm install
npm run build
```

如有 `campus-net-mcp`：在项目侧更新 `.agents/mcp-servers-src/campus-net-mcp` 后再次运行 `setup-cursor-agents.ps1` 或直接覆盖 `%USERPROFILE%\.cursor\mcp-servers\campus-net-mcp` 并重装 venv 依赖。

## 排查顺序

1. 确认 Cursor 已重启。
2. 在 `Settings > Tools & MCP` 确认 MCP 已启用。
3. 检查 `mcp.json` 是否为合法 JSON。
4. 检查本地入口文件是否存在：
   - `C:\Users\25705\.cursor\mcp-servers\academic-research-mcp\server.py`
   - `C:\Users\25705\.cursor\mcp-servers\zotero-mcp\dist\index.js`
   - `C:\Users\25705\.cursor\mcp-servers\deck-builder\build\index.js`
5. 使用 Zotero MCP 前确认 Zotero Desktop 已启动。
