# `.agents` 智能体配置包

可迁移的 **Agent Skills + Rules + MCP** 配置仓库，面向文献检索、校园网全文、Zotero、学术 PPT、**UI/UX 设计（React Native）**、CAD 工程出图调试、Superpowers 软件开发方法与去重后的 gstack 工程工作流等场景。复制到任意项目根目录的 `.agents/` 后，按所用 IDE / Agent 运行时选择下方安装方式。

> **给智能体**：进入工作区后先读本文；执行任务时再读 `mcp.md`、`skills.md`、`workflows.md`。

---

## 快速开始（按平台）

### Codex（一键安装）

**前置**：Windows 上已安装 Git for Windows（含 Git Bash）、Python 3.10+、Node.js、npm 与 Codex CLI（需支持 `codex mcp`，本包按 `codex-cli 0.134.0` 验证）。若 PATH 中的 `python` 是旧版本，脚本会优先通过 Windows `py` 启动器选择 `py -3.10` 或更高版本。

进入 `.agents` 目录，在 PowerShell 中执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1"
```

脚本会：

- 将托管 `skills/` **增量覆盖**到 `%USERPROFILE%\.codex\skills\`（只覆盖 manifest 中同名托管项，不删除用户自装 skill）
- 安装 33 个去重后的 Codex 版 gstack 入口，并在 `%USERPROFILE%\.codex\skills\gstack\` 首次编译共享运行时
- 将 Codex 全局入口安装到 `%USERPROFILE%\.codex\AGENTS.md`，并备份已有文件
- 将按需规则安装到 `%USERPROFILE%\.codex\agent-rules\`
- 从 `mcp-servers-src/` 安装本地 MCP 到 `%USERPROFILE%\.codex\mcp-servers\`
- 重复安装时保留 Codex MCP 的 `.venv` / `node_modules`，依赖清单未变化则跳过重复依赖安装
- 用 `codex mcp remove/add` 刷新本包托管的 MCP 注册，不卸载用户自己添加的其他 MCP

常用参数：

```powershell
# 预览将更新的托管项，不写入磁盘
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -WhatIf -NoClearScreen

# 只安装 Rules 与 Skills，不构建或注册 MCP
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -SkipMcpInstall

# 不安装 gstack；或只复制 gstack 源码、暂不编译运行时
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -SkipGstackInstall
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -SkipGstackBuild

# 指定 Codex 用户目录（测试或多环境时使用）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -CodexHome "D:\tmp\codex-home"
```

更细的 Codex 说明见 [`CODEX.md`](CODEX.md)。

---

### Antigravity（一键安装）

**前置**：Windows 上已安装 Git、Python 3.10+、Node.js、npm 与 Antigravity CLI。若 PATH 中的 `python` 是旧版本，脚本会优先通过 Windows `py` 启动器寻找 `py -3.10` 或更高版本。

进入 `.agents` 目录，在 PowerShell 中执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-antigravity-agents.ps1"
```

脚本会：

- 将托管 `skills/` **增量覆盖**到 `%USERPROFILE%\.gemini\config\plugins\agents\skills\`（只覆盖 manifest 中同名托管项，**不删除**用户自己安装的其他 skill）
- 将 `rules/antigravity/` 下的 Markdown 规则聚合注入到 `%USERPROFILE%\.gemini\config\plugins\agents\plugin.json` 的 `system_prompt` 中
- 从 `mcp-servers-src/` 安装本地 MCP 到 `%USERPROFILE%\.gemini\config\plugins\agents\mcp-servers\`，并自动安装 Python/Node 依赖
- 更新 `plugin.json` 时采用**增量聚合**逻辑：只刷新本包托管的 MCP 注册，**完全保留**用户自己在此文件中配置的其他 MCP 记录

常用参数：

```powershell
# 预览将更新的托管项，不写入磁盘
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-antigravity-agents.ps1" -WhatIf

# 只更新 Rules 与 Skills，跳过 MCP 构建与依赖安装
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-antigravity-agents.ps1" -SkipMcpInstall

# 自定义 pip 镜像或使用官方源（默认使用清华源）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-antigravity-agents.ps1" -PipIndexUrl "https://mirrors.aliyun.com/pypi/simple/"
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-antigravity-agents.ps1" -UseOfficialPipIndex
```

更细的 Antigravity 说明见 [`ANTIGRAVITY.md`](ANTIGRAVITY.md)。

---

### Cursor（一键安装）

**前置**：Windows 上已安装 Git for Windows（含 Git Bash）、Python 3.10+、Node.js、npm 与 Cursor。若 PATH 中的 `python` 是旧版本，脚本会优先通过 Windows `py` 启动器选择 `py -3.10` 或更高版本。

进入 `.agents` 目录，在 PowerShell 中执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
```

（若已在 `.agents` 内，直接执行第二行即可。）

脚本结束后会**清屏**并显示**分层着色**的结构化摘要；调试时可加 `-Verbose`（展开详细日志）、`-NoClearScreen`（不清屏）或 `-NoColor`（禁用着色；输出重定向时亦自动禁用）。

脚本会：

- 将 manifest 托管的 `skills/` **增量覆盖**到 `%USERPROFILE%\.cursor\skills\`（仅同名托管项，不删除用户自装 skill）
- 安装 33 个去重后的 Cursor 版 gstack 入口，并在 `%USERPROFILE%\.cursor\skills\gstack\` 首次编译共享运行时
- 从 `mcp-servers-src/` 安装本地 MCP 到 `%USERPROFILE%\.cursor\mcp-servers\`
- 写入或合并 `%USERPROFILE%\.cursor\mcp.json`（已有配置会备份为 `mcp.json.bak-时间戳`）
- **默认不安装 Rules**；结束时提醒按 [`rules/universal/AGENTS.md`](rules/universal/AGENTS.md) 各节**手动录入** Cursor Settings → Rules → **User**

完成后 **重启 Cursor**，在 **Settings → Tools & MCP** 确认服务已启用，并按终端提醒录入 User Rules。

常用参数（均在 `.agents` 目录内执行）：

```powershell
# 只装 Skills/MCP，不构建 MCP 服务
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -SkipMcpInstall

# 预览将更新的托管 Skills
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -WhatIf

# 跳过 Skills 更新
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -SkipSkillUpdate

# 不安装 gstack；或只复制 gstack 源码、暂不编译运行时
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -SkipGstackInstall
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -SkipGstackBuild

# 可选：将 rules/cursor/*.mdc 安装到指定工程的 .cursor/rules/
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -ProjectPath "D:\GeoPile"

# 调试：不清屏，末尾展开全部安装细节
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -Verbose -SkipMcpInstall

# CI/重定向：保留进度输出，摘要追加在末尾
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -NoClearScreen -SkipMcpInstall

# 禁用摘要着色（重定向到文件时亦自动禁用）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -NoColor -SkipMcpInstall
```

**Rules 说明**：

| 通道 | 方式 |
|------|------|
| **User Rules（跨项目）** | 默认：手动按 [`AGENTS.md`](rules/universal/AGENTS.md) 各 `##` 节逐条录入 Settings → User |
| **Project Rules（单工程）** | 可选：`-ProjectPath "工程根"`，安装 14 个 `.mdc` 到该工程 `.cursor/rules/` |
| **勿用** | Include third-party 整份导入 AGENTS.md；`~/.cursor/rules/`（Cursor 不加载） |

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

3. **Rules**  
   - 团队开发规范：`.agents/rules/universal/AGENTS.md`（建议写入 `CLAUDE.md` 或设为项目规则源）。

4. **项目引导**（可选）  
   - 在仓库根 `CLAUDE.md` / `AGENTS.md` 中指向 `.agents/README.md` 与上述 Rules 文件。

5. **环境变量**  
   - 见下文 [环境变量](#环境变量)；`campus-net` 凭据可放在 Claude 配置中的等价 env 或手动指定的 `CAMPNET_USER_ROOT/local.env`。

---

### OpenCode

OpenCode 各版本对 Skills / MCP 的路径可能不同，通用做法：

1. 克隆本仓库，将 **`.agents` 放在项目根目录**（或只拷贝 `skills/` + `mcp-servers-src/`）。
2. 在 OpenCode 设置中把 **Skills 目录** 指向本包的 `.agents/skills/`（或复制到 OpenCode 要求的 `skills` 路径）。
3. **Rules**：将 [`rules/universal/AGENTS.md`](rules/universal/AGENTS.md) 配置为项目规则/说明文件。
4. MCP：用 [`mcp.template.json`](mcp.template.json) 作模板，把 `command` / `args` 改为本机路径后粘贴到 OpenCode 的 MCP 配置界面。
5. 需要 Python MCP 时，在对应目录执行 `python -m venv .venv` 与 `pip install -r requirements.txt`；`campus-net` 另需 `playwright install chromium`。

具体菜单以你安装的 OpenCode 版本文档为准。

---

### Trea

Trea 使用 **`.agent`** 目录名（单数）：

1. 下载 / 克隆本仓库。  
2. 将根目录下的 **`.agents` 文件夹重命名为 `.agent`**，并放在 Trea 识别的项目根路径。  
3. Skills 即 `.agent/skills/`；团队规范即 `.agent/rules/universal/AGENTS.md`；MCP 见 [`mcp.template.json`](mcp.template.json) 与 [`mcp.md`](mcp.md)。

---

## 目录结构

```text
.agents/
├── README.md                 # 本文：平台安装、目录索引、Skills/MCP 总表
├── PORTABLE.md               # Cursor 迁移与脚本细节
├── CODEX.md                  # Codex 安装与 MCP 增量适配说明
├── ANTIGRAVITY.md            # Antigravity 安装与配置说明
├── manifest.json             # Skills / MCP 来源清单（机器可读）
├── licenses/                 # 第三方技能许可证
├── mcp.md                    # MCP 调用规范（给智能体）
├── skills.md                 # Skills 选择规则（给智能体）
├── workflows.md              # 文献检索 → 下载 → 引用 → PPT 流程
├── output-templates.md       # 候选文献池、摘要、筛选记录等模板
├── environment.md            # 环境变量、路径、维护命令
├── mcp.template.json         # MCP 配置模板（替换 {{USERPROFILE}} 后使用）
├── skills/                   # 全部 Agent Skills（每目录一个 SKILL.md）
├── host-skills/              # gstack 宿主生成入口（codex / cursor）
├── runtime/gstack/           # gstack 共享运行时源码（安装时编译）
├── rules/
│   ├── cursor/               # Cursor Rules（.mdc）→ .cursor/rules/
│   ├── codex-global/         # Codex 全局 AGENTS.md 与按需 agent-rules/
│   ├── antigravity/          # Antigravity 专有规则（AGENTS.md + agent-rules/）
│   └── universal/            # Claude Code / OpenCode / Trea（AGENTS.md）
├── mcp-servers-src/          # 需本地构建的 MCP 源码快照
│   ├── academic-research-mcp/
│   ├── zotero-mcp/
│   ├── deck-builder/
│   └── campus-net-mcp/       # 校园网馆藏（本仓库附带）
└── scripts/
    ├── setup-cursor-agents.ps1   # 仅 Cursor：写入 ~/.cursor/
    ├── setup-codex-agents.ps1    # 仅 Codex：写入 ~/.codex/
    ├── setup-antigravity-agents.ps1 # 仅 Antigravity：写入 ~/.gemini/config/plugins/agents/
    ├── gstack-install-lib.ps1       # Codex / Cursor 共用 gstack 安装与构建逻辑
    └── sync-ui-ux-skills.ps1     # 维护者：从 ui-ux-pro-max-skill 同步 UI/UX 技能族
```

| 路径 | 说明 |
|------|------|
| `skills/` | 智能体技能包；每个子文件夹含 `SKILL.md`，由运行时自动发现。 |
| `host-skills/{codex,cursor}/` | gstack 官方生成器的宿主专用入口，仅由对应安装脚本读取。 |
| `runtime/gstack/` | gstack 1.60.1.0 的裁剪运行时源码；不含 `.git`、测试、依赖与预编译大文件。 |
| `rules/cursor/` | Cursor 规则（`.mdc`）；见 [`rules/README.md`](rules/README.md)。 |
| `rules/codex-global/` | Codex 全局入口与按需规则；由 `setup-codex-agents.ps1` 安装到 `%USERPROFILE%\.codex\`。 |
| `rules/universal/` | 通用团队规范（`.md`）；非 Cursor 平台使用。 |
| `mcp-servers-src/` | MCP 服务端源码；**不含** `.venv`、`node_modules`（需安装脚本或手动构建）。 |
| `scripts/setup-cursor-agents.ps1` | **仅 Cursor**：安装 Skills + MCP 到用户目录。 |
| `scripts/setup-codex-agents.ps1` | **仅 Codex**：安装 Rules + Skills + MCP 到用户目录，增量覆盖托管项。 |
| `mcp.template.json` | 非 Cursor 平台手工配置 MCP 时的 JSON 模板。 |
| `workflows.md` | 多技能串联的标准工作流（查文献、筛文献、下全文、做 PPT）。 |
| `output-templates.md` | 统一交付格式（表格、大纲、筛选日志）。 |

工作区根目录另有 `cad-structure-layout-debug/`、`wpf-python-mvvm-builder/`、`superpowers/` 与 `gstack/` 等编辑源。gstack 先用上游生成器分别生成 Codex/Cursor 入口，再按 `manifest.json` 的去重清单发布；共享运行时以裁剪源码形式纳入。

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
| `ppt-maker` | Vue 高保真幻灯片预览 + 浏览器导出 pptx/zip；默认「做 PPT」；**grill-me 顺序定稿** + `ui-ux-pro-max`；见 `skills/ppt-maker/发布说明.md`。 |
| `academic-ppt-builder` | 学术快出：中文学术 PPT 大纲 + deck-builder / ppt-markdown 生成 pptx。 |
| **UI/UX 设计**（源自 [`ui-ux-pro-max-skill`](../ui-ux-pro-max-skill/) 汉化，经 `sync-ui-ux-skills.ps1` 同步） | |
| `ui-ux-pro-max` | React Native UI/UX BM25 检索与设计系统推荐（`search.py --design-system`）。 |
| `design` | Logo、CIP 企业识别、图标生成与检索（生成脚本需 `GEMINI_API_KEY`）。 |
| `design-system` | 设计令牌、幻灯片文案/布局/策略检索（含 Python/Node scripts）。 |
| `ui-styling` | shadcn/ui 与 Tailwind 组件与配置辅助。 |
| `brand` | 品牌指南、视觉识别与资产校验。 |
| `slides` | 融资/产品路演幻灯片结构与文案（联动 design-system scripts）。 |
| `banner-design` | 横幅尺寸与风格规范（完整生成链依赖未打包的 ai-artist 等，见 environment.md）。 |
| **CAD 工程出图**（Cursor + Codex 托管） | |
| `cad-structure-layout-debug` | 从零搭建或调试 CAD 出图组件，覆盖 DXF 排版、布局引擎、明细表锚点、预览一致性、烟测与视觉验收；编辑源在工作区根 `cad-structure-layout-debug/`，经 sync 发布到 `.agents/skills/`。 |
| **WPF + Python 工程脚手架**（Cursor + Codex 托管） | |
| `wpf-python-mvvm-builder` | 在已有 Visual Studio WPF 项目上增量补全 PythonBridge、MVVM 目录、Themes/Resources/Properties 与 memory/archive 持久化路线；编辑源在工作区根 `wpf-python-mvvm-builder/`，经 sync 发布到 `.agents/skills/`。 |
| **Superpowers 软件开发方法**（上游 `obra/superpowers` 6.1.1，MIT） | |
| `using-superpowers` | 会话入口：要求先检查并调用匹配技能，再响应或执行任务。 |
| `brainstorming` | 创意或功能开发前澄清意图、约束并形成经确认的设计。 |
| `using-git-worktrees` | 在需要隔离的功能开发或计划执行前建立或复用工作树。 |
| `writing-plans` | 将已确认的规格拆成含文件路径和验证步骤的实施计划。 |
| `executing-plans` | 按检查点批量执行既有计划。 |
| `subagent-driven-development` | 以独立实施与两阶段审查推进当前会话中的计划任务。 |
| `dispatching-parallel-agents` | 对无共享状态、无顺序依赖的任务并行分派智能体。 |
| `test-driven-development` | 在功能或缺陷实现前执行红—绿—重构循环。 |
| `systematic-debugging` | 在提出修复前完成复现、根因定位与验证。 |
| `requesting-code-review` | 在任务完成或合并前发起代码审查。 |
| `receiving-code-review` | 对审查意见做技术核验后再实施。 |
| `verification-before-completion` | 在宣称完成、修复或通过前运行并检查验证命令。 |
| `finishing-a-development-branch` | 测试通过后选择合并、PR、保留或清理分支。 |
| `writing-skills` | 用面向过程文档的测试驱动方法创建或修改技能。 |
| **gstack 去重集成**（上游 `garrytan/gstack` 1.60.1.0，MIT；仅 Codex + Cursor） | |
| `gstack-browse`、`gstack-qa`、`gstack-qa-only`、`gstack-scrape` | 浏览器自动化、站点 QA、回归证据与网页抓取。 |
| `gstack-design-html`、`gstack-design-review`、`gstack-diagram`、`gstack-make-pdf` | HTML 设计、视觉审查、图表渲染与 PDF 生成。 |
| `gstack-benchmark`、`gstack-benchmark-models`、`gstack-canary`、`gstack-health` | 性能/模型基准、发布金丝雀与健康检查。 |
| `gstack-ios-*` | iOS 清理、修复、同步、QA 与设计审查。 |
| 其余保留入口 | CSO、DevEx、发布文档、部署配置、复盘、学习、pair-agent、freeze/unfreeze 等；完整 33 项见 `manifest.json`。 |
| **工程与协作**（多源自 Matt Pocock 技能适配） | |
| `karpathy-guidelines` | Karpathy 四原则：减少 LLM 编码错误（编码前思考、简洁优先、精准修改、目标驱动执行）。 |
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

### Superpowers 集成与维护边界

- 本包集成的是上游 14 个技能目录；安装器依据 `manifest.json` 将它们作为普通托管 Skills 安装，不改写技能正文。
- Codex 使用原生技能发现机制，与上游 Codex 插件的无 Hook 方式一致。Cursor、Antigravity 与 QoderCN 侧依赖各自运行时发现 `using-superpowers` 的描述；本包不额外安装上游 Cursor Marketplace 的会话启动 Hook。
- 若某平台必须强制注入会话启动上下文，应改用该平台的上游官方 Superpowers 插件，并避免与本包重复托管同名技能。
- 更新根目录 `superpowers/` 快照后，应同步 `superpowers/skills/*`、`superpowers/LICENSE`、`manifest.json` 中的版本和三个平台托管清单，再运行技能校验与安装器 `-WhatIf` 烟测。

### gstack 集成与去重边界

- 上游 54 个 Codex/Cursor 生成入口中保留 33 个；排除的 21 个及逐项理由记录在 `manifest.json > gstackIntegration.excludedSkills`，不会再复制一套同义流程。
- 典型替代关系：`investigate` → `systematic-debugging`/`diagnose`，`review` → `requesting-code-review`，`ship` → `finishing-a-development-branch`，`spec` → `to-prd` + `to-issues`，上下文保存/恢复 → `handoff`。
- `gstack-upgrade` 被排除，运行时更新由本仓库维护；托管运行时中的上游自动更新提示已关闭。gbrain 的全局配置与同步也不纳入。
- gstack 入口含宿主路径，不能放入通用 `skills/` 后跨平台混用。目前仅 Codex、Cursor 安装脚本接入；Antigravity、QoderCN、Claude Code、OpenCode 与 Trea 保持原清单。
- 首次安装会调用本机 Bun，未安装 Bun 时通过 `npx --yes bun` 获取，并编译浏览器、设计、PDF 等运行时；同版本且二进制完整时跳过重编译。可用 `-SkipGstackInstall` 完全跳过，或用 `-SkipGstackBuild` 只复制源码。
- gstack 技能中的命令块使用 Bash；Windows 上若 `bash` 不在 PATH，应通过 `C:\Program Files\Git\bin\bash.exe` 执行。

---

## Rules 一览

团队规范来自 `自建/AI Rules.md`，已拆为两套：

| 套系 | 路径 | 平台 |
|------|------|------|
| Cursor | `rules/cursor/*.mdc` | Cursor（含 `00` 团队规范 + 文献包规则） |
| Codex | `rules/codex-global/AGENTS.md` + `rules/codex-global/agent-rules/*.md` | Codex 全局规则与按需规则 |
| Antigravity | `rules/antigravity/AGENTS.md` + `agent-rules/*.md` | Antigravity（由脚本自动聚合注入 `plugin.json`） |
| 通用 | `rules/universal/AGENTS.md` | Claude Code、OpenCode、Trea |

完整文件表见 [`rules/README.md`](rules/README.md)。

**与 Skills 的区别**：Skills 教智能体**如何执行一类任务**；Rules 是**始终或按文件生效的硬约束**。

---

## MCP 一览

| MCP 名称 | 类型 | 用途 | 前置条件 |
|----------|------|------|----------|
| `academic-research` | 本地 Python | 多源学术检索：OpenAlex、Semantic Scholar、CrossRef、PubMed、arXiv、Unpaywall 等 | Python venv；可选 `S2_API_KEY`、`OPENALEX_EMAIL` 等 |
| `zotero` | 本地 Node | 读写本地 Zotero 库、附件、集合、BibTeX | Zotero Desktop 运行；需构建 `dist/index.js` |
| `deck-builder` | 本地 Node | 结构化生成可编辑 `.pptx` | `npm install` + `npm run build` |
| `ppt-markdown` | npx 远程包 | Markdown 转 PowerPoint | Node.js；`npx -y @botrun/mcp-ppt-generator` |
| `campus-net` | 本地 Python（本仓库附带） | 学校 Profile、馆藏探测、CAS/VPN 会话、DOI 全文下载；失败写入 `manual_download_required.md` | Python venv + Playwright Chromium；Codex 下可选 `CAMPUS_USERNAME` / `CAMPUS_PASSWORD` 或 `~/.codex/campus-net/local.env` |

**常用工具（campus-net）**：`get_active_profile`、`onboard_school`、`ensure_auth`、`download_paper`、`download_papers`、`download_cnki`、`detect_network`。

源码位置：`mcp-servers-src/<名称>/`。安装后 Cursor 默认路径：`%USERPROFILE%\.cursor\mcp-servers\`；Codex 默认路径：`%USERPROFILE%\.codex\mcp-servers\`；Antigravity 默认路径：`%USERPROFILE%\.gemini\config\plugins\agents\mcp-servers\`。

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

`campus-net` 用户配置目录：Cursor 为 `~/.cursor/campus-net/`，Codex 为 `~/.codex/campus-net/`（含 `local.env`、`sessions/`、`active.json`）。

---

## 常见问题排错 (FAQ)

### pip 安装依赖时报错 `[SSL: UNEXPECTED_EOF_WHILE_READING]` 或假死

**原因**：通常是因为开启了 VPN / 网络代理（如 Clash、V2Ray 的系统代理或 TUN 模式），代理软件拦截了 Python `pip` 的 HTTPS 请求，导致证书验证失败；或者代理路由规则在处理国内镜像（如清华源）时发生中断，引发脚本假死。

**解决方法**：
1. **方案 A（最推荐）**：暂时彻底关闭代理软件，重新打开终端以清空环境变量，然后在正常的国内网络下重新运行安装脚本。
2. **方案 B（信任镜像源）**：如果必须开启代理，在手动排错时可带上 `--trusted-host` 参数跳过 SSL 验证。例如：
   ```bash
   pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
   ```
3. **方案 C（使用 HTTP 源）**：在使用一键安装脚本时，可通过参数指定非 HTTPS 的阿里源：
   ```powershell
   powershell -ExecutionPolicy Bypass -File ".\scripts\setup-antigravity-agents.ps1" -PipIndexUrl "http://mirrors.aliyun.com/pypi/simple/"
   ```

---

## 智能体阅读顺序

1. 本文（安装与总览）  
2. [`mcp.md`](mcp.md) — 调用 MCP 前  
3. [`skills.md`](skills.md) — 选择技能前  
4. [`workflows.md`](workflows.md) — 文献/PPT 类任务  
5. [`output-templates.md`](output-templates.md) — 需要统一交付格式时  
6. [`environment.md`](environment.md) — 排错与更新  
