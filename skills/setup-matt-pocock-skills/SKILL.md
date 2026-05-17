---
name: setup-matt-pocock-skills
description: 在 AGENTS.md / CLAUDE.md 写入 `## Agent skills` 块，并创建 `docs/agents/`，以便工程技能了解本仓库的问题跟踪（GitHub 或本地 Markdown）、分拣标签词典与领域文档布局。在首次使用 `to-issues`、`to-prd`、`triage`、`diagnose`、`tdd`、`improve-codebase-architecture` 或 `zoom-out` 前运行 —— 或当这些技能似乎缺少跟踪系统 / 分拣标签 / 领域文档上下文时运行。
disable-model-invocation: true
---

# Setup Matt Pocock Skills（脚手架）

搭建工程技能所假定的仓库级配置：

- **问题跟踪（Issue tracker）** —— 工单所在位置（默认 GitHub；亦原生支持本地 Markdown）
- **分拣标签** —— 五个规范分拣角色对应的实际字符串
- **领域文档** —— `CONTEXT.md` 与 ADR 的布局，以及阅读它们的消费规则

这是 **提示驱动** 的技能，不是确定性脚本。先探索、展示发现、与用户确认，再写入。

## 流程

### 1. 探索

查看仓库现状，阅读已有文件；勿想当然：

- `git remote -v` 与 `.git/config` —— 是否为 GitHub 仓库？具体哪一个？
- 根目录 `AGENTS.md` 与 `CLAUDE.md` —— 是否存在？是否已有 `## Agent skills` 小节？
- 根目录 `CONTEXT.md`、`CONTEXT-MAP.md`
- `docs/adr/` 以及任意 `src/*/docs/adr/`
- `docs/agents/` —— 本技能先前是否已产出
- `.scratch/` —— 是否已在使用本地 Markdown 工单惯例

### 2. 展示并提问

汇总已有 / 缺失项。然后 **逐条** 带用户走完三项决策 —— 每次只展示一节，拿到答案再继续，不要三件事一把丢出。

假定用户不熟这些术语：每节前附短说明（是什么、为何技能需要、选不同会怎样），再给选项与默认。

**小节 A —— 问题跟踪。**

> 说明：「问题跟踪」指本仓库工单存放何处。`to-issues`、`triage`、`to-prd`、`qa` 等技能会读写它 —— 需要知道该调用 `gh issue create`、在 `.scratch/` 下写 Markdown，还是你描述的其它流程。请选择你 **实际** 跟踪工作的位置。

默认策略：技能面向 GitHub 设计。若 `git remote` 指向 GitHub，建议 GitHub。若指向 GitLab（`gitlab.com` 或自建 host），建议 GitLab。否则（或用户偏好）可提供：

- **GitHub** —— 工单在仓库的 GitHub Issues（用 `gh` CLI）
- **GitLab** —— 工单在 GitLab Issues（用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI）
- **Local markdown** —— 工单为 `.scratch/<feature>/` 下文件（适合个人项目或无 remote 仓库）
- **Other**（Jira、Linear 等）—— 请用户用一段话描述流程；技能将其记录为自由文本

**小节 B —— 分拣标签词典。**

> 说明：`triage` 技能处理新进工单时在状态机中移动它们 —— 待评估、等报告者、可供 AFK 智能体认领、需人类实现、或不修。为此需应用与你的跟踪系统 **真实配置相符** 的标签（或等价物）。若仓库已用不同名称（例如 `bug:triage` 而非 `needs-triage`），在此映射，避免技能再打重复标签。

五个规范角色：

- `needs-triage` —— 维护者需评估
- `needs-info` —— 等报告者
- `ready-for-agent` —— 规格齐备，AFK 可领（无需人类临场语境）
- `ready-for-human` —— 需人类实现
- `wontfix` —— 不予处理

默认：每角色的字符串与其角色名相同。询问是否覆盖。若跟踪系统尚无标签，默认通常可用。

**小节 C —— 领域文档。**

> 说明：若干技能（`improve-codebase-architecture`、`diagnose`、`tdd`）会读 `CONTEXT.md` 学领域用语，读 `docs/adr/` 看历史架构决策。需确认仓库是 **单一全局语境** 还是 **多语境**（例如 mono 仓库前后端拆分），以便查对位置。

确认布局：

- **Single-context** —— 根目录一个 `CONTEXT.md` + `docs/adr/`。多数仓库如此。
- **Multi-context** —— 根 `CONTEXT-MAP.md` 指向各语境的 `CONTEXT.md`（常为 monorepo）。

### 3. 确认与编辑

向用户展示草案：

- 将写入 `CLAUDE.md` / `AGENTS.md`（择一，规则见下一步）的 `## Agent skills` 块
- `docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/agents/domain.md` 的内容

先让用户改满意再落盘。

### 4. 写入

**选择编辑哪个文件：**

- 若存在 `CLAUDE.md`，编辑它。
- 否则若存在 `AGENTS.md`，编辑它。
- 若两者皆无，问用户新建哪一个 —— **勿代选**。

当 `CLAUDE.md` 已存在时切勿再建 `AGENTS.md`（反之亦然），只编辑已有的那个。

若所选文件已有 `## Agent skills` 块，**就地更新**，勿追加重复块。勿覆盖用户对周围自定义内容的编辑。

块内容形如：

```markdown
## Agent skills

### Issue tracker

[单行摘要：工单跟踪于何处]。详见 `docs/agents/issue-tracker.md`。

### Triage labels

[单行摘要：标签用语]。详见 `docs/agents/triage-labels.md`。

### Domain docs

[单行摘要：布局 —— "single-context" 或 "multi-context"]。详见 `docs/agents/domain.md`。
```

再以本技能文件夹中的种子模板为基础写出三个文档：

- [issue-tracker-github.md](./issue-tracker-github.md) —— GitHub
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md) —— GitLab
- [issue-tracker-local.md](./issue-tracker-local.md) —— 本地 Markdown
- [triage-labels.md](./triage-labels.md) —— 标签映射
- [domain.md](./domain.md) —— 领域文档消费规则与布局

对「Other」跟踪系统，依据用户描述从头写 `docs/agents/issue-tracker.md`。

### 5. 完成

告知 setup 已完成，并说明哪些工程技能会读取这些文件。提醒用户可直接编辑 `docs/agents/*.md`；仅当切换跟踪系统或想从零重做时才需重跑本技能。
