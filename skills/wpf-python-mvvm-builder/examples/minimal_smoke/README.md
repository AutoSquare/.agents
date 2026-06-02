# AgentStatistics scaffold 预期目录树

**夹具固定为 memory 模式**（intake 默认；无另存为菜单，自动 AppData 快照）。archive 另存为验收在用户项目上执行。

## 共用（memory / archive 模板）

- `Themes/DefaultTheme.xaml`
- `Resources/icons/.gitkeep`（+ backgrounds, fonts）
- `Properties/Settings.settings`, `Resource.resx`, Designer 文件
- `ViewModel/`, `Services/`（Bridge、Coordinator 等）
- `ASPy/`, `ASEnv/`（scaffold `--apply` 自动创建 venv）
- `.dual-stack-persistence.json`
- `App.xaml` 合并 DefaultTheme

## AgentStatistics（memory 夹具）

- `Services/UserSettingsStore.cs`, `SessionSnapshotStore.cs`（含 WindowPlacement / uiState）
- `ApplicationBootstrap.cs`（启动恢复 snapshot + Loaded 窗口几何）
- **无** `ProjectFileService`、**无** 文件菜单
- **无** `Assets/Baseline/`

## archive（用户项目，非夹具）

- `Model/Persistence/ProjectVault.cs`
- `Services/ProjectFileService.cs`
- `MainWindow.xaml` 含 **文件→打开/保存/另存为**

## 持久化验收（夹具 memory）

```powershell
py -3 scripts/reset_agent_statistics_fixture.py --project-dir $proj --apply
py -3 scripts/scaffold_dual_stack.py --project-dir $proj --abbr AS --persistence memory --app-id AgentStatistics --root-namespace AgentStatistics --display-name "Agent Statistics" --apply
py -3 scripts/smoke_bridge.py --project-dir $proj --abbr AS
py -3 scripts/memory_persistence_smoke.py --project-dir $proj --abbr AS --app-id AgentStatistics --display-name "Agent Statistics"
py -3 scripts/verify_persistence_artifacts.py --mode memory --app-id AgentStatistics --require-sample-result --require-ui-state --require-window-settings
py -3 scripts/audit_project.py --project-dir $proj --abbr AS --expect memory
dotnet build $proj/AgentStatistics.csproj
```

**verify 新增参数：**

- `--require-ui-state` — 断言 `uiState.statusText` 非空
- `--require-window-settings` — 断言 `user_settings.json` 含 WindowPlacement 五字段

**手动 F5：** 调整窗口 → 样本计算 → 退出 → 再开 → 窗口布局与状态栏文案应与上次一致。详见 `references/persistence-wiring.md`。
