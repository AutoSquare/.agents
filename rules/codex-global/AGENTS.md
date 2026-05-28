# Codex 全局规则入口

本文件安装到 `$CODEX_HOME/AGENTS.md`，适用于本机所有 Codex 会话。项目或子目录中的 `AGENTS.md` 可以补充更具体规则；若发生冲突，优先级为：系统/开发者消息 > 项目/子目录规则 > 本全局规则。

## 常驻硬约束

- 默认使用中文回复；用户明确要求其他语言时除外。
- 执行代码修改前，先阅读项目开发文档或 `docs/` 目录中的约定。
- 代码变更默认需要同步开发文档；若任务明确无需文档更新，在交付时说明。
- 禁止执行 `git add` / `git commit` / `git push`，除非用户在同一条消息里明确要求提交。
- 不伪造论文、引用、DOI、期刊、作者、检索来源或已读全文状态。
- 使用 skills 时，先读取匹配 skill 的 `SKILL.md`，再按其流程执行。

## 按需读取规则

规则文件位于 `$CODEX_HOME/agent-rules/`。遇到对应任务时，先读取相应文件再执行。

- 通用命名、中文界面、英文路径：`01-language-and-naming.md`
- 代码修改、功能新增、交付文档：`02-doc-linkage-and-delivery.md`
- 开发前读取项目文档：`03-pre-development-requirements.md`
- 写注释、文档、技术说明：`04-comment-and-writing-quality.md`
- 新增模块、分层、重构、架构调整：`05-code-organization-and-architecture.md`
- 代码任务最终交付前检查：`06-pre-submit-checklist.md`
- 创建或修改 Agent Skills：`07-skills-authoring.md`
- C#、WPF、WinUI3、XAML、`.csproj`：`08-csharp-xml-docs.md`
- 用户要求提交说明，或完整任务收尾需要建议提交：`09-git-commit-message.md`
- 编写、审查、重构代码：`10-karpathy-guidelines.md`
- 文献、论文、引用、综述、学术输出：`11-literature-integrity.md`
- 文献检索、全文下载、引用导出、PPT：`12-literature-workflow.md`
- 项目含 `.agents/` 配置包时：`13-agents-entry.md`

## Skills

全局 skills 位于 `$CODEX_HOME/skills/`。当用户点名 skill，或任务明显匹配 skill 描述时，必须读取该 skill 的 `SKILL.md`；多个 skill 同时适用时，选择最小必要组合并说明使用顺序。
