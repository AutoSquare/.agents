---
name: adapt-mattpocock-skills-for-cursor
description: >-
  将 mattpocock/skills 下的 Agent Skills 批量复制并改写为 Cursor 可用格式，安装到
  ~/.cursor/skills/（完整副本，非符号链接），换账号或换电脑无需保留 mattpocock 仓库。
  在用户要迁移 Matt Pocock 技能、让技能跨机可用、从 mattpocock 文件夹安装 Cursor
  skills、或提到「不依赖 mattpocock 项目」时使用。
---

# 将 Matt Pocock Skills 适配为 Cursor

目标：**自包含的个人技能**，装在 `~/.cursor/skills/<skill-name>/`，不依赖 `mattpocock/` 仓库路径。

## 快速执行

有 mattpocock 源码时，优先运行捆绑脚本（复制 + 文本改写 + 校验）：

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.cursor\skills\adapt-mattpocock-skills-for-cursor\scripts\install.ps1" -Source "D:\path\to\mattpocock"
```

- 省略 `-Source` 时脚本会在常见位置搜索 `mattpocock` 文件夹。
- 默认跳过 `deprecated/`、`personal/`、`in-progress/`；加 `-IncludeAll` 可全部安装。
- 安装后可在任意项目的 Cursor 里用 `@技能名` 或让 Agent 按 description 自动选用。

无源码、仅维护已安装副本时：直接编辑 `~/.cursor/skills/<name>/`，遵守 [ADAPTATION.md](ADAPTATION.md)。

## 工作流（Agent 手动执行时）

```
- [ ] 1. 定位源目录（用户提供的 mattpocock 路径，或工作区内的 mattpocock/）
- [ ] 2. 运行 install.ps1，或按 ADAPTATION.md 逐技能复制改写
- [ ] 3. 抽查：无绝对路径、无 /slash 命令、相对链接仍有效
- [ ] 4. 告知用户：工程类技能仍需在**目标仓库**运行 setup-matt-pocock-skills
- [ ] 5. 可选：git-guardrails 用 Cursor hooks 单独配置（见下文）
```

## Cursor 与 Claude Code 差异（摘要）

| 原习惯 | Cursor 做法 |
|--------|-------------|
| `~/.claude/skills` 符号链接到仓库 | `~/.cursor/skills/<name>/` **完整目录副本** |
| `/triage`、`/setup-…` 斜杠命令 | 技能名 + `@技能名`；正文写「应用 **triage** 技能」 |
| 仅 `CLAUDE.md` / `AGENTS.md` | 仍写 `AGENTS.md`（存在则更新）；无则新建 `AGENTS.md` |
| `.claude/hooks` + PreToolUse | `.cursor/hooks.json` + `beforeShellExecution`（见 create-hook 技能） |
| `git-guardrails-claude-code` | 安装为 `git-guardrails`，按 [CURSOR-GIT-GUARDRAILS.md](CURSOR-GIT-GUARDRAILS.md) 配置 |

完整替换表与边界情况：[ADAPTATION.md](ADAPTATION.md)。

## 默认安装的技能

**engineering/**：diagnose, grill-with-docs, improve-codebase-architecture, prototype, setup-matt-pocock-skills, tdd, to-issues, to-prd, triage, zoom-out

**productivity/**：caveman, grill-me, handoff, write-a-skill

**misc/**：migrate-to-shoehorn, scaffold-exercises, setup-pre-commit, git-guardrails（由 claude 版改写）

默认**不**安装：`deprecated/`、`personal/`、`in-progress/`（除非用户要求 `-IncludeAll`）。

## 仓库级配置（重要）

`setup-matt-pocock-skills` 会在**当前打开的项目**里创建 `docs/agents/*.md` 与 `AGENTS.md` 片段 —— 这是预期行为，与技能文件所在位置无关。

每个要用 to-issues / triage / tdd 等的仓库，仍需在该仓库运行一次 **setup-matt-pocock-skills**（或手动维护 `docs/agents/`）。

## 同步更新

上游 [mattpocock/skills](https://github.com/mattpocock/skills) 更新后：

1. 拉取最新 mattpocock 仓库
2. 重新运行 `install.ps1`（会覆盖 `~/.cursor/skills/` 下同名的 mattpocock 来源技能）
3. 勿改 `~/.cursor/skills-cursor/`（Cursor 内置技能）

## 附加资源

- [ADAPTATION.md](ADAPTATION.md) — 逐条改写规则与技能交叉引用
- [CURSOR-GIT-GUARDRAILS.md](CURSOR-GIT-GUARDRAILS.md) — git 护栏的 Cursor hooks 版
- [scripts/install.ps1](scripts/install.ps1) — 批量安装脚本
