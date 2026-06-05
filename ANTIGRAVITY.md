# Antigravity 安装说明

本文记录 `.agents` 包面向 Antigravity 的安装方式。

## 一键安装

**前置要求**：Windows 上已安装 Git、Python 3.10+、Node.js、npm 与 Antigravity CLI。如果 PATH 默认的 `python` 版本较旧，脚本会自动通过 Windows `py` 启动器向下兼容查找 `py -3.10` 或以上版本。

在 `.agents` 目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-antigravity-agents.ps1"
```

## 安装行为

脚本将读取 `manifest.json` 中的 `antigravityInstallManifest` 节点：
- 将托管的 Skills 增量拷贝到 `%USERPROFILE%\.gemini\config\plugins\agents\skills\`。
- 自动将 `rules/antigravity/` 下的所有 Markdown 文件拼接组合，写入 `%USERPROFILE%\.gemini\config\plugins\agents\plugin.json` 的 `system_prompt` 字段中，实现开箱即用的规则挂载。
- 将 MCP 服务端源码拷贝至 `%USERPROFILE%\.gemini\config\plugins\agents\mcp-servers\`（包括依赖安装），并自动更新 Antigravity 的相关配置文件。

**隔离保证**：脚本只会写入 `.gemini` 目录，完全不影响现有的 `.cursor` 和 `.codex` 安装环境。
