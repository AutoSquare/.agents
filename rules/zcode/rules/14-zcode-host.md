# ZCode 宿主适配

## 触发条件

在 ZCode 会话中执行任何任务前读取；需要确认工具名、技能发现、计划模式、MCP 调用或子代理边界时复读本节。

## 工具映射

技能里的动作在 ZCode 中对应：

| 动作 | ZCode 工具/机制 |
|------|----------------|
| 建/更新待办 | `TodoWrite`（保持一条进行中，完成后及时勾选） |
| 读 / 写 / 改文件 | `Read`、`Write`、`Edit`（覆盖前先读，优先 `Edit` 做精确替换） |
| 查找文件/内容 | `Glob`、`Grep` |
| 执行命令 | `Bash`（Windows 为 Git Bash；路径含空格或中文时加引号）；长任务用 `run_in_background` |
| 分派子代理 | `Agent`（子代理类型按任务选择；独立任务并行分派） |
| 续作 / 停止子代理 | `SendMessage`（携 agentId 续作）；后台任务经 `TaskOutput`/`TaskStop` 管理 |
| 向用户提问 | `AskUserQuestion`（结构化选项；子代理不能调用） |
| 加载技能 | `Skill` 工具按精确名称加载；用户可用 `/name` 显式调用 |
| 网页检索 | `WebSearch`、`WebFetch`；浏览器自动化由插件（如 browser-use）提供，是否可用以当前工具列表为准 |
| 计划模式 | `EnterPlanMode` 只读探索，`ExitPlanMode` 提交计划，批准后才实施 |
| 持久记忆 | 记忆文件位于 `~/.zcode/cli/memories/`；仅记录不可从代码库推导的事实 |

## 模式与审批

- **Plan 模式**：只读探索，不写文件、不改配置、不提交；计划未经 `ExitPlanMode` 批准不得实施，用户口头同意不等于批准。
- **权限模式**：工具调用被拒绝时不要原样重试；向用户报告被拒的具体操作与路径，调整方式后再试。
- **危险命令**：破坏性操作（删除、覆盖、外发）先确认；不得声称未实际运行的验证已通过。

## 子代理边界

- `Agent` 子代理不继承主会话上下文，提示必须自包含、写明交付物；其最终报告不会自动展示给用户，由主代理转述要点。
- 运行中的子代理**不能**调用 `AskUserQuestion`；待决问题放进子代理最终结果，由主代理询问用户。
- 已完成的子代理可用 `SendMessage` 续作以保留其上下文；并行分派仅用于无共享状态、无顺序依赖的任务。

## MCP

- 工具名为 `mcp__<serverName>__<toolName>`；只使用工具列表中实际出现的名称，不要臆测。
- 注册位置：`~/.zcode/cli/config.json` 的 `mcp.servers`（schema 严格，未知键导致条目被丢弃；不展开 `${...}` 模板，路径必须写绝对路径）。
- `campus-net` 的用户根通过 `CAMPNET_USER_ROOT` 固定为 `~/.zcode/campus-net`。
- 调用下载类工具前先 `get_active_profile`；凭据只从系统环境变量或 `~/.zcode/campus-net/local.env` 读取，不回显明文。

## 技能资源

- 技能加载结果会给出资源基目录；正文中的相对脚本路径按该目录解析。
- 若正文硬编码 `%USERPROFILE%\.cursor\skills\` 等其它宿主路径且该路径不存在，改用 `%USERPROFILE%\.zcode\skills\`（ZCode 用户级安装根）。
- 用户级 `~/.zcode/skills/` 的同名技能**优先于**项目内 `.agents/skills/`（用户级遮蔽工作区）；更新技能源后重跑 `setup-zcode-agents.ps1` 同步。

## 本包不为 ZCode 安装的能力

- **无 hooks**：本包不写任何 hooks 配置（配置文件 hooks 需 `hooks.enabled: true`，属用户自管范围）；git 安全由 `09-git-commit-message.md` 与确认流程约束。
- **无 gstack 宿主入口**：gstack 仅支持 Codex / Cursor，本包不为 ZCode 安装。
