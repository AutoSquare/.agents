# Codex 安装说明

本文记录 `.agents` 包面向 Codex 的安装方式。Cursor 仍使用 [`PORTABLE.md`](PORTABLE.md) 与 `scripts/setup-cursor-agents.ps1`。

## 一键安装

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

# 指定 Codex 用户目录（测试或多环境时使用）
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1" -CodexHome "D:\tmp\codex-home"
```

## 增量边界

脚本只覆盖 [`manifest.json`](manifest.json) 中 `codexInstallManifest` 声明的托管项：

- `$CODEX_HOME/AGENTS.md`
- `$CODEX_HOME/agent-rules/<managed-rule>.md`
- `$CODEX_HOME/skills/<managed-skill>/`
- `$CODEX_HOME/mcp-servers/<managed-mcp-source>/`
- `codex mcp` 中同名托管 MCP 注册：`academic-research`、`zotero`、`deck-builder`、`ppt-markdown`、`campus-net`

脚本不会清空 `$CODEX_HOME/skills`、`$CODEX_HOME/agent-rules`、`$CODEX_HOME/mcp-servers`，也不会卸载用户自己添加的其他 MCP。

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
