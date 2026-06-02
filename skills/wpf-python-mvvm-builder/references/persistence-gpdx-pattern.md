# 工程包持久化（GeoPile 式 ZIP）

## 包结构

```text
project{Ext}   (ZIP)
├── manifest.json
├── 数据表/
│   └── *.json
└── 材料库/
    └── *.json
```

## manifest.json 最小字段

```json
{
  "formatVersion": 1,
  "appId": "{{RootNamespace}}",
  "displayName": "{{DisplayName}}",
  "createdUtc": "2026-01-01T00:00:00Z"
}
```

## C# 侧

- `ProjectDocument`：内存表集合
- `ProjectVault.SaveAsync` / `LoadAsync`：ZIP 读写
- `ProjectSession.ExportWorkspaceForPython()`：导出到 `%Temp%\{Abbr}Work_{guid}/数据表|材料库`
- `ProjectSession.MergeTablesFromWorkspaceDirectory(path)`：Driver 成功后合并回文档

## Python 侧

- 环境变量 `{ABBR}_WORKSPACE` 指向临时目录根
- `PythonTableCatalog.py` 读写 `{workspace}/数据表/`、`{workspace}/材料库/`

## 与 GeoPile `.gpdx` 差异

本母版保留相同 **表目录语义** 与 Export-Merge 流程；扩展名与 manifest 字段由 intake 的 `{Ext}` 决定，不硬编码 `.gpdx`。
