# Matt Pocock → Cursor 改写规则

对复制到 `~/.cursor/skills/<skill-name>/` 下的每个文件执行（`.md`、`.sh` 等文本文件）。

## 1. 路径与依赖

- **删除** 指向 mattpocock 仓库根、`skills.sh` 安装器、`link-skills.sh` 的说明。
- **禁止** 在技能正文中写死本机绝对路径（如 `D:\...\mattpocock`）。
- **保留** 技能目录内的相对链接（如 `[tests.md](tests.md)`、`../grill-with-docs/ADR-FORMAT.md`）—— 安装脚本会把 `setup-matt-pocock-skills` 的种子文件一并复制到该技能目录，或把跨技能引用改成「见 grill-with-docs 技能内的 ADR-FORMAT」；同仓库内复制的技能保持相对路径有效。

## 2. 斜杠命令 → 技能名

仅替换**已知技能**的斜杠调用，勿改代码路径（如 `src/triage/handler.ts`）。

| 原文 | 改写为 |
|------|--------|
| `/setup-matt-pocock-skills` | **setup-matt-pocock-skills** 技能 |
| `/triage` | **triage** 技能 |
| `/grill-with-docs` | **grill-with-docs** 技能 |
| `/grill-me` | **grill-me** 技能 |
| `/tdd` | **tdd** 技能 |
| `/diagnose` | **diagnose** 技能 |
| `/to-prd` | **to-prd** 技能 |
| `/to-issues` | **to-issues** 技能 |
| `/zoom-out` | **zoom-out** 技能 |
| `/caveman` | **caveman** 技能 |
| `/handoff` | **handoff** 技能 |
| `/improve-codebase-architecture` | **improve-codebase-architecture** 技能 |
| `/prototype` | **prototype** 技能 |

说明句式统一为：「先应用 **setup-matt-pocock-skills** 技能」而非「先运行 `/setup-…`」。

## 3. 项目指引文件

`setup-matt-pocock-skills` 内：

- 优先编辑已有 **`AGENTS.md`**。
- 若仅有 `CLAUDE.md` 且无 `AGENTS.md`，编辑 `CLAUDE.md`（内容 Cursor 与 Claude 均可读）。
- 若两者皆无，**新建 `AGENTS.md`**（勿因 Cursor 单独建一套规则文件，除非用户明确要求 `.cursor/rules`）。
- 在 SKILL 中补充一句：Cursor 用户通过 `@setup-matt-pocock-skills` 或描述触发本技能。

## 4. Frontmatter

- 保留 `name`、`description`；`description` 保持第三人称并含「在…时使用」。
- 保留 `disable-model-invocation: true`（若源文件有）—— Cursor 支持仅显式调用。
- 无需 `claude`-专用字段。

## 5. Claude Code 专属技能

| 源技能 | 处理 |
|--------|------|
| `git-guardrails-claude-code` | 安装为 `git-guardrails`，按 CURSOR-GIT-GUARDRAILS.md 重写 SKILL.md |
| `git-guardrails-claude-code` 的 shell 脚本 | 可保留作参考；Cursor 用 `beforeShellExecution` + hooks.json |

其余 misc/engineering/productivity 技能通常只需斜杠命令与路径清理。

## 6. description 微调（可选）

在 description 末尾追加触发语（若尚未包含）：

- 工程类：「在 Cursor 中用户 @<技能名> 或描述相关任务时使用。」
- 不必每条都加，避免超 1024 字符。

## 7. 校验清单

安装后抽查任意 2～3 个技能：

- [ ] `~/.cursor/skills/<name>/SKILL.md` 存在且 frontmatter 合法
- [ ] 正文无 `/setup-matt-pocock-skills` 等斜杠形式（代码路径除外）
- [ ] 无 `~/.claude/`、`.claude/hooks` 作为**唯一**操作指引（git-guardrails 除外）
- [ ] 附属 md / scripts 已随目录复制
