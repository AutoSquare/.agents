# Python Bridge 契约

## 环境变量

| 通用 | GeoPile |
|------|---------|
| `{ABBR}_WORKSPACE` | `GEOPILE_WORKSPACE` |

`ABBR` 是 `{Abbr}` 的大写，例如 `AS` -> `AS_WORKSPACE`。

## 进程启动

- `FileName` 由 `AppPaths.ResolvePythonExecutable` 解析：
  1. `{Root}/{Abbr}Env/python.exe`，发布版可移植 Python 环境。
  2. `{Root}/{Abbr}Env/Scripts/python.exe`，仅兼容旧项目，不能作为新发布规范。
  3. `{Root}/{Abbr}Env/bin/python`，Unix fallback。
- `WorkingDirectory` 为 `{Root}/{Abbr}Py`。
- `Arguments` 使用 `-u "{Abbr}Py/CalculateDriver.py"`。
- stdin 第一行为工作区根路径，并与 `{ABBR}_WORKSPACE` 环境变量一致。

## Driver 约定

1. 读取 stdin 工作区路径，写入 `{ABBR}_WORKSPACE`。
2. 读取 `数据表/项目基本信息.json`。
3. 写入 `数据表/样本计算结果.json`。
4. 成功返回 exit 0；失败返回非零并写 stderr。

## 发布环境规则

- `{Abbr}Env/` 存放可移植 Python 环境和依赖，会进入 Release 输出和安装包。
- `{Abbr}Env/pyvenv.cfg` 会记录创建者机器的 Python 绝对路径；若安装包包含它，目标电脑可能报 `No Python at C:\Users\...\Python...\python.exe`。
- 发布前用 `audit_project.py` 检查 `.csproj` 是否复制 `{Abbr}Env`、`{Abbr}Env/pyvenv.cfg` 是否不存在、Release 输出是否没有 `pyvenv.cfg` 或本机绝对路径。

## stdout 协议

- 可选行前缀 `<log>` 供 UI 日志消费。
- 取消时 C# 抛 `OperationCanceledException`，不要当计算失败写业务日志。

## 登记要求

- 所有 Driver 都经 `PythonBridge.RunScriptAsync` 启动。
- 子进程登记到 `ProcessJob.Add(proc)` 和 `CalculationRunCoordinator.RegisterProcess`。
- 关窗必须调用 `CancelAndKillAll()`。
