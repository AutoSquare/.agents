# 智能体规则

| 目录 | 格式 | 适用平台 |
|------|------|----------|
| [`cursor/`](cursor/) | `.mdc`（YAML 头 + 正文） | **Cursor** → 安装到项目 `.cursor/rules/` |
| [`universal/`](universal/) | `.md` | **Claude Code、OpenCode、Trea** 等 |

## Cursor：安装 `.mdc`

在含 `.agents` 的项目根执行：

```powershell
powershell -ExecutionPolicy Bypass -File ".\.agents\scripts\setup-cursor-agents.ps1" -InstallRules -OverwriteRules
```

将 `rules/cursor/*.mdc` 复制到 **项目根** `.cursor/rules/`。

### Cursor 规则清单

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
| `agents-entry.mdc` | 始终 | `.agents` 包入口与 MCP |
| `literature-integrity.mdc` | 始终 | 文献诚信 |
| `literature-workflow.mdc` | `**/*.{md,mdx}` | 文献 Skill/MCP 选用 |
| `karpathy-guidelines.mdc` | 始终 | Karpathy 四原则（编码前思考、简洁优先、精准修改、目标驱动执行） |

## 通用：Claude Code / OpenCode / Trea

使用 **[`universal/AGENTS.md`](universal/AGENTS.md)**（单文件 Markdown，无 Cursor 专属 IDE 条款）。

| 平台 | 建议挂载方式 |
|------|----------------|
| **Claude Code** | 将正文合并进项目根 `CLAUDE.md`，或 `import`/引用 `.agents/rules/universal/AGENTS.md` |
| **OpenCode** | 在 OpenCode 规则设置中指向该文件，或复制到其要求的 rules 目录 |
| **Trea** | 开启 `将AGENTS.md包含在上下文中` 设置选项 |

## 新增或修改规则

1. **Cursor**：在 `cursor/` 下编辑或新增 `.mdc`，再运行 `-InstallRules`。  
2. **通用**：编辑 `universal/DEVELOPMENT-RULES.md`，保持与 `cursor/` 中团队条款一致（Cursor 专属条目只写在 `00-cursor-ide.mdc`）。

`.mdc` 格式说明见 Cursor 文档：`description`、`alwaysApply`、`globs` 字段。
