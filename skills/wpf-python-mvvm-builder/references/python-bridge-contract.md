# Python Bridge 契约

## 环境变量

| 通用 | GeoPile |
|------|---------|
| `{ABBR}_WORKSPACE` | `GEOPILE_WORKSPACE` |

`ABBR` 为 `{Abbr}` 的大写（如 `AS` → `AS_WORKSPACE`）。

## 进程启动

- **FileName**：`AppPaths.ResolvePythonExecutable` 按序查找：
  1. `{Root}/{Abbr}Env/Scripts/python.exe`（`setup_python_env.py` 创建的 Windows venv）
  2. `{Root}/{Abbr}Env/python.exe`（GeoPile 式嵌入式布局）
  3. `{Root}/{Abbr}Env/bin/python`（Unix venv）
- **WorkingDirectory**：`{Root}/{Abbr}Py`
- **Arguments**：`-u "{Abbr}Py/CalculateDriver.py"`
- **stdin 第 1 行**：工作区根路径（与 env 一致）

## Driver 约定（最小 Sample）

1. 读 stdin 工作区路径，写入 `{ABBR}_WORKSPACE`
2. 读 `数据表/项目基本信息.json`
3. 写 `数据表/样本计算结果.json`（一行演示）
4. exit 0；失败 exit 1 + stderr

## stdout 协议（可选）

- 行前缀 `<log>` 供 UI 日志板消费（与 GeoPile 一致）
- 取消时 C# 抛 `OperationCanceledException`，**不得**当计算失败记日志

## 登记要求

- 所有 Driver 经 `PythonBridge.RunScriptAsync` 启动
- `ProcessJob.Add(proc)` + `CalculationRunCoordinator.RegisterProcess`
- 关窗须 `CancelAndKillAll()`
