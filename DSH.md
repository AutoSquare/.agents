# DeepSeek Harness（DSH）安装说明

本文记录 `.agents` 包面向 DeepSeek Harness（DSH）的适配方式。本包按 DSH `0.2.1-rc.3` 桌面端验证。Cursor 见 [`PORTABLE.md`](PORTABLE.md)，Codex 见 [`CODEX.md`](CODEX.md)，Antigravity 见 [`ANTIGRAVITY.md`](ANTIGRAVITY.md)。

## 前置

- Windows 上已安装 DSH 桌面端；`$DSH_HOME` 默认 `%USERPROFILE%\.dsh`，profile 默认 `desktop`。
- Python 3.10+（脚本优先使用 Windows `py` 启动器选择 3.10+；PATH 中的旧版 `python` 会被跳过）。
- Node.js 18+ 与 npm（`zotero`、`deck-builder` 构建与运行）。
- 首次安装 MCP 需要网络：pip 默认清华源，npm 走默认源，`campus-net` 还会下载 Playwright Chromium。

## 一键安装

进入 `.agents` 目录，在 PowerShell 中执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1"
```

脚本会：

- 将 manifest 托管的 `skills/` **增量覆盖**到 `%USERPROFILE%\.dsh\skills\`（只覆盖 `dshInstallManifest.managedSkills` 同名项，不删除用户自装 skill）
- 把 `pathRewriteSkills` 中技能的 Cursor 绝对路径改写为当前 DSH 技能根（保留 BOM 与行尾）
- 将 `rules/dsh/AGENTS.md` 写入 `%USERPROFILE%\.dsh\AGENTS.md` 的托管块（保留既有用户内容并备份）
- 将 `rules/dsh/rules/*.md` 直拷到 `%USERPROFILE%\.dsh\rules\`
- 从 `mcp-servers-src/` 构建 4 个本地 MCP 到 `%USERPROFILE%\.dsh\mcp-servers\`，并创建 `%USERPROFILE%\.dsh\campus-net\`
- 把 4 个 `@deepseek-ai/dsh-mcp-client` 条目写入 `%USERPROFILE%\.dsh\profiles\desktop\cordis.patch.yml` 的托管标记块；写前备份，写后用 PyYAML 校验
- 发现旧版本遗留的退役 MCP 时先询问；默认保留，只有用户明确确认后才删除

常用参数：

```powershell
# 预览将更新的托管项，不写入磁盘
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1" -WhatIf

# 只安装 Rules 与 Skills，不构建或注册 MCP
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1" -SkipMcpInstall

# 跳过 Skills 或 Rules
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1" -SkipSkillUpdate
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1" -SkipRules

# 不改写技能内的 Cursor 路径
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1" -NoPathRewrite

# 指定 DSH home / profile（测试或多环境）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1" -DshHome "D:\tmp\dsh-home" -Profile "web"

# 海外网络：官方 PyPI 或自定义镜像
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1" -UseOfficialPipIndex
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-dsh-agents.ps1" -PipIndexUrl "https://mirrors.aliyun.com/pypi/simple/"
```

## 技能发现与优先级

DSH 从文件系统按目录一层发现技能，优先级如下（数字越小越优先）：

| 优先级 | 来源 | 路径 |
|---|---|---|
| 100 | 项目 DSH | `<projectRoot>/.dsh/skills` |
| 200 | 项目 `.agents` | `<projectRoot>/.agents/skills` |
| 300 | 自定义 | `customSkillDirs` |
| 400 | 用户 DSH | `$DSH_HOME/skills` |
| 500 | 共享 agents | `<agentsHome>/skills`（`$DSH_AGENTS_HOME` 或 `~/.agents`） |

`projectRoot` 取最近含 `.git` 的祖先；没有时用当前工作目录。**项目内 `.agents/skills` 优先于本脚本安装的用户级副本**，因此在本仓库中运行 DSH 无需另行安装技能。

技能格式：`<name>/SKILL.md`；frontmatter 必填 `name`（`^[a-z0-9]+(?:-[a-z0-9]+)*$`）与 `description`，可选 `disable-model-invocation`、`user-invocable`、`metadata`、`whenToUse`。目录描述上限 500 字符。`disable-model-invocation: true` 的技能不出现在模型目录中，只能由用户 `/name` 调用（本包中为 `cad-structure-layout-debug`、`setup-matt-pocock-skills`、`wpf-python-mvvm-builder`、`zoom-out`）。

技能加载结果会给出资源基目录；正文中硬编码 `%USERPROFILE%\.cursor\skills\` 的命令，在 DSH 副本中由安装器改写为 `%USERPROFILE%\.dsh\skills\`。项目内 `.agents/skills` 未被改写时，若该 Cursor 路径不存在，按全局规则改用 `.dsh` 路径。


安装副本中的历史「Cursor」字样（如「运行时（Cursor）」）不会被删除，但其中的路径已改写为 DSH 技能根；以实际路径为准。

## 规则

DSH 加载：

- 用户级：`$DSH_HOME/AGENTS.md`，然后 `<agentsHome>/AGENTS.md`
- 项目级：项目根到 cwd 每层的 `AGENTS.md` / `CLAUDE.md`（含 `*.local.md`），受 64 KiB 预算约束；不解析 `@path` 导入

本包写入 `$DSH_HOME/AGENTS.md` 的是薄入口：常驻硬约束 + 按需规则索引 + DSH 工具要点。主题规则在 `$DSH_HOME/rules/`，由模型在对应任务前读取；DSH 没有 Qoder/Cursor 的 trigger 机制。

托管块边界：

```text
<!-- >>> portable-agents:dsh managed rules >>> -->
...
<!-- <<< portable-agents:dsh managed rules <<< -->
```

重复安装原位替换，块外内容与已有备份不受影响。

## MCP

注册位置：`$DSH_HOME/profiles/<profile>/cordis.patch.yml`（默认 `desktop`）。每个服务器一条 `@deepseek-ai/dsh-mcp-client` 行，托管块边界：

```text
# >>> portable-agents:dsh mcp managed >>>
...
# <<< portable-agents:dsh mcp managed <<<
```

工具名固定为 `mcp__<serverName>__<toolName>`，例如 `mcp__academic-research__smart_search`、`mcp__campus-net__download_paper`。DSH 会清洗 stdio 子进程中匹配 `/KEY|PASSWORD|SECRET|TOKEN/i` 的变量，因此模板显式传入 `S2_API_KEY`、`NCBI_API_KEY`、`CAMPUS_PASSWORD`、`PADDLEOCR_TOKEN` 等；未设置的环境变量按空字符串传入。

新增条目必须放在 `- insert:` 列表中；裸 `- id: ...` 会被 loader 当作覆盖目标并报 `patch: entry "..." not found`，新服务器不会加载。模板与安装器已按 `insert` 形式生成。

| 服务器 | 入口 | 说明 |
|---|---|---|
| `academic-research` | `.venv\Scripts\python.exe server.py` | 多源学术检索 |
| `zotero` | `<node> dist\index.js` | 需 Zotero Desktop 运行 |
| `deck-builder` | `<node> build\index.js` | 生成可编辑 pptx |
| `campus-net` | `.venv\Scripts\python.exe server.py` | `CAMPNET_USER_ROOT=$DSH_HOME/campus-net` |

`campus-net` 源码默认用户根是 `~/.codex/campus-net`；本包通过 `CAMPNET_USER_ROOT` 固定到 DSH 目录，避免与 Codex 配置混用。

DSH 的 profile patch 受 HMR 监视；写入后通常无需重启，若新会话未见工具则重启桌面端。验证方式：新会话工具列表出现 `mcp__academic-research__*` 等；否则检查 DSH 的 Plugins 页面与 patch 文件。

## 与其它宿主的差异

| 能力 | Cursor / Codex | DSH |
|---|---|---|
| 规则注入 | Cursor User Rules / Codex `AGENTS.md` + 按需 | `$DSH_HOME/AGENTS.md` + `$DSH_HOME/rules/` 按需 |
| 技能调用 | `@name` / 描述触发 | `skill` 工具或 `/name`；`disable-model-invocation` 仅 `/name` |
| Hooks | Cursor hooks / Claude Code hooks | **无**；由审批、沙箱与规则约束 |
| 浏览器 | 可由 MCP 或扩展提供 | **无内置浏览器工具**；需要用户打开 URL 或自行导出 |
| gstack | Codex / Cursor 专用入口 | **不安装** |
| 子代理提问 | 视宿主而定 | 子代理不能调用 `ask_user_question`，待决问题回传主代理 |
| MCP 凭据 | `${env:VAR}` 等模板 | `!!js process.env.VAR || ''` 显式传入 |

## 排错

1. 新会话看不到技能：确认技能目录在 `$DSH_HOME/skills/<name>/SKILL.md`，`name` 与目录同名且为 kebab-case，`description` 非空。
2. 工具未出现：检查 `cordis.patch.yml` 托管块是否完整、YAML 是否合法；重启 DSH 后再看 Plugins 页面。
3. Python MCP 失败：进入对应目录后运行 `& ".\.venv\Scripts\python.exe" -c "import server; print('ok')"`（`academic-research` 的 `scholarly` 需要 `bibtexparser<2`，已写入随包 `requirements.txt`）。
4. Node MCP 失败：确认 `node -v` 可用（本包在 patch 中写入 node 绝对路径）；`zotero` 需 Zotero Desktop 运行。
5. `campus-net` 凭据：设置 `CAMPUS_USERNAME` / `CAMPUS_PASSWORD` 环境变量，或写入 `%USERPROFILE%\.dsh\campus-net\local.env`；不要在对话中回显明文。
6. 路径报错：确认技能内命令使用的是 `%USERPROFILE%\.dsh\skills\`；重新运行安装器可刷新改写。
7. 退役 MCP：`manifest.json > retiredMcpServers` 中的条目默认保留；重跑安装器时按提示确认删除。

## 卸载与回滚

- `$DSH_HOME/AGENTS.md` 与 profile patch 写入前均有 `.bak-<时间戳>` 备份；把备份覆盖回原文件即可回滚。
- 删除 `$DSH_HOME/skills/<name>`、`$DSH_HOME/rules/<rule>`、`$DSH_HOME/mcp-servers/<name>` 可分别移除托管内容；用户自装内容不受影响。
- 只移除托管块：删除 `AGENTS.md` 中的 `portable-agents:dsh managed rules` 标记段，或 patch 中的 `portable-agents:dsh mcp managed` 标记段。
- 本脚本**不**执行任何 git 操作。

## 验证清单

- [ ] `.agents\tests\dsh-adapter.Tests.ps1` 通过
- [ ] `.agents\tests\retired-mcp-cleanup.Tests.ps1` 通过
- [ ] `-WhatIf` 不产生文件
- [ ] `%USERPROFILE%\.dsh\skills` 含 manifest 托管技能
- [ ] `%USERPROFILE%\.dsh\AGENTS.md` 含托管块；`%USERPROFILE%\.dsh\rules` 含 14 条规则
- [ ] `cordis.patch.yml` 可被 PyYAML 解析，含 4 个 `mcp-*` 条目
- [ ] 新会话出现 `design`、`design-system`、`brand`、`banner-design`、`slides`、`ui-styling`
- [ ] 新会话出现 `mcp__academic-research__*` 等工具
