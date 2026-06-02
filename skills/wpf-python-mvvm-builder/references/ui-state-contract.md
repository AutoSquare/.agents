# UI 状态与窗口布局契约（memory 模式）

本文定义 memory 持久化路线下 **跨会话 UI 记忆** 的标准字段、读写时机与扩展规则。archive 模式仅复用 **WindowPlacement**（`user_settings.json`），不使用 `session_snapshot.json` 的 `uiState`。

## 双存储分工

| 存储 | 路径 | 职责 |
|------|------|------|
| 业务 + 状态栏记忆 | `%AppData%/{AppId}/session_snapshot.json` | 业务表 + `uiState` |
| 窗口布局偏好 | `%AppData%/{AppId}/user_settings.json` | 窗口几何与 WindowState |

二者独立读写，**禁止**把窗口 Left/Top 写入 `uiState`（应走 `UserSettingsStore`）。

---

## session_snapshot.json

### 顶层结构

```json
{
  "formatVersion": 1,
  "displayName": "应用名",
  "dataTables": { "项目基本信息": "[...]" },
  "materialTables": { "示例材料": "[...]" },
  "uiState": {
    "statusText": "样本计算完成，已写入会话快照\nC:\\Users\\...\\session_snapshot.json"
  }
}
```

- `formatVersion`：当前固定为 `1`；未来增键时递增并文档化迁移。
- 写入方式：先写 `.tmp`，再 `File.Move` 覆盖（原子写入）。

### uiState 键表

| 键 | 类型 | 必选（模板） | 说明 |
|----|------|--------------|------|
| `statusText` | string | **是** | 主窗口状态栏/摘要文本；可含换行 |
| *(业务扩展)* | 任意 JSON 可序列化类型 | 否 | camelCase 命名；须在项目开发说明中登记 |

### Merge 规则（启动恢复）

1. `ProjectSession.EnsureInitialized()` → `SessionSnapshotStore.TryLoad` 读出 `uiState.statusText` → 存为 `SavedStatusText`。
2. `MainWindowViewModel.RefreshSessionStatus(restoredFromSnapshot, savedStatusText)`：
   - 若 `restoredFromSnapshot == true` 且 `savedStatusText` 非空 → **直接使用** `savedStatusText`，不再拼接默认「已恢复上次会话」文案。
   - 否则 → 按无快照/无 statusText 逻辑生成默认提示。
3. 业务扩展键：模板 **不** 自动 merge；业务 VM 在 `OnStartup` 后自行读取 `Saved*` 或扩展 `TryLoad`。

### 写入时机（禁止绕开 VM）

| 时机 | 调用方 | 要求 |
|------|--------|------|
| 样本计算成功 | `MainWindowViewModel` | **先** 设置最终 `StatusText`，**再** `SaveSnapshot(BuildUiState(StatusText))` |
| 窗口关闭 | `MainWindow.OnClosing` | `PersistOnExit(BuildUiState(StatusText))` |
| 计算 Service | `SampleCalculationService` | **禁止** 调用 `SaveSnapshot`（避免 uiState 早于 StatusText 定稿） |

### 扩展指南

```csharp
// 合并多个 uiState 片段
public static IReadOnlyDictionary<string, object?> BuildUiState(string statusText, string? activeTab = null)
{
    var dict = new Dictionary<string, object?> { ["statusText"] = statusText };
    if (activeTab != null)
        dict["activeTab"] = activeTab;
    return dict;
}
```

- 新增键须在 `%项目%/docs/开发说明.md` 的「uiState 扩展键」小节登记。
- 禁止在 `Model` 层直接写 `SessionSnapshotStore`；经 `ProjectSession` 或 VM 编排。

---

## user_settings.json — WindowPlacement

### 字段表

| 键 | 类型 | 说明 |
|----|------|------|
| `windowWidth` | number | 窗口宽度（像素）；Normal 或 RestoreBounds |
| `windowHeight` | number | 窗口高度 |
| `windowLeft` | number | 窗口左边缘（屏幕坐标） |
| `windowTop` | number | 窗口上边缘 |
| `windowState` | string | `Normal` / `Maximized` / `Minimized`（模板主要处理前两者） |

### 读写时机

| 操作 | 时机 | 实现 |
|------|------|------|
| 恢复 | `MainWindow.Loaded` 之后 | `ApplicationBootstrap.ApplyWindowGeometry` → `UserSettingsStore.LoadWindowPlacement` |
| 保存 | `MainWindow.OnClosing` | `ApplicationBootstrap.SaveWindowGeometry` |

### 最大化语义

关窗时若 `WindowState == Maximized`，保存 **`RestoreBounds`**（还原后的 Left/Top/Width/Height），并单独保存 `windowState: "Maximized"`。下次启动先设尺寸位置，再设 `WindowState`。

### 禁止

- 在构造函数 / `InitializeComponent` **之前或之后立即** 调用 `ApplyWindowGeometry`（会被 XAML 默认 `Height`/`Width` 覆盖）。
- 仅用 `windowWidth`/`windowHeight` 而忽略 Left/Top/State（用户反馈「窗口状态没恢复」的常见根因）。

---

## 验收（脚本）

```powershell
py -3 scripts/verify_persistence_artifacts.py --mode memory --app-id <AppId> `
  --require-sample-result --require-ui-state --require-window-settings
```

见 [persistence-wiring.md](persistence-wiring.md) 完整 E2E。
