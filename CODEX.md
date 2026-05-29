# Codex 安装说明

本文记录 `.agents` 包面向 Codex 的安装方式。Cursor 仍使用 [`PORTABLE.md`](PORTABLE.md) 与 `scripts/setup-cursor-agents.ps1`。

## 一键安装

前置要求：Git、Python 3.10+、Node.js、npm 与 Codex CLI。脚本会优先用 Windows `py` 启动器选择 `py -3.13`、`py -3.12`、`py -3.11`、`py -3.10`，最后才检查 PATH 中的 `python`；因此 PATH 中残留 Python 3.6 不会再导致 Python MCP 依赖安装失败。

在 `.agents` 目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1"
```

常用参数：

```powershell
# 预览将更新的托管项，不写入磁盘
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -WhatIf -NoClearScreen

# 只安装 Rules 与 Skills，不构建或注册 MCP
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -SkipMcpInstall

# 海外或需官方 PyPI 时
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -UseOfficialPipIndex

# 自定义 pip 镜像
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -PipIndexUrl "https://mirrors.aliyun.com/pypi/simple/"

# 指定 Codex 用户目录（测试或多环境时使用）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -CodexHome "D:\tmp\codex-home"

# 调试：不清屏，末尾展开全部安装细节
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -Verbose -NoClearScreen
```

## 增量边界

脚本只覆盖 [`manifest.json`](manifest.json) 中 `codexInstallManifest` 声明的托管项：

- `$CODEX_HOME/AGENTS.md`
- `$CODEX_HOME/agent-rules/<managed-rule>.md`
- `$CODEX_HOME/skills/<managed-skill>/`
- `$CODEX_HOME/mcp-servers/<managed-mcp-source>/`
- `codex mcp` 中同名托管 MCP 注册：`academic-research`、`zotero`、`deck-builder`、`ppt-markdown`、`campus-net`

脚本不会清空 `$CODEX_HOME/skills`、`$CODEX_HOME/agent-rules`、`$CODEX_HOME/mcp-servers`，也不会卸载用户自己添加的其他 MCP。

对托管 MCP 源码目录，脚本会刷新仓库内随包携带的源码文件，但会保留已安装依赖目录（例如 `.venv`、`node_modules`）和依赖安装标记；当 `requirements.txt`、`package.json` 或 `package-lock.json` 未变化且入口文件存在时，会跳过重复的 `pip install` / `npm install` / build。因此首次安装仍可能较慢，后续重复执行应只做轻量刷新与 `codex mcp` 注册更新。

安装 MCP 依赖时，脚本会在终端显示当前子步骤和 `pip` / `npm` 输出；Python MCP 会在写入依赖标记前检查 `mcp` 模块是否真实可导入，避免 `.venv` 已创建但依赖未装完时被误判为可用。`pip install` 默认使用清华 tuna 镜像（`https://pypi.tuna.tsinghua.edu.cn/simple`）；海外用户可加 `-UseOfficialPipIndex`，或通过 `-PipIndexUrl` 指定其它 index。`pip install` 使用 `--timeout 30 --retries 3 --prefer-binary`，网络源异常时会尽快显式失败，而不是长时间无反馈。

`cad-structure-layout-debug` 属于 Codex 托管 Skill，安装后位于：

```text
%USERPROFILE%\.codex\skills\cad-structure-layout-debug
```

Cursor 侧安装与验证见 [`PORTABLE.md`](PORTABLE.md) 与已安装目录内 `README-cursor.md`。

## MCP

Codex MCP 使用 `codex mcp add/remove/list/get` 管理，不直接写 `config.toml`。

托管 MCP 安装到：

```text
%USERPROFILE%\.codex\mcp-servers
```

`campus-net` 的用户级 Profile、会话与 `local.env` 默认在：

```text
%USERPROFILE%\.codex\campus-net
```

可用 `CAMPNET_USER_ROOT` 覆盖该目录。

## 排查

```powershell
codex mcp list
codex mcp get academic-research --json
codex mcp get campus-net --json
```

入口文件应指向 `%USERPROFILE%\.codex\mcp-servers\...`，而不是 `.cursor`。

Python MCP 安装时，脚本通过 `--no-cache-dir` 调用 pip，并按进程退出码判断失败。pip 缓存损坏产生的 `Cache entry deserialization failed, entry ignored` 这类 stderr 警告会写入详细日志，但不会再被 PowerShell 误判为安装失败。

如果需要强制重装某个 MCP 的依赖，可以删除对应目录下的 `.venv` / `node_modules` 或 `.agents-*-deps.sha256` 标记后重新运行安装脚本。若 `.venv` 存在但 `import mcp` 失败（半安装状态），删除该 MCP 目录下的 `.venv` 或 `.agents-python-deps.sha256` 后重跑即可。

若安装看起来卡在第一个 MCP，先看终端最后一条 `->` 子步骤；常见卡点是 `academic-research-mcp` 的 `pip install -r requirements.txt`（官方 PyPI 在国内可能极慢，默认已改用 tuna）。加 `-Verbose -NoClearScreen` 可保留完整 `pip` 输出：

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -Verbose -NoClearScreen
```

可用下面命令确认依赖是否装完整：

```powershell
& "$env:USERPROFILE\.codex\mcp-servers\academic-research-mcp\.venv\Scripts\python.exe" -c "import mcp; print('academic-research deps ok')"
```
