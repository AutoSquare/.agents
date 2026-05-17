# `.agents` 智能体配置包

可迁移的 **Agent Skills + MCP** 配置仓库，面向文献检索、校园网全文、Zotero、学术 PPT 等场景。复制到任意项目根目录的 `.agents/` 后，按所用 IDE / Agent 运行时选择下方安装方式。

> **给智能体**：进入工作区后先读本文；执行任务时再读 `mcp.md`、`skills.md`、`workflows.md`。

---

## 快速开始（按平台）

### Cursor（推荐，一键安装）

**前置**：Windows 上已安装 Git、Python、Node.js、Cursor。

在仓库根目录打开 PowerShell，执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -OverwriteSkills
```

脚本会：

- 将 `skills/` 复制到 `%USERPROFILE%\.cursor\skills\`
- 从 `mcp-servers-src/` 安装本地 MCP 到 `%USERPROFILE%\.cursor\mcp-servers\`
- 写入或合并 `%USERPROFILE%\.cursor\mcp.json`（已有配置会备份为 `mcp.json.bak-时间戳`）

完成后 **重启 Cursor**，在 **Settings → Tools & MCP** 确认服务已启用。

常用参数：

```powershell
# 只装 Skills，不构建 MCP
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -SkipMcpInstall

# 覆盖已存在的同名 Skill
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -OverwriteSkills
```

更细的 Cursor 说明见 [`PORTABLE.md`](PORTABLE.md)。

---

### Claude Code

本包不附带 Claude 专用安装脚本，采用 **手动挂载**（与 Cursor 共用同一份 `skills/` 与 MCP 源码）。

1. **Skills**（任选其一）  
   - **用户级**：将 `.agents/skills/` 下各子目录复制到 `~/.claude/skills/`（macOS/Linux）或 `%USERPROFILE%\.claude\skills\`（Windows）。  
   - **项目级**：复制到项目内 `.claude/skills/`（若你的 Claude Code 版本支持项目 Skills）。

2. **MCP**  
   - 先在本机构建 MCP（可参考 `scripts/setup-cursor-agents.ps1` 中的 `Install-*` 逻辑，或自行 `git clone` + `pip` / `npm`）。  
   - 将 [`mcp.template.json`](mcp.template.json) 中的 `{{USERPROFILE}}\.cursor\mcp-servers\` 替换为你的实际安装路径（例如 `%USERPROFILE%\.claude\mcp-servers\`）。  
   - 按 Claude Code 文档把 JSON 合并进其 MCP 配置（项目或用户级，以当前版本为准）。

3. **项目引导**（可选）  
   - 在仓库根目录 `CLAUDE.md` 或 `AGENTS.md` 中写明：智能体协作规范见 `.agents/README.md`。

4. **环境变量**  
   - 见下文 [环境变量](#环境变量)；`campus-net` 凭据可放在 `~/.cursor/campus-net/local.env`（与 Cursor 共用路径）或 Claude 配置中的等价 env。

---

### OpenCode

OpenCode 各版本对 Skills / MCP 的路径可能不同，通用做法：

1. 克隆本仓库，将 **`.agents` 放在项目根目录**（或只拷贝 `skills/` + `mcp-servers-src/`）。
2. 在 OpenCode 设置中把 **Skills 目录** 指向本包的 `.agents/skills/`（或复制到 OpenCode 要求的 `skills` 路径）。
3. MCP：用 [`mcp.template.json`](mcp.template.json) 作模板，把 `command` / `args` 改为本机 Python / Node 可执行文件与 `mcp-servers-src` 构建产物路径后，粘贴到 OpenCode 的 MCP 配置界面。
4. 需要 Python MCP（`academic-research`、`campus-net`）时，在对应目录执行 `python -m venv .venv` 与 `pip install -r requirements.txt`；`campus-net` 另需 `playwright install chromium`。

具体菜单以你安装的 OpenCode 版本文档为准。

---

### Trea

Trea 使用 **`.agent`** 目录名（单数）：

1. 下载 / 克隆本仓库。  
2. 将根目录下的 **`.agents` 文件夹重命名为 `.agent`**，并放在 Trea 识别的项目根路径。  
3. Skills 即 `.agent/skills/` 下各子目录；MCP 需在 Trea 中按界面配置，路径参考 [`mcp.template.json`](mcp.template.json) 与 [`mcp.md`](mcp.md)。

---

## 目录结构

```text
.agents/
├── README.md                 # 本文：平台安装、目录索引、Skills/MCP 总表
├── PORTABLE.md               # Cursor 迁移与脚本细节
├── manifest.json             # Skills / MCP 来源清单（机器可读）
├── mcp.md                    # MCP 调用规范（给智能体）
├── skills.md                 # Skills 选择规则（给智能体）
├── workflows.md              # 文献检索 → 下载 → 引用 → PPT 流程
├── output-templates.md       # 候选文献池、摘要、筛选记录等模板
├── environment.md            # 环境变量、路径、维护命令
├── mcp.template.json         # MCP 配置模板（替换 {{USERPROFILE}} 后使用）
├── skills/                   # 全部 Agent Skills（每目录一个 SKILL.md）
├── mcp-servers-src/          # 需本地构建的 MCP 源码快照
│   ├── academic-research-mcp/
│   ├── zotero-mcp/
│   ├── deck-builder/
│   └── campus-net-mcp/       # 校园网馆藏（本仓库附带）
└── scripts/
    └── setup-cursor-agents.ps1   # 仅 Cursor：写入 ~/.cursor/
```

| 路径 | 说明 |
|------|------|
| `skills/` | 智能体技能包；每个子文件夹含 `SKILL.md`，由运行时自动发现。 |
| `mcp-servers-src/` | MCP 服务端源码；**不含** `.venv`、`node_modules`（需安装脚本或手动构建）。 |
| `scripts/setup-cursor-agents.ps1` | **仅 Cursor**：安装 Skills + MCP 到用户目录。 |
| `mcp.template.json` | 非 Cursor 平台手工配置 MCP 时的 JSON 模板。 |
| `workflows.md` | 多技能串联的标准工作流（查文献、筛文献、下全文、做 PPT）。 |
| `output-templates.md` | 统一交付格式（表格、大纲、筛选日志）。 |

---

## Skills 一览

| Skill | 用途 |
|-------|------|
| **文献与综述** | |
| `literature-search` | 构造检索式，调用 academic-research / Zotero，形成候选文献池；需馆藏全文时联动 campus-net。 |
| `paper-screening` | 按纳入/排除标准筛文献，输出筛选记录。 |
| `paper-summary` | 结构化精读单篇或多篇论文（方法、结论、局限等）。 |
| `citation-export` | 导出 APA、GB/T 7714、BibTeX、Markdown 参考文献表。 |
| `research-gap-analysis` | 归纳研究脉络、争议与证据缺口，辅助选题。 |
| `campus-net-onboarding` | 校园网 Profile 配置、CAS/VPN 会话、全文下载与失败清单 `manual_download_required.md`。 |
| **汇报与演示** | |
| `academic-ppt-builder` | 中文学术 PPT 大纲 + 调用 deck-builder / ppt-markdown 生成 pptx。 |
| **工程与协作**（多源自 Matt Pocock 技能适配） | |
| `diagnose` | 有纪律的缺陷/性能诊断循环（重现→缩小→修复→回归）。 |
| `tdd` | 测试驱动开发（红-绿-重构）。 |
| `prototype` | 终端或 UI 一次性原型验证。 |
| `improve-codebase-architecture` | 结合 CONTEXT.md / ADR 寻找架构改进点。 |
| `grill-with-docs` | 对照成文领域模型质询计划并更新文档。 |
| `grill-me` | 对计划/设计穷追问答直至决策清晰。 |
| `setup-matt-pocock-skills` | 初始化 `docs/agents/` 与问题跟踪说明，供工程类技能使用。 |
| `triage` | 工单分拣状态机。 |
| `to-prd` | 将会话整理为 PRD。 |
| `to-issues` | 将计划拆为可领取工单。 |
| `zoom-out` | 从更高层次解释陌生代码或系统。 |
| `handoff` | 生成交接文档供其他智能体续作。 |
| `write-a-skill` | 按规范撰写新 Skill。 |
| `adapt-mattpocock-skills-for-cursor` | 将 mattpocock/skills 批量复制为 Cursor 用户级 Skills。 |
| `git-guardrails` | Claude Code 钩子：拦截危险 git 命令。 |
| `migrate-to-shoehorn` | 测试中的 `as` 断言迁移到 shoehorn。 |
| `scaffold-exercises` | 生成练习/习题目录骨架。 |
| `setup-pre-commit` | Husky + lint-staged + 类型检查 + 测试。 |
| `caveman` | 极简沟通模式（省 token）。 |

分组索引见 [`manifest.json`](manifest.json) 的 `skillGroups`。

---

## MCP 一览

| MCP 名称 | 类型 | 用途 | 前置条件 |
|----------|------|------|----------|
| `academic-research` | 本地 Python | 多源学术检索：OpenAlex、Semantic Scholar、CrossRef、PubMed、arXiv、Unpaywall 等 | Python venv；可选 `S2_API_KEY`、`OPENALEX_EMAIL` 等 |
| `zotero` | 本地 Node | 读写本地 Zotero 库、附件、集合、BibTeX | Zotero Desktop 运行；需构建 `dist/index.js` |
| `deck-builder` | 本地 Node | 结构化生成可编辑 `.pptx` | `npm install` + `npm run build` |
| `ppt-markdown` | npx 远程包 | Markdown 转 PowerPoint | Node.js；`npx -y @botrun/mcp-ppt-generator` |
| `campus-net` | 本地 Python（本仓库附带） | 学校 Profile、馆藏探测、CAS/VPN 会话、DOI 全文下载；失败写入 `manual_download_required.md` | Python venv + Playwright Chromium；可选 `CAMPUS_USERNAME` / `CAMPUS_PASSWORD` 或 `~/.cursor/campus-net/local.env` |

**常用工具（campus-net）**：`get_active_profile`、`onboard_school`、`ensure_auth`、`download_paper`、`download_papers`、`download_cnki`、`detect_network`。

源码位置：`mcp-servers-src/<名称>/`。安装后 Cursor 默认路径：`%USERPROFILE%\.cursor\mcp-servers\`。

详细能力与调用约束见 [`mcp.md`](mcp.md)。

---

## 环境变量

| 变量 | 适用 MCP | 说明 |
|------|----------|------|
| `S2_API_KEY` | academic-research | Semantic Scholar 高配额（可选） |
| `OPENALEX_EMAIL` | academic-research、campus-net | OpenAlex polite pool |
| `CROSSREF_EMAIL` | academic-research、campus-net | CrossRef polite pool |
| `NCBI_API_KEY` | academic-research | PubMed 高配额（可选） |
| `CAMPUS_USERNAME` / `CAMPUS_PASSWORD` | campus-net | 学校统一身份 / VPN（可选，亦可写 `local.env`） |
| `CAMPUS_OUTPUT_DIR` | campus-net | PDF 默认输出目录 |

`campus-net` 用户配置目录（与 Cursor 共用）：`~/.cursor/campus-net/`（含 `local.env`、`sessions/`、`active.json`）。

---

## 智能体阅读顺序

1. 本文（安装与总览）  
2. [`mcp.md`](mcp.md) — 调用 MCP 前  
3. [`skills.md`](skills.md) — 选择技能前  
4. [`workflows.md`](workflows.md) — 文献/PPT 类任务  
5. [`output-templates.md`](output-templates.md) — 需要统一交付格式时  
6. [`environment.md`](environment.md) — 排错与更新  

