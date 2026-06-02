# 命名约定

## 目录

| 用途 | 名称 | 入库 |
|------|------|------|
| Python 脚本 | `{Abbr}Py/` | 是 |
| Python 运行时 | `{Abbr}Env/` | **否**（gitignore） |
| 临时工作区 | `%Temp%\{Abbr}Work_{GUID}/` | 否 |

示例：`Abbr=AS` → `ASPy/`、`ASEnv/`、`AS_WORKSPACE` 环境变量。

## 禁止中文的路径与文件名

- 项目简写、`*Py`、`*Env`、Driver 文件名、Assets 子目录（除 JSON **表逻辑名** 可为中文，如 `数据表/项目基本信息.json`）
- 若用户给出中文项目名：提示提供英文简写；**软件窗口标题可中文**

## gitignore 片段（模板见 `templates/gitignore-snippet.txt`）

```
{Abbr}Env/
*{Abbr}Work_*
```

## csproj 注释锚点

```xml
<!-- dual-stack: {Abbr}Py -->
<!-- dual-stack: {Abbr}Env -->
<!-- dual-stack: packages -->
```

便于脚本幂等追加与 audit 检测。
