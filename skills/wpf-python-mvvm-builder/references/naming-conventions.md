# 命名约定

## 目录

| 用途 | 名称 | 入库 |
|------|------|------|
| Python 脚本 | `{Abbr}Py/` | 是 |
| 可移植 Python 环境 | `{Abbr}Env/` | 按项目发布策略；不得是 venv |
| 临时工作区 | `%Temp%\{Abbr}Work_{GUID}/` | 否 |

示例：`Abbr=AS` -> `ASPy/`、`ASEnv/`、`AS_WORKSPACE` 环境变量。

## 禁止中文的路径与文件名

- 项目简写、`*Py`、`*Env`、Driver 文件名、Assets 子目录必须使用 ASCII。
- JSON 表逻辑名可为中文，例如 `数据表/项目基本信息.json`。
- 软件窗口标题可中文。

## Python 环境规则

- `{Abbr}Env/` 存放可移植 Python 环境和依赖，会进入 Release 输出和安装包。
- `{Abbr}Env/pyvenv.cfg` 会记录开发机绝对路径，因此 `{Abbr}Env/` 不能是 venv。
- `setup_python_env.py` 默认创建 Python 3.10.11 embeddable 环境；替换旧 venv 时使用 `--force`。

## gitignore 片段

```text
*{Abbr}Work_*
```

是否忽略 `{Abbr}Env/` 由项目发布策略决定；若安装包从本机 Release 输出构建，`{Abbr}Env/` 可以不入库但必须在构建机存在。

## csproj 注释锚点

```xml
<!-- dual-stack: {Abbr}Py -->
<!-- dual-stack: {Abbr}Env -->
<!-- dual-stack: packages -->
```
