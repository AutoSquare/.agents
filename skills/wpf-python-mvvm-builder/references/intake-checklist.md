# Intake 问卷（顺序 grill，每轮 1 题）

Agent 须取得用户显式选择后再 scaffold。**禁止**未答完就假设默认。

## 宿主提问规则

- Cursor 等支持结构化提问的宿主：使用宿主结构化提问能力，每轮只问 1 个关键决策。
- Codex 或无专用提问控件的宿主：使用 Markdown 单题选票，列出互斥选项，发出后停止等待用户回复。
- 无论宿主如何，收答后都要复述下方表格，再运行 `--dry-run`；未复述前不运行 `--apply`。

## 题目顺序

| # | 问题 | 校验 |
|---|------|------|
| 1 | 目标 WPF 项目路径（含 `.csproj` 且 `UseWPF=true`） | 无则提示先去 Visual Studio 创建 WPF 空模板 |
| 2 | 英文项目简写 `{Abbr}`（2–16 字符，字母数字） | 中文项目名须给 2–3 个缩写选项 |
| 3 | **持久化路线**：`memory`（记忆型）还是 `archive`（工程归档型）？ | 见 [persistence-modes.md](persistence-modes.md)；**用户不确定时默认 `memory`，须在复述表格中写明** |
| 4a | 若 `archive`：工程文件后缀 `{Ext}` | 须以 `.` 开头 |
| 4a+ | 若 `archive`：**是否注册文件关联 / 双击打开**？ | **默认是**（HKCU + Startup 传参） |
| 4b | 若 `memory`：`AppId`（AppData 子目录，ASCII） | 通常与 RootNamespace 相同 |
| 5 | 软件中文显示名（仅 UI/About） | 不得用于路径或文件名 |
| 6 | 是否已是 MVVM？ | 否 → 问是否重构为 View/ViewModel/Services/Model |
| 7 | Python 环境 | conda / venv / auto-venv |
| 8 | 确认 `{Abbr}Py`、`{Abbr}Env` 目录名 | 路径与文件名不得含中文 |
| 9 | 若 `memory`：**是否记忆 UI 状态**（状态栏文案 + 窗口布局）？ | **默认是**（模板已接线）；否须说明原因并在开发说明记录 |
| P4 | 若已 scaffold 且要换路线 | 是否 `migrate_persistence_mode.py` + `--import-last-snapshot`？ |

## 收答后复述表格

| 项 | 用户选择 |
|----|----------|
| project-dir | … |
| persistence | memory / archive |
| Abbr | … |
| Ext 或 AppId | … |
| display-name | … |
| mvvm-refactor | … |
| python-env | … |
| ui-state-memory | 是 / 否（memory 默认 **是**：statusText + WindowPlacement） |
| file-association | 是 / 否（archive 默认 **是**：双击 `{Ext}` 打开） |

## 调试夹具（AgentStatistics）

- memory（Phase B，冻结）：`--persistence memory --app-id AgentStatistics --include-form-demo`
- archive（Phase C，补充）：`--persistence archive --ext .ast --include-form-demo` 或 `migrate_persistence_mode.py`
- memory 验收前：`reset_agent_statistics_fixture.py --apply`
- archive 验收：`run_agent_statistics_archive_e2e.py`（**勿**对 archive 夹具 reset 回 memory）
