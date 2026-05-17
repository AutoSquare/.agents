# 问题跟踪：GitLab

本仓库工单与 PRD 以 GitLab Issue 形式存在。一切操作用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI。

## 约定

- **创建工单**：`glab issue create --title "..." --description "..."`。多行描述用 heredoc；也可用 `--description -` 开编辑器。
- **阅读工单**：`glab issue view <number> --comments`。加 `-F json` 可获得机器可读输出。
- **列出工单**：`glab issue list -F json`，按需加 `--label`。
- **评论**：`glab issue note <number> --message "..."`。GitLab 称评论为「notes」。
- **增删标签**：`glab issue update <number> --label "..."` / `--unlabel "..."`。多标签可逗号分隔或重复该 flag。
- **关闭**：`glab issue close <number>`。`glab issue close` 不接受收束评论，需先用 `glab issue note <number> --message "..."` 写说明再关。
- **合并请求**：GitLab 的 PR 称为 merge request。使用 `glab mr create`、`glab mr view`、`glab mr note` 等 —— 与 `gh pr ...` 同形，把 `pr` 换 `mr`，`comment`/`--body` 换 `note`/`--message`。

从 `git remote -v` 推断仓库 —— 在 clone 目录内运行时 `glab` 会自动解析。

## 当技能要求「发布到问题跟踪」

创建 GitLab 工单。

## 当技能要求「拉取相关工单」

运行 `glab issue view <number> --comments`。
