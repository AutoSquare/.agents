# 智能体协作入口（<配置包根目录> 包）

## 触发条件

当前项目含智能体配置包（识别特征：目录含 `manifest.json` 与 `skills/`；常见目录名 `AI规则仓库/`、`.agents/`、`.agent/`，名称不限），或任务涉及 MCP、skills、文献工作流、PPT 工作流时读取。

## 执行要求

本仓库（或已安装本配置包的项目）中，智能体应：

1. 先读 `<配置包根目录>/README.md`（安装方式、Skills/MCP 总表）。
2. 团队工程规范见本目录规则 `01`-`08`；DSH 宿主差异见 `<配置包根目录>/DSH.md` 与 `14-dsh-host.md`。
3. 涉及外部工具时读 `<配置包根目录>/mcp.md`；选技能时读 `<配置包根目录>/skills.md`。
4. 文献检索、筛选、引用、PPT 任务读 `<配置包根目录>/workflows.md`。
5. DSH 用户级技能位于 `$DSH_HOME/skills/`（默认 `~/.dsh/skills/`），规则位于 `$DSH_HOME/rules/`；项目内 `.agents/skills/` 优先。
6. 执行 `campus-net` 的下载类工具前调用 `get_active_profile`；失败时向用户说明 `manual_download_required.md` 路径。

不要跳过上述文档直接臆测 MCP 工具名或学校 Profile。