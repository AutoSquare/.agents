# WPF + Python MVVM Builder — Codex 使用说明

## 位置

Codex 用户级安装目录：

```text
%USERPROFILE%\.codex\skills\wpf-python-mvvm-builder
```

源目录可直接作为开发副本使用；若要正式安装到 Codex，将整个 `wpf-python-mvvm-builder/` 目录复制到上述位置。Codex 展示元数据在 `agents/openai.yaml`，Cursor 使用说明仍在 `README-cursor.md`。

## 使用边界

- 只能在已有 Visual Studio WPF 空项目上增量补全；不要从零创建 WPF 项目。
- 开工前先按 `references/intake-checklist.md` 完成 intake，取得用户显式选择。
- 涉及旧 AppData 缓存时，先运行 `inspect_appdata_cache.py --check`；需要迁移或删除时必须先问用户。
- 先 `--dry-run`，确认文件计划后再 `--apply`。

## Codex 提问方式

本 skill 的历史文档可能提到 `AskQuestion`。在 Codex 中按以下等价规则执行：

| 场景 | Codex 做法 |
|------|------------|
| 有结构化提问工具 | 使用结构化工具，每轮只问一个关键决策 |
| 没有结构化提问工具 | 用 Markdown 单题选票列出互斥选项并停止等待 |
| 用户未选择 | 不运行 `--apply`、`--migrate` 或 `--purge` |

## 常用流程

```powershell
# 从 skill 根目录执行
py -3 scripts/audit_project.py --project-dir "<path>" --abbr "<Abbr>"

# 先预览
py -3 scripts/scaffold_dual_stack.py --project-dir "<path>" --abbr "<Abbr>" --persistence memory --app-id "<AppId>" --dry-run

# 确认后应用
py -3 scripts/scaffold_dual_stack.py --project-dir "<path>" --abbr "<Abbr>" --persistence memory --app-id "<AppId>" --apply

# 验证
py -3 scripts/smoke_bridge.py --project-dir "<path>" --abbr "<Abbr>"
py -3 scripts/audit_project.py --project-dir "<path>" --abbr "<Abbr>"
dotnet build "<path>/<Project>.csproj"
```

archive 路线把 `--persistence memory --app-id "<AppId>"` 替换为：

```powershell
--persistence archive --ext "<Ext>"
```

## 不影响 Cursor

- 不修改 `README-cursor.md`。
- 不依赖 `.cursor` 路径。
- 不要求更新 Cursor install manifest。
- 若未来要纳入可迁移 `.agents` 包，只登记 `codexInstallManifest.managedSkills`，不要改 Cursor 的 `installManifest.managedSkills`。
