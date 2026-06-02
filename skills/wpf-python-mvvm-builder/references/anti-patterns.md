# 反模式

## 关窗与子进程

- ❌ 关窗只处理脏保存，不 `CancelAndKillAll()`
- ❌ Kill 后仍写「计算失败」业务日志
- ❌ stdout 回调在 `IsShuttingDown` 时仍 `Dispatcher.Invoke`
- ✅ 见 GeoPile `CalculationRunCoordinator` 与 workspace 规则 p15

## 分层

- ❌ `Model` 引用 `View` / 控件类型
- ❌ 菜单 Click 共用单一 handler 混跑多阶段计算
- ✅ 每计算入口先 `ValidateInputs` / `ValidationCoordinator`

## 路径与仓库

- ❌ `{Abbr}Env/` 提交到 git
- ❌ Skill 脚本硬编码 `GeoPile` 或本机盘符
- ❌ 中文目录名存放 Python 或 Env

## Scaffold

- ❌ 未 `--dry-run` 直接覆盖用户 MainWindow 业务
- ❌ 冲突文件静默覆盖
- ✅ 冲突清单 + 用户确认合并策略

## Python

- ❌ Driver 不经 Bridge 直接 `Process.Start`
- ❌ 取消返回非零 exitCode 当失败
- ✅ `CancellationToken` 贯通至 `RunScriptAsync`

## WPF 菜单栏

- ❌ 把 `MenuItem` 直接挂在 `DockPanel` / `StackPanel` / `Grid` 下（无 `Menu` 容器，无法弹出子菜单）
- ❌ 菜单与正文挤在同一 `DockPanel` 且带 `Margin`，易出现命中区异常；菜单栏应独占 `Grid` 首行
- ✅ 与 GeoPile 一致：`<Menu Grid.Row="0" Background="{StaticResource DefaulMenuBackground}">` 内再挂顶级 `MenuItem`

## archive 文件关联与双击打开

- ❌ archive 仍用 `StartupUri="MainWindow.xaml"`，无法接收 Explorer 双击传入的 `{Ext}` 路径
- ❌ 未注册 `HKCU\Software\Classes\{Ext}`，资源管理器无法用本 exe 打开工程包
- ✅ `App.xaml` 使用 `Startup="Application_Startup"`，解析 `e.Args` 中的 `{Ext}` 并优先 `OpenAsync`
- ✅ 启动时 `FileAssociationUtilities.TryRegisterOnStartup()` 写入 open 命令 `"exe" "%1"`

详见 [persistence-wiring.md](persistence-wiring.md) archive 专节。

## UI 记忆

- ❌ 在 `MainWindow` 构造函数里 `ApplyWindowGeometry`（XAML 默认尺寸会覆盖）
- ❌ `SampleCalculationService` 内调用 `SaveSnapshot`（uiState 早于 StatusText 定稿）
- ❌ 只读写 `windowWidth`/`windowHeight`，忽略 Left/Top/WindowState
- ❌ scaffold 了 `uiState` 字段但 `TryLoad` 不读、`Save` 不写 `statusText`
- ❌ `SessionSnapshotStore.CopyTables` 对字符串表用 `GetRawText()`（会把 JSON 字符串外层引号读入，重启后表反序列化失败、业务数据「像没保存」）
- ✅ `Loaded` → `ApplyWindowGeometry`；关窗 `SaveWindowGeometry` + `PersistOnExit(BuildUiState)`
- ✅ `CopyTables` 对 `JsonValueKind.String` 用 `GetString()`，必要时 `UnwrapOverQuotedJson` 修复历史损坏
- ✅ form-demo：`VM ↔ dataTables` 防抖自动保存 + 关窗 `CommitTextBoxBindings` + `FlushPendingFormEdits`
- ✅ 见 [ui-state-contract.md](ui-state-contract.md)、[agent-cache-intake.md](agent-cache-intake.md)
