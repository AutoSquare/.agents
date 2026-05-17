# 问题跟踪：GitHub

本仓库工单与 PRD 以 GitHub Issue 形式存在。一切操作用 `gh` CLI。

## 约定

- **创建工单**：`gh issue create --title "..." --body "..."`。多行正文用 heredoc。
- **阅读工单**：`gh issue view <number> --comments`，必要时用 `jq` 过滤评论并拉标签。
- **列出工单**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，按需加 `--label`、`--state`。
- **评论**：`gh issue comment <number> --body "..."`
- **增删标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭**：`gh issue close <number> --comment "..."`

从 `git remote -v` 推断仓库 —— 在 clone 目录内运行时 `gh` 会自动解析。

## 当技能要求「发布到问题跟踪」

创建 GitHub 工单。

## 当技能要求「拉取相关工单」

运行 `gh issue view <number> --comments`。
