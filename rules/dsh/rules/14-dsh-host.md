# DSH 宿主适配

## 触发条件

在 DeepSeek Harness（DSH）会话中执行任何任务前读取；需要确认工具名、模式、审批/沙箱行为、MCP 调用或子代理边界时复读本节。

## 工具映射

技能里的动作在 DSH 中对应：

| 动作 | DSH 工具/机制 |
|------|----------------|
| 建/更新待办 | `todo_write`（每个具体步骤一条，保持更新） |
| 读 / 写 / 改文件 | `read`、`write`、`edit`（覆盖前先读，优先 `edit`） |
| 查找文件/内容 | `glob`、`grep` |
| 执行命令 | `pwsh`（带 `workdir`）；长任务 `run_in_background` + `job_output`/`job_kill` |
| 分派子代理 | `subagent`（全新上下文、自包含提示）或 `subagent_fork`（继承本会话） |
| 继续 / 停止子代理 | `send_message`、`list_agents`、`interrupt_agent` |
| 向用户提问 | `ask_user_question`（结构化选项；子代理不能调用） |
| 加载技能 | `skill` 工具按精确名称加载；用户可用 `/<name>` 显式调用用户可调用技能 |
| 交付文件 | `present`（传入已存在的成品路径） |
| 网页检索 | `web_search`、`web_fetch`；**没有**浏览器自动化工具 |
| 计划模式 | 只读探索，最后用 `exit_plan_mode` 提交计划，批准后才实施 |
| 长目标 | `create_goal` / `get_goal` / `update_goal` |
| 大规模扇出 | `workflow`（仅用户明确要求工作流或大规模并行时） |

## 模式与审批

- **Plan 模式**：不能写文件、改配置、提交；计划未经 `exit_plan_mode` 批准不得实施。用户口头同意不等于批准。
- **审批策略**：`never` 时需审批的操作会被自动拒绝；不要请求沙箱提权，也不要换路径重试同一操作。报告被拒的具体命令与路径。
- **文件沙箱**：`read-only` 禁止写入；`workspace-write` 仅允许写工作区及临时区；`danger-full-access` 不受限。拒绝是策略结果，不是命令失败。

## 子代理边界

- `subagent` 不继承本会话上下文，提示必须自包含；`subagent_fork` 继承已完成对话，适合续作与审查。
- 运行中的子代理**不能**调用 `ask_user_question`（`DELEGATED_CALLER`）；待决问题放进子代理最终结果，由主代理询问。
- 记录所有后台 job id；结束前收集仍有用的输出，终止不再需要的 job。

## MCP

- 工具名为 `mcp__<serverName>__<toolName>`；只使用工具列表中实际出现的名称。
- profile 的 `cordis.patch.yml` 注册本地 MCP；stdio 子进程会清洗匹配 `/KEY|PASSWORD|SECRET|TOKEN/i` 的变量，凭据必须在条目 `env` 中显式传入。
- `campus-net` 的用户根默认写死为 `~/.codex/campus-net`，DSH 必须用 `CAMPNET_USER_ROOT` 指向 `$DSH_HOME/campus-net`。
- 调用下载类工具前先 `get_active_profile`；凭据只从环境变量或 `$DSH_HOME/campus-net/local.env` 读取，不回显明文。

## 技能资源

- 技能加载结果会给出资源基目录；正文中的相对脚本路径按该目录解析。
- 若正文硬编码 `%USERPROFILE%\.cursor\skills\` 等其它宿主路径且该路径不存在，改用 `%USERPROFILE%\.dsh\skills\`（DSH 用户级安装根）。
- `disable-model-invocation: true` 的技能不在模型目录中，只能由用户 `/name` 触发，不要用 `skill` 工具猜名加载。

## 不可用的宿主能力

- **无 hooks**：不要创建 `.claude/settings.json`、`.cursor/hooks.json` 等钩子；危险操作由审批/沙箱与 `09-git-commit-message.md` 约束。
- **无浏览器工具**：需要浏览器验收的任务（如 ppt-maker）由用户打开 URL 或由用户在浏览器导出；不得声称已截图验收。
- **无 gstack 宿主入口**：本包不为 DSH 安装 gstack。
