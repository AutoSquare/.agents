# 智能体规则

| 目录 | 格式 | 适用平台 |
|------|------|----------|
| [`cursor/`](cursor/) | `.mdc`（YAML 头 + 正文） | **Cursor Project Rules**（可选 `-ProjectPath` 安装） |
| [`universal/`](universal/) | `.md` | **Claude Code、OpenCode、Trea**；**Cursor User Rules 手动录入源** |

## Cursor：双通道

### 1. User Rules（跨项目，默认手动）

运行 setup 脚本**后**，按 [`universal/AGENTS.md`](universal/AGENTS.md) **自第 2 个 `##` 二级标题起至文末**逐条录入（脚本摘要显示条数与节名，**首节已排除**）：

**Cursor Settings → Rules → User → New User Rule**

- 每节一条规则，勿整份粘贴 AGENTS.md
- 脚本默认**不**自动安装任何 rules

### 2. Project Rules（单工程，可选）

进入 `.agents` 目录，指定工程根路径：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1" -ProjectPath "D:\GeoPile"
```

将 manifest 托管的 `rules/cursor/*.mdc` 增量复制到 `{ProjectPath}\.cursor\rules\`，在 Settings → **Project** 可见。

### Cursor 规则清单（`.mdc`）

| 文件 | 作用域 | 内容 |
|------|--------|------|
| `00-cursor-ide.mdc` | 始终 | Cursor：中文回复、可直接改代码 |
| `01-language-and-naming.mdc` | 始终 | 界面中文、路径/文件名英文 |
| `02-doc-linkage-and-delivery.mdc` | 始终 | 代码与文档同步交付 |
| `03-pre-development-requirements.mdc` | 始终 | 先读文档再开发 |
| `04-comment-and-writing-quality.mdc` | 始终 | 注释与写作质量 |
| `05-code-organization-and-architecture.mdc` | 始终 | 代码组织与架构 |
| `06-pre-submit-checklist.mdc` | 始终 | 提交前检查清单 |
| `07-skills-authoring.mdc` | `skills/**/SKILL.md` | Skills 可迁移与文档 |
| `08-csharp-xml-docs.mdc` | `**/*.{cs,csproj,xaml}` | C# XML 注释与格式 |
| `09-git-commit-message.mdc` | 始终 | Git 提交说明规范 |
| `agents-entry.mdc` | 始终 | `.agents` 包入口与 MCP |
| `literature-integrity.mdc` | 始终 | 文献诚信 |
| `literature-workflow.mdc` | `**/*.{md,mdx}` | 文献 Skill/MCP 选用 |
| `karpathy-guidelines.mdc` | 始终 | Karpathy 四原则 |

## 通用：Claude Code / OpenCode / Trea

使用 **[`universal/AGENTS.md`](universal/AGENTS.md)**（单文件 Markdown，无 Cursor 专属 IDE 条款）。

| 平台 | 建议挂载方式 |
|------|----------------|
| **Claude Code** | 将正文合并进项目根 `CLAUDE.md`，或 `import`/引用 `.agents/rules/universal/AGENTS.md` |
| **OpenCode** | 在 OpenCode 规则设置中指向该文件，或复制到其要求的 rules 目录 |
| **Trea** | 开启 `将AGENTS.md包含在上下文中` 设置选项 |

## 新增或修改规则

1. **Cursor `.mdc`**：编辑 `cursor/` 下文件，更新 [`manifest.json`](../manifest.json) 的 `installManifest.managedRules`，再按需 `-ProjectPath` 安装。  
2. **通用 / User 手动源**：编辑 `universal/AGENTS.md`，保持与 `cursor/` 团队条款一致（Cursor 专属条目写在 `00-cursor-ide.mdc`）。

`.mdc` 格式说明见 Cursor 文档：`description`、`alwaysApply`、`globs` 字段。
