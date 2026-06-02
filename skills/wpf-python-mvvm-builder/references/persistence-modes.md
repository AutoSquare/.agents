# 持久化双路线（memory / archive）

## 模式对照

| id | 用户语义 | 工程文件 | 跨会话业务数据 | 用户偏好 |
|----|----------|----------|----------------|----------|
| `memory` | 运行时 / SpectLeakage 类 | **无** `{Ext}` 工程包 | `%AppData%/{AppId}/session_snapshot.json` | `%AppData%/{AppId}/user_settings.json` |
| `archive` | GeoPile 类持久化 | ZIP **`project{Ext}`** | 工程包内 `数据表/`、`材料库/` | `Properties/Settings` + 可选 AppData |

## session_snapshot.json（memory）

```json
{
  "formatVersion": 1,
  "displayName": "应用名",
  "dataTables": { "项目基本信息": "[...]" },
  "materialTables": { "示例材料": "[...]" },
  "uiState": {
    "statusText": "样本计算完成，已写入会话快照\nC:\\Users\\...\\AppData\\Roaming\\{AppId}\\session_snapshot.json"
  }
}
```

路径：`%AppData%/{AppId}/session_snapshot.json`（原子写入 `.tmp` → rename）。

## archive 工程包

见 [persistence-gpdx-pattern.md](persistence-gpdx-pattern.md)。

## 标记文件

项目根目录 `.dual-stack-persistence.json`：

```json
{
  "persistence": "memory",
  "abbr": "AS",
  "ext": ".asproj",
  "appId": "AgentStatistics",
  "rootNamespace": "AgentStatistics"
}
```

## 迁移

| 方向 | 脚本 | 数据 |
|------|------|------|
| memory → archive | `migrate_persistence_mode.py --from memory --to archive [--import-last-snapshot]` | snapshot → 可选 `sample_import{Ext}` |
| archive → memory | `--from archive --to memory` | 首个 `*{Ext}` → 写 snapshot |

模块切换由 `scaffold_dual_stack.py --migrate-to` 完成；**不删除**用户已有 `{Ext}` 文件。

## 运行期生命周期（scaffold 必须接线）

| 阶段 | memory | archive |
|------|--------|---------|
| 启动 | `ApplicationBootstrap.OnStartup` → `EnsureInitialized` + 读 snapshot（含 `uiState.statusText`）；`MainWindow.Loaded` → 恢复 WindowPlacement | `EnsureInitialized` + 可选 `TryOpenLastProjectAsync`；`Loaded` → WindowPlacement |
| 计算 | Export → Driver → Merge → VM 定稿 `StatusText` → **`SaveSnapshot(BuildUiState)`** | Export → Driver → Merge → **`MarkDirty()`** |
| 用户落盘 | 无工程菜单 | **文件→打开/保存/另存为** → `ProjectVault` |
| 退出 | `SaveWindowGeometry` + `PersistOnExit(BuildUiState)` | `SaveWindowGeometry` + 脏且已有路径则 **自动 Save** |

Intake 用户不确定持久化路线时，**默认 memory**（须在复述表格确认）。

**UI 记忆（memory 默认开启）**：`statusText` → snapshot；窗口几何 → `user_settings.json`。详见 [ui-state-contract.md](ui-state-contract.md)、[persistence-wiring.md](persistence-wiring.md)。

## FAQ

### memory 没有「另存为」菜单是否正常？

**正常。** memory 模式故意不提供 `{Ext}` 工程文件菜单；跨会话数据写入 `%AppData%/{AppId}/session_snapshot.json`。需要 ZIP 工程包时，intake 选 **archive** 并对用户项目 scaffold。

### AgentStatistics 夹具用哪种模式？

- **Phase B（默认 E2E）**：**memory** — 验收 AppData 快照与 form-demo 自动保存（命令块冻结，勿改）。
- **Phase C（补充）**：**archive**（夹具示例 `.ast`）— migrate 或直 scaffold + `run_agent_statistics_archive_e2e.py`；验证 Ctrl+S、双击打开、HKCU 关联。
- 二者**互不覆盖**；archive 夹具勿再 `reset` 回 memory 除非刻意回归 memory 轨。

### 如何确认 memory 快照已写入？

样本计算成功后状态栏显示 AppData 路径；或运行：

```powershell
py -3 scripts/verify_persistence_artifacts.py --mode memory --app-id <AppId> --require-sample-result --require-ui-state --require-window-settings
```

### 窗口位置/状态栏重启后不对？

常见原因：在构造函数而非 `Loaded` 后恢复几何；`SampleCalculationService` 过早 `SaveSnapshot` 导致 `uiState.statusText` 过期；只存宽高未存 Left/Top/WindowState。见 [ui-state-contract.md](ui-state-contract.md) 与 [anti-patterns.md](anti-patterns.md#ui-记忆)。

### 文本框/业务表「像没保存」、重启变空？

常见原因：`SessionSnapshotStore.CopyTables` 用 `GetRawText()` 读字符串表，外层引号被读入导致 JSON 反序列化失败。修复：`GetString()` + `UnwrapOverQuotedJson`。Agent E2E 前运行 `inspect_appdata_cache.py --check`；验收用 `verify_persistence_artifacts.py`（含 round-trip）。见 [agent-cache-intake.md](agent-cache-intake.md)。
