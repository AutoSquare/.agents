# Agent 侧 AppData 缓存 intake（memory）

**不在 WPF 运行时弹窗。** 由 Agent 在 scaffold / E2E **之前**执行。

## 何时检查

| 时机 | 命令 |
|------|------|
| Maintainer E2E 开始前 | `inspect_appdata_cache.py --check` |
| 用户项目 intake 确认 memory + appId 后 | 同上 |

## 检查命令

```powershell
py -3 scripts/inspect_appdata_cache.py --app-id <AppId> --check
```

输出 JSON 字段：

| 字段 | 含义 |
|------|------|
| `status` | `missing` / `ok` / `legacy` / `corrupt` |
| `actionRequired` | true 时 **必须**询问用户并取得显式选择 |
| `agentPrompt` | 可直接展示给用户的中文说明 |
| `issues` | 具体问题列表 |

退出码：`0` 正常；`10` 需用户决策。

## Agent 必问（actionRequired=true）

按当前宿主选择提问方式：结构化提问工具优先；没有专用工具时，用 Markdown 单题选票并停止等待用户回复。

1. **是否为本软件数据？**（对照 `appId` / 项目 displayName）
2. 若是：
   - **迁移**：转为当前 memory 格式（修复多层引号、normalize tables）
   - **删除重建**：删除整个 `%AppData%/{AppId}/` 目录

**禁止**未获用户选择就 `--migrate` 或 `--purge`。

## 执行命令

```powershell
# 迁移（保留可修复业务表 + uiState）
py -3 scripts/inspect_appdata_cache.py --app-id <AppId> --display-name "<名>" --migrate --apply

# 删除整个缓存目录（快照 + user_settings）
py -3 scripts/inspect_appdata_cache.py --app-id <AppId> --purge --apply
```

## 与 verify 的关系

| 脚本 | 职责 |
|------|------|
| `inspect_appdata_cache.py` | E2E **前**：旧版/损坏缓存 → 用户决策 |
| `verify_persistence_artifacts.py` | E2E **后**：快照结构、round-trip、form-demo 表可解析 |

## 典型 legacy 征象

- `dataTables` 值以 `\"` 开头（GetRawText 历史 bug）
- `formatVersion` 缺失或与当前不一致
- `测试表单` JSON 无法 `json.loads`

见 [anti-patterns.md](anti-patterns.md#ui-记忆)。
