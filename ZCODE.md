# ZCode 安装说明

本文记录 `.agents` 包面向 ZCode 的适配方式。ZCode 通过 `~/.zcode`（默认 `%USERPROFILE%\.zcode`）承载用户级技能与指令，通过 `~/.zcode/cli/config.json` 承载 MCP 注册。Cursor 见 [`PORTABLE.md`](PORTABLE.md)，Codex 见 [`CODEX.md`](CODEX.md)，Antigravity 见 [`ANTIGRAVITY.md`](ANTIGRAVITY.md)，DSH 见 [`DSH.md`](DSH.md)。

## 前置

- Windows 上已安装 ZCode；`~/.zcode` 为用户级配置根。
- Python 3.10+（脚本优先使用 Windows `py` 启动器选择 3.10+；PATH 中的旧版 `python` 会被跳过）。
- Node.js 18+ 与 npm（`zotero`、`deck-builder` 构建与运行）。
- 首次安装 MCP 需要网络：pip 默认清华源，npm 走默认源，`campus-net` 还会下载 Playwright Chromium。

## 一键安装

进入 `.agents` 目录，在 PowerShell 中执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1"
```

脚本会：

- 将 manifest 托管的 `skills/` **增量覆盖**到 `%USERPROFILE%\.zcode\skills\`（只覆盖 `zcodeInstallManifest.managedSkills` 同名项，不删除用户自装 skill）
- 对 `pathRewriteSkills` 中的技能把 Cursor 绝对路径改写为当前 ZCode 技能根（保留 BOM 与行尾）
- 将 `rules/zcode/AGENTS.md` 写入 `%USERPROFILE%\.zcode\AGENTS.md` 的托管块（保留既有用户内容并备份）
- 将 `rules/zcode/rules/*.md`（14 条）直拷到 `%USERPROFILE%\.zcode\rules\`，并创建 `%USERPROFILE%\.zcode\campus-net\`
- 从 `mcp-servers-src/` 构建 4 个本地 MCP 到 `%USERPROFILE%\.zcode\mcp-servers\`
- 将 4 个托管服务器条目**增量合并**进 `%USERPROFILE%\.zcode\cli\config.json` 的 `mcp.servers`（只写托管同名条目，保留其余所有键与用户自装服务器；写前备份、写后 JSON 校验）
- 发现旧版本遗留的退役 MCP 时先询问；默认保留，只有用户明确确认后才删除
- **不安装 gstack**（宿主支持清单仅 Codex / Cursor），也不写入任何 hooks 配置

常用参数：

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1" -WhatIf            # 预览，不写盘
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1" -SkipMcpInstall    # 只装 Rules 与 Skills
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1" -SkipSkillUpdate   # 跳过 Skills
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1" -SkipRules         # 跳过 Rules
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1" -NoPathRewrite     # 不改写技能内的 Cursor 路径
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1" -ZcodeHome "D:\tmp\zcode-home"  # 测试/多环境
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1" -UseOfficialPipIndex          # 海外网络
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1" -PipIndexUrl "https://mirrors.aliyun.com/pypi/simple/"
```

## 技能发现与优先级

ZCode 按以下顺序扫描技能目录（数字越小越优先，**同名技能先发现者加载、遮蔽后者**）：

| 优先级 | 来源 | 路径 |
|---|---|---|
| 1 | 显式配置根 | 配置中声明的技能根 |
| 2 | 用户 ZCode | `~/.zcode/skills` |
| 3 | 用户共享 | `~/.agents/skills` |
| 4 | 工作区 `.zcode` | `<repo>/.zcode/skills`（自 cwd 向上每层都算） |
| 5 | 工作区 `.agents` | `<repo>/.agents/skills` |
| 6 | 插件 | 已启用插件的技能根 |

与 DSH 相反，**用户级 `~/.zcode/skills/` 会遮蔽项目内 `.agents/skills/`**：安装本包后，同名技能从用户级副本加载。用户级副本中的 Cursor 路径已被安装器改写为 `%USERPROFILE%\.zcode\skills\`；更新 `.agents/skills/` 源后需重跑安装器同步，或临时用 `-SkipSkillUpdate` 后手动删除 `~/.zcode/skills/<name>` 让项目副本生效。

技能格式：`<skill>/SKILL.md`；frontmatter 必填 `name` 与 `description`（超过 1024 字符会被丢弃），可选 `when_to_use`；触发语应落在 `description` 前 250 字符内。frontmatter 中的 `disable-model-invocation` 是 DSH 专属键，ZCode **不识别**——带 description 的技能既可被模型按需调用，也可由用户 `/name` 显式调用。以 `.` 开头的目录（除 `.system`）与 `node_modules` 会被跳过。

## 规则

ZCode 加载：

- 用户级：`~/.zcode/AGENTS.md`（每个工作区都会先注入）
- 工作区级：自 cwd 向上解析到项目根的 `AGENTS.md`（后注入，可收窄或覆盖用户级）

本包写入 `~/.zcode/AGENTS.md` 的是薄入口：常驻硬约束 + 按需规则索引 + ZCode 工具要点。主题规则在 `~/.zcode/rules/`，由模型在对应任务前读取；ZCode 没有 Cursor/Qoder 的 trigger 机制。工作区已有的 `AGENTS.md`（如本仓库根）不受影响。

托管块边界：

```text
<!-- >>> portable-agents:zcode managed rules >>> -->
...
<!-- <<< portable-agents:zcode managed rules <<< -->
```

重复安装原位替换，块外内容与已有备份不受影响。

## MCP

注册位置：`~/.zcode/cli/config.json` 的 `mcp.servers`。注意 ZCode 的三条硬约束：

1. **schema 严格**：服务器条目只认 `type`/`command`/`args`/`cwd`/`env`/`enabled`/`timeoutMs`（stdio）等已知键，未知键导致条目被**静默丢弃**。
2. **不展开 `${...}` 模板**：配置文件中的 MCP 条目不做变量展开，路径必须写**绝对路径**（安装器在写入时解析 python venv 与 node 的绝对路径）。
3. **凭据靠环境继承**：stdio 子进程自然继承系统环境变量，因此安装器**不写** `S2_API_KEY` 等可选凭据的空占位；需要时设为 Windows 用户环境变量，或写入 `%USERPROFILE%\.zcode\campus-net\local.env`。唯一显式写入的 `env` 是 `campus-net` 的 `CAMPNET_USER_ROOT`（固定到 `%USERPROFILE%\.zcode\campus-net`）。

| 服务器 | 入口（安装器写入绝对路径） | 说明 |
|---|---|---|
| `academic-research` | `<home>\mcp-servers\academic-research-mcp\.venv\Scripts\python.exe server.py` | 多源学术检索 |
| `zotero` | `<node> <home>\mcp-servers\zotero-mcp\dist\index.js` | 需 Zotero Desktop 运行 |
| `deck-builder` | `<node> <home>\mcp-servers\deck-builder\build\index.js` | 生成可编辑 pptx |
| `campus-net` | `<home>\mcp-servers\campus-net-mcp\.venv\Scripts\python.exe server.py` | `CAMPNET_USER_ROOT=<home>\campus-net` |

工具名固定为 `mcp__<serverName>__<toolName>`，例如 `mcp__academic-research__smart_search`。用户级与工作区同名服务器时**用户级覆盖工作区**；所有作用域的 MCP 在会话启动时自动连接。验证方式：重启会话后 **Settings → MCP** 显示 4 个服务为 connected，工具列表出现 `mcp__academic-research__*` 等。

## 与其它宿主的差异

| 能力 | Cursor / Codex | ZCode |
|---|---|---|
| 规则注入 | Cursor User Rules / Codex `AGENTS.md` + 按需 | `~/.zcode/AGENTS.md` 托管块 + `~/.zcode/rules/` 按需读取 |
| 技能优先级 | 仅用户级安装 | 用户级 `~/.zcode/skills/` **遮蔽**项目内 `.agents/skills/` |
| 技能调用 | `@name` / 描述触发 | `Skill` 工具或 `/name`；无 `disable-model-invocation` 概念 |
| Hooks | Cursor hooks / Claude Code hooks | 支持（7 种事件）但**本包不安装**；由权限模式与规则约束 |
| 浏览器 | 可由 MCP 或扩展提供 | 由插件提供（如 browser-use）；是否可用以工具列表为准 |
| gstack | Codex / Cursor 专用入口 | **不安装** |
| 子代理 | 视宿主而定 | `Agent` 工具分派；子代理不能向用户提问，可用 `SendMessage` 续作 |
| MCP 凭据 | `${env:VAR}` 等模板 | **不展开模板**；绝对路径 + 系统环境变量继承 |

## 排错

1. 新会话看不到技能：确认技能目录在 `~/.zcode/skills/<name>/SKILL.md`，`name` 与目录同名且 frontmatter `name`/`description` 齐全；**Settings → Skills** 与 `/` 菜单可查。若本项目内 `.agents/skills/` 的改动未生效，多半是被用户级同名副本遮蔽——重跑安装器同步。
2. MCP 工具未出现：检查 `~/.zcode/cli/config.json` 是否为合法 JSON、`mcp.servers` 是否含 4 个托管条目；条目含未知键会被静默丢弃。修改后重启会话，再看 **Settings → MCP** 的内联错误。
3. Python MCP 失败：进入对应目录后运行 `& ".\.venv\Scripts\python.exe" -c "import server; print('ok')"`（`academic-research` 的 `scholarly` 需要 `bibtexparser<2`，已写入随包 `requirements.txt`）。
4. Node MCP 失败：确认安装器写入的 node 绝对路径仍有效（升级 Node 后重跑安装器刷新）；`zotero` 需 Zotero Desktop 运行。
5. `campus-net` 凭据：设置 `CAMPUS_USERNAME` / `CAMPUS_PASSWORD` 系统环境变量，或写入 `%USERPROFILE%\.zcode\campus-net\local.env`；不要在对话中回显明文。
6. 启动超时：`failed ... timed out after 30000ms` 时可为该条目补 `"timeoutMs": 60000`。
7. 退役 MCP：`manifest.json > retiredMcpServers` 中的条目默认保留；重跑安装器时按提示确认删除。

## 卸载与回滚

- `~/.zcode/AGENTS.md` 与 `~/.zcode/cli/config.json` 写入前均有 `.bak-<时间戳>` 备份；把备份覆盖回原文件即可回滚。
- 删除 `~/.zcode/skills/<name>`、`~/.zcode/rules/<rule>`、`~/.zcode/mcp-servers/<name>` 可分别移除托管内容；用户自装内容不受影响。
- 只移除托管规则块：删除 `~/.zcode/AGENTS.md` 中的 `portable-agents:zcode managed rules` 标记段；只移除 MCP：在 `mcp.servers` 中删除 4 个托管同名条目。
- 本脚本**不**执行任何 git 操作。

## 验证清单

- [ ] `.agents\tests\zcode-adapter.Tests.ps1` 通过
- [ ] `.agents\tests\dsh-adapter.Tests.ps1` 等既有测试不受影响
- [ ] `-WhatIf` 不产生文件
- [ ] `%USERPROFILE%\.zcode\skills` 含 manifest 托管技能
- [ ] `%USERPROFILE%\.zcode\AGENTS.md` 含托管块；`%USERPROFILE%\.zcode\rules` 含 14 条规则
- [ ] `%USERPROFILE%\.zcode\cli\config.json` 可被 `ConvertFrom-Json` 解析，`mcp.servers` 恰含 4 个托管条目，其余键（如 `plugins`）原样保留
- [ ] 新会话出现 `design`、`design-system`、`brand`、`banner-design`、`slides`、`ui-styling`
- [ ] 新会话出现 `mcp__academic-research__*` 等工具
