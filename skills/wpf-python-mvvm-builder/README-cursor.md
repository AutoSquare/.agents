# WPF + Python MVVM Builder — Cursor 使用说明

## 安装

在 `.agents` 目录执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
```

安装后重启 Cursor。Skill 位于：

```text
%USERPROFILE%\.cursor\skills\wpf-python-mvvm-builder\
```

在对话中使用 `@wpf-python-mvvm-builder`，或让 Agent 按 description 自动选用。

## 持久化路线

- **memory**：AppData 记忆快照，无工程文件
- **archive**：GeoPile 式 `{Ext}` ZIP 工程包；Ctrl+S；双击 `{Ext}` 打开（HKCU 关联）

详见 [references/persistence-modes.md](references/persistence-modes.md)、[references/persistence-wiring.md](references/persistence-wiring.md)（中文接线手册）。

## 使用边界

- 只能在已有 Visual Studio WPF 空项目上增量补全；不要从零创建 WPF 项目。
- 开工前先按 [references/intake-checklist.md](references/intake-checklist.md) 完成 intake，取得用户显式选择。
- 涉及旧 AppData 缓存时，先运行 `inspect_appdata_cache.py --check`；需要迁移或删除时必须先问用户。
- 先 `--dry-run`，确认文件计划后再 `--apply`。

## Cursor 提问方式

| 场景 | Cursor 做法 |
|------|-------------|
| 有 `AskQuestion` | 每轮只问一个关键决策 |
| 工具不可用 | 用 Markdown 单题选票列出互斥选项并停止等待 |
| 用户未选择 | 不运行 `--apply`、`--migrate` 或 `--purge` |

## 常用流程

```powershell
$skill = "$env:USERPROFILE\.cursor\skills\wpf-python-mvvm-builder"

py -3 "$skill\scripts\audit_project.py" --project-dir "<path>" --abbr "<Abbr>"

# 先预览
py -3 "$skill\scripts\scaffold_dual_stack.py" --project-dir "<path>" --abbr "<Abbr>" --persistence memory --app-id "<AppId>" --dry-run

# 确认后应用
py -3 "$skill\scripts\scaffold_dual_stack.py" --project-dir "<path>" --abbr "<Abbr>" --persistence memory --app-id "<AppId>" --apply

# 验证
py -3 "$skill\scripts\smoke_bridge.py" --project-dir "<path>" --abbr "<Abbr>"
py -3 "$skill\scripts\audit_project.py" --project-dir "<path>" --abbr "<Abbr>"
dotnet build "<path>/<Project>.csproj"
```

archive 路线把 `--persistence memory --app-id "<AppId>"` 替换为：

```powershell
--persistence archive --ext "<Ext>"
```

## 完整夹具 E2E

AgentStatistics Phase B/C 冻结命令块见 [SKILL.md](SKILL.md)（维护者 / 工作区夹具路径，非日常用户必跑项）。

## 维护者工作流

编辑源在工作区根目录 `wpf-python-mvvm-builder/`（非 `.agents/skills/` 手改）：

```powershell
# 1. 编辑 wpf-python-mvvm-builder/ 下的 SKILL.md、references、scripts 等
# 2. 同步到 .agents 发布副本
powershell -ExecutionPolicy Bypass -File "wpf-python-mvvm-builder\scripts\sync-to-agents.ps1"

# 3. 安装到 Cursor
cd .agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
```

Codex 侧安装与说明见 [README-codex.md](README-codex.md) 与 `.agents/CODEX.md`（本文件不修改 Codex 文档）。
