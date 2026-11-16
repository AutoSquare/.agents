# MCP 服务规范

迁移包内提供两类 MCP 资产：

- `mcp.template.json`：可迁移 MCP 配置模板。
- `mcp-servers-src/`：`academic-research`、`zotero`、`deck-builder`、`campus-net-mcp` 等的源码或可安装副本。
- **Cursor**：将 Skills 与用户级 MCP 写入 `~\.cursor\` 时，请进入 **配置包根目录** 执行 **`scripts/setup-cursor-agents.ps1`**（非 Claude Desktop / 其他 IDE 的通用安装名）。
- **Codex**：将 Rules、Skills 与用户级 MCP 写入 `~\.codex\` 时，请进入 **配置包根目录** 执行 **`scripts/setup-codex-agents.ps1`**；脚本通过 `codex mcp add/remove` 刷新托管 MCP，不卸载用户自装 MCP。
- **DSH**：将 Skills、Rules 与本地 MCP 写入 `$DSH_HOME`（默认 `~\.dsh\`）时，请进入 **配置包根目录** 执行 **`scripts/setup-dsh-agents.ps1`**；脚本把 `@deepseek-ai/dsh-mcp-client` 条目写入 `profiles\<profile>\cordis.patch.yml` 的托管标记块。

Cursor 安装到当前账号后，全局 MCP 配置文件为：

```text
C:\Users\25705\.cursor\mcp.json
```

Codex 安装后使用 CLI 管理：

```powershell
codex mcp list
codex mcp get academic-research --json
```

## academic-research

- 用途：多源学术检索。
- 能力范围：OpenAlex、Semantic Scholar、CrossRef、PubMed、arXiv、Google Scholar、ORCID、Unpaywall。
- 推荐场景：查论文、找 DOI、找开放获取版本、做综述候选文献池、追踪引用网络。
- 迁移包源码：`<配置包根目录>/mcp-servers-src/academic-research-mcp`
- 安装后路径：Cursor 为 `%USERPROFILE%\.cursor\mcp-servers\academic-research-mcp`；Codex 为 `%USERPROFILE%\.codex\mcp-servers\academic-research-mcp`
- 可选环境变量：`S2_API_KEY`、`OPENALEX_EMAIL`、`CROSSREF_EMAIL`、`NCBI_API_KEY`。
- 调用要求：检索结果必须标注来源；不要把单一数据库命中结果当作完整检索结论。

## zotero

- 用途：访问本地 Zotero 文献库。
- 推荐场景：检索已有文献、读取条目和附件信息、导出 BibTeX、管理集合和笔记。
- 迁移包源码：`<配置包根目录>/mcp-servers-src/zotero-mcp`
- 安装后路径：Cursor 为 `%USERPROFILE%\.cursor\mcp-servers\zotero-mcp`；Codex 为 `%USERPROFILE%\.codex\mcp-servers\zotero-mcp`
- 前置条件：本机 Zotero Desktop 需要运行。
- 调用要求：未确认本地桥接插件状态前，优先执行只读操作；写入前说明具体变更对象。

## deck-builder

- 用途：生成结构化、可编辑的 `.pptx`。
- 推荐场景：根据研究材料生成正式 PPT、汇报稿、开题或文献综述展示。
- 迁移包源码：`<配置包根目录>/mcp-servers-src/deck-builder`
- 安装后路径：Cursor 为 `%USERPROFILE%\.cursor\mcp-servers\deck-builder`；Codex 为 `%USERPROFILE%\.codex\mcp-servers\deck-builder`
- 调用要求：先形成幻灯片大纲，再生成 PPT；文件名优先英文。

## campus-net

- 用途：通用学校 Profile YAML 驱动馆藏探针、网页 VPN 与统一身份认证自动会话、馆藏 DOI 解析与开放获取下载；可选用知网检索页。
- 推荐场景：自检 `get_active_profile` → `discover_school_profile` / `onboard_school` / `save_school_profile` → `detect_network`、`ensure_auth` → `download_paper` 或 `download_cnki`。
- 迁移包源码：`<配置包根目录>/mcp-servers-src/campus-net-mcp`
- 安装后路径：Cursor 为 `%USERPROFILE%\.cursor\mcp-servers\campus-net-mcp`；Codex 为 `%USERPROFILE%\.codex\mcp-servers\campus-net-mcp`。
- 用户侧配置与 Cookie 会话：Cursor 为 `%USERPROFILE%\.cursor\campus-net\`；Codex 为 `%USERPROFILE%\.codex\campus-net\`；DSH 为 `%USERPROFILE%\.dsh\campus-net\`（由 `CAMPNET_USER_ROOT` 指定）。可用 `CAMPNET_USER_ROOT` 覆盖。
- 环境变量建议：`CAMPUS_USERNAME`、`CAMPUS_PASSWORD`；可选 `OPENALEX_EMAIL`、`CROSSREF_EMAIL`（改善 Unpaywall 访问）；可选 `CAMPUS_OUTPUT_DIR` 固定 PDF 输出目录（未设时默认在当前工作目录下的 `papers/`）。
- 调用要求：未完成学校选择与凭据配置前不得静默抓取；`download_paper` / `download_papers` 会自动准备会话，失败时写入输出目录下的 `manual_download_required.md`（文首说明原因，逐条给出 DOI 与出版商链接）。
- 主要工具：`download_paper`（单篇）、`download_papers`（批量）、`download_cnki`、`ensure_auth`、`get_active_profile`。
- Agent 技能：`campus-net-onboarding`、`literature-search`（与 `academic-research` 串联）。

## DSH 注册方式

- 配置文件：`%USERPROFILE%\.dsh\profiles\desktop\cordis.patch.yml`；每个服务器一条 `@deepseek-ai/dsh-mcp-client`，条目由 `setup-dsh-agents.ps1` 写入托管标记块（先备份，再写临时文件并用 PyYAML 校验，最后原子替换）。新增条目必须放在 `- insert:` 列表中；裸 `- id: ...` 会被当作覆盖目标并报 `entry not found`。
- 工具名：`mcp__<serverName>__<toolName>`，例如 `mcp__academic-research__smart_search`、`mcp__campus-net__download_paper`。只使用工具列表中实际出现的名称。
- 凭据：DSH 会清洗 stdio 子进程中匹配 `/KEY|PASSWORD|SECRET|TOKEN/i` 的变量，因此 `S2_API_KEY`、`NCBI_API_KEY`、`CAMPUS_PASSWORD`、`PADDLEOCR_TOKEN` 等必须在条目 `env` 中用 `!!js process.env.VAR || ''` 显式传入；未设置时按空字符串处理。
- `campus-net`：`CAMPNET_USER_ROOT` 固定为 `%USERPROFILE%\.dsh\campus-net`，避免读写 Codex 的配置目录。
- 本地服务路径：`%USERPROFILE%\.dsh\mcp-servers\<name>`；`academic-research` 与 `campus-net` 用 `.venv\Scripts\python.exe server.py`，`zotero` 用 `node dist\index.js`，`deck-builder` 用 `node build\index.js`（patch 中写 node 绝对路径）。
- 修改 patch 后等待 DSH HMR 或重启桌面端；新会话确认 `mcp__academic-research__*` 等工具出现，未出现则检查 Plugins 页面与 patch 合法性。
