---
name: wpf-python-mvvm-builder
description: 在已有 VS WPF 项目上增量补全双栈 MVVM（Themes/Resources/Properties、{Abbr}Py/Env、PythonBridge）。支持 memory（AppData 记忆快照 + UI 状态）与 archive（GeoPile 式 ZIP 工程包）两路线，含 migrate 重构。用于 wpf-python-mvvm-builder、WPF+Python 脚手架。
disable-model-invocation: true
---

# WPF + Python MVVM Builder

Distilled from GeoPile. **Do not** scaffold WPF from zero — create an empty WPF project in Visual Studio first.

## Host Compatibility

- Codex: install or copy this folder to `$CODEX_HOME/skills/wpf-python-mvvm-builder/`; Codex-only display metadata lives in `agents/openai.yaml`. See [README-codex.md](README-codex.md).
- Cursor: managed by `.agents/scripts/setup-cursor-agents.ps1` (`installManifest.managedSkills`); after install use `%USERPROFILE%\.cursor\skills\wpf-python-mvvm-builder\` or `@wpf-python-mvvm-builder`. See [README-cursor.md](README-cursor.md). Cursor-facing docs stay separate so Codex edits do not change Cursor behavior.
- Intake questions are host-neutral: use the host's structured question tool when available; otherwise ask one Markdown ballot question and stop until the user answers.
- Keep the normal execution order: intake first, then audit, scaffold with `--dry-run`, apply only after review, and verify with the smoke/audit/build commands.

## Cursor Usage

- Install: run `setup-cursor-agents.ps1` from `.agents`, then restart Cursor.
- Path: `%USERPROFILE%\.cursor\skills\wpf-python-mvvm-builder\`
- Intake: prefer `AskQuestion` with one question per round; fall back to a single Markdown ballot and stop until the user answers.
- Full install, verification, and maintainer sync: [README-cursor.md](README-cursor.md).

## Persistence modes

| Mode | Use when |
|------|----------|
| `memory` | Runtime app like SpectLeakage: no project file; `session_snapshot.json` (tables + `uiState.statusText`) + `user_settings.json` (WindowPlacement) in AppData |
| `archive` | GeoPile-like: ZIP `{Ext}` project with 数据表/材料库; WindowPlacement in `user_settings.json` |

See [references/persistence-modes.md](references/persistence-modes.md), [references/ui-state-contract.md](references/ui-state-contract.md), [references/persistence-wiring.md](references/persistence-wiring.md) (中文接线手册).

## Workflow

### Phase 0 — Intake

[references/intake-checklist.md](references/intake-checklist.md) — include **`memory|archive`** and **UI state memory** (default yes for memory).

### Phase 1 — Audit

```powershell
py -3 scripts/audit_project.py --project-dir "<path>" --abbr "<Abbr>"
```

### Phase 2 — Scaffold

```powershell
# archive
py -3 scripts/scaffold_dual_stack.py --project-dir "<path>" --abbr "<Abbr>" --persistence archive --ext "<Ext>" --root-namespace "<Ns>" --display-name "<名>" --dry-run
py -3 scripts/scaffold_dual_stack.py ... --apply

# memory
py -3 scripts/scaffold_dual_stack.py ... --persistence memory --app-id "<AppId>" --apply
```

Scaffolds: MVVM + Python + **Themes/Resources/Properties** + App.xaml DefaultTheme merge + **持久化运行期接线**（memory 快照 + uiState/WindowPlacement / archive 文件菜单）。

**`--apply` 默认自动执行 `setup_python_env.py`** 创建 `{Abbr}Env` 可移植 Python 环境；跳过请加 `--skip-python-env`。

`{Abbr}Env` 是发布运行时目录，必须是可移植 Python 环境，不得是 venv；目录内不能出现 `pyvenv.cfg` 或开发机绝对路径。

### Phase 2b — Migrate (optional)

```powershell
py -3 scripts/migrate_persistence_mode.py --project-dir "<path>" --abbr "<Abbr>" --from memory --to archive --import-last-snapshot --dry-run
py -3 scripts/migrate_persistence_mode.py ... --apply
```

### Phase 3 — Python env

```powershell
py -3 scripts/setup_python_env.py --project-dir "<path>" --abbr "<Abbr>"
```

### Phase 4 — Persistence wiring (included in scaffold)

| Mode | User-visible behavior |
|------|----------------------|
| `memory` | Startup restores tables + **status bar text** from snapshot; **window layout** from `user_settings.json` on `Loaded`; calc/exit writes snapshot with `uiState.statusText`; **no** project file menu |
| `archive` | File → Open/Save/Save As `{Ext}`；**Ctrl+S**；双击 `{Ext}` 启动并打开；HKCU 文件关联；脏且已有路径时关窗自动 Save；窗口布局同 memory |

See [references/persistence-wiring.md](references/persistence-wiring.md) for call-chain checklist.

### Phase 5 — Verify

```powershell
py -3 scripts/smoke_bridge.py --project-dir "<path>" --abbr "<Abbr>"
py -3 scripts/audit_project.py --project-dir "<path>" --abbr "<Abbr>"
dotnet build "<path>/<Project>.csproj"
```

发布前额外检查：`audit_project.py` 的 `Release Python runtime safety` 小节中，`.csproj copies {Abbr}Env to output` 必须为 `True`；`{Abbr}Env/pyvenv.cfg`、`Release output pyvenv.cfg`、`Release absolute Python path leaks found` 都必须为 `False`。

**Persistence acceptance (memory):** `%AppData%/{AppId}/session_snapshot.json` with `uiState.statusText` + `user_settings.json` with WindowPlacement after calc/exit.

**Archive:** Save As `{Ext}` round-trip on **user projects**, not the fixture.

## Maintainer E2E — AgentStatistics 夹具

Do **not** hand-edit the test project. **Phase B（memory）冻结**；**Phase C（archive）** 为独立补充轨，互不覆盖。

### Phase A — Agent 缓存 intake（memory E2E 前必做）

```powershell
py -3 scripts/inspect_appdata_cache.py --app-id AgentStatistics --check
```

若 `actionRequired=true`：使用当前宿主的结构化提问能力询问用户是否为本软件数据；Codex 等无专用控件时，用单题 Markdown 选票并等待用户回复。见 [references/agent-cache-intake.md](references/agent-cache-intake.md)。

### Phase B — memory Scaffold + verify（冻结，勿改命令块）

```powershell
# Run from the skill root: wpf-python-mvvm-builder
# Adjust this path if your AgentStatistics fixture is stored elsewhere.
$proj = "..\..\测试专用\AgentStatistics"

py -3 scripts/reset_agent_statistics_fixture.py --project-dir $proj --apply
py -3 scripts/scaffold_dual_stack.py --project-dir $proj --abbr AS --persistence memory --app-id AgentStatistics --root-namespace AgentStatistics --display-name "Agent Statistics" --include-form-demo --apply
py -3 scripts/smoke_bridge.py --project-dir $proj --abbr AS
py -3 scripts/memory_persistence_smoke.py --project-dir $proj --abbr AS --app-id AgentStatistics --display-name "Agent Statistics" --include-form-demo
py -3 scripts/verify_persistence_artifacts.py --mode memory --app-id AgentStatistics --require-sample-result --require-ui-state --require-window-settings --require-form-demo
py -3 scripts/audit_project.py --project-dir $proj --abbr AS --expect memory
dotnet build $proj/AgentStatistics.csproj
```

**Manual UI:** F5 → 填写测试表单 → 等 ~0.5s 或关窗 → relaunch → **六个文本框 + 窗口布局 + 状态栏** 恢复。见 [references/persistence-wiring.md](references/persistence-wiring.md)。

### `--include-form-demo`（memory / archive 可选）

用户项目默认**不带**测试表单 UI。夹具 / 验收显式加 `--include-form-demo`：

| 模式 | 模板 | 行为 |
|------|------|------|
| `memory` | `form-demo/` | 防抖 → `SaveSnapshot`；无文件菜单 |
| `archive` | `form-demo-archive/` | 编辑 → `MarkDirty`；**Ctrl+S** / 文件菜单 → `{Ext}` 工程包 |

### Phase C — archive 补充验收（`.ast`，不 reset memory）

**前置**：夹具已为 archive，或已完成 Phase B 后 migrate。勿对 archive 夹具再跑 `reset` + memory scaffold。

```powershell
# Run from the skill root: wpf-python-mvvm-builder
# Adjust this path if your AgentStatistics fixture is stored elsewhere.
$proj = "..\..\测试专用\AgentStatistics"

# 方式 1：自 memory 迁移（生成 sample_import.ast）
py -3 scripts/migrate_persistence_mode.py --project-dir $proj --abbr AS `
  --from memory --to archive --ext .ast --import-last-snapshot --apply

# 方式 2：已是 archive 时，仅重刷模板
py -3 scripts/scaffold_dual_stack.py --project-dir $proj --abbr AS --persistence archive `
  --ext .ast --root-namespace AgentStatistics --display-name "Agent Statistics" `
  --include-form-demo --migrate-to archive --apply

py -3 scripts/run_agent_statistics_archive_e2e.py --project-dir $proj --abbr AS
py -3 scripts/inspect_file_association.py --ext .ast --prog-id AgentStatistics.ProjectFile --check
```

**Manual UI（archive）：** F5 一次（写入 HKCU 关联）→ 双击 `.ast` 或带参启动 → 六框恢复；**Ctrl+S** 保存；菜单「文件」可展开。见 [references/persistence-wiring.md](references/persistence-wiring.md) archive 专节。

## Archive on user projects

```powershell
py -3 scripts/scaffold_dual_stack.py --project-dir "<user-path>" --persistence archive --ext ".gpdx" ... --apply
```

## References

- [architecture-map.md](references/architecture-map.md)
- [persistence-modes.md](references/persistence-modes.md)
- [persistence-wiring.md](references/persistence-wiring.md) — 中文运行期接线与 E2E
- [ui-state-contract.md](references/ui-state-contract.md) — uiState / WindowPlacement 契约
- [agent-cache-intake.md](references/agent-cache-intake.md) — Agent 侧旧版 AppData 缓存 intake
- [csproj-wiring.md](references/csproj-wiring.md)
- [anti-patterns.md](references/anti-patterns.md)
