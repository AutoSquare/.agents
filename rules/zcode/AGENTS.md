# ZCode 全局规则入口

本文件由 `<配置包根目录>/scripts/setup-zcode-agents.ps1` 安装到 `~/.zcode/AGENTS.md`（默认 `%USERPROFILE%\.zcode\AGENTS.md`）的托管块，适用于本机所有 ZCode 会话。工作区 `AGENTS.md` 在其后加载，可收窄或覆盖本文件；冲突时优先级为：系统/开发者消息 > 直接用户指令 > 工作区规则 > 本文件。

## 常驻硬约束

- 默认使用中文回复；用户明确要求其他语言时除外。
- 执行代码修改前，先阅读项目开发文档或 `docs/` 目录中的约定。
- 代码变更默认需要同步开发文档；若任务明确无需文档更新，在交付时说明。
- 禁止执行 `git add` / `git commit` / `git push`，除非用户在同一条消息里明确要求提交。
- 不伪造论文、引用、DOI、期刊、作者、检索来源或已读全文状态。
- 使用 skills 时，先读取匹配 skill 的 `SKILL.md`，再按其流程执行；已有 `<skill_content>` 时不要重复加载。
- 计划模式下只做只读探索，不写文件、不改配置；计划经 `ExitPlanMode` 批准后才实施。
- 工具调用被权限拒绝时不原样重试；向用户报告被拒的具体操作与路径。
- 不得声称未实际运行的验证已通过；遵循 `verification-before-completion`。

## 按需读取规则

规则文件位于 `~/.zcode/rules/`（默认 `%USERPROFILE%\.zcode\rules\`）。遇到对应任务时，先读取相应文件再执行。

- 命名、中文界面、英文路径：`01-language-and-naming.md`
- 代码修改、功能新增、交付文档：`02-doc-linkage-and-delivery.md`
- 开发前读取项目文档：`03-pre-development-requirements.md`
- 注释、文档、技术说明：`04-comment-and-writing-quality.md`
- 新增模块、分层、重构、架构调整：`05-code-organization-and-architecture.md`
- 交付前检查：`06-pre-submit-checklist.md`
- 创建或修改 Agent Skills：`07-skills-authoring.md`
- C#、WPF、WinUI3、XAML、`.csproj`：`08-csharp-xml-docs.md`
- 提交说明与手动提交：`09-git-commit-message.md`
- 编写、审查、重构代码：`10-karpathy-guidelines.md`
- 文献、引用、综述、学术输出：`11-literature-integrity.md`
- 文献检索、全文下载、引用导出、PPT：`12-literature-workflow.md`
- 项目含智能体配置包（目录名任意）：`13-agents-entry.md`
- ZCode 工具映射、模式、技能发现、MCP 与子代理：`14-zcode-host.md`

## Skills

ZCode 技能发现顺序（前者优先，同名遮蔽后者）：显式配置根 → `~/.zcode/skills/` → `~/.agents/skills/` → 工作区 `.zcode/skills/` → 工作区 `.agents/skills/` → 插件。用户点名技能或任务匹配 description 时用 `Skill` 工具加载；用户以 `/name` 显式调用时按其注入内容执行。frontmatter 中的 `disable-model-invocation` 是 DSH 专属键，ZCode 不识别——带 description 的技能既可被模型调用，也可由用户 `/name` 调用。

技能正文中的脚本路径以加载结果给出的资源基目录为准；若正文硬编码 `%USERPROFILE%\.cursor\skills\` 而该路径不存在，改用 `%USERPROFILE%\.zcode\skills\`。

## MCP

MCP 工具在 ZCode 中名为 `mcp__<server>__<tool>`；不要臆测未出现在工具列表中的名称。调用 `campus-net` 的下载类工具前先 `get_active_profile`；凭据只从系统环境变量或 `~/.zcode/campus-net/local.env` 读取，不回显明文。
