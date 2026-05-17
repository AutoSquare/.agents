# Git 护栏（Cursor 版）

对应上游 `git-guardrails-claude-code`，使用 Cursor **用户级** hooks。

## 范围

问用户：**仅当前项目**（`.cursor/hooks.json`）还是 **所有项目**（`~/.cursor/hooks.json`）。

## 拦截的命令

与上游一致：

- `git push`（含 `--force`）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

## 实现步骤

1. 创建 `hooks/block-dangerous-git.js`（或 `.sh`），在 `beforeShellExecution` 中读取 JSON stdin，检查 `command` 字段是否匹配上述模式；匹配则返回 `permission: "deny"` 与说明信息。
2. 在对应 `hooks.json` 注册：

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      {
        "command": "./hooks/block-dangerous-git.js"
      }
    ]
  }
}
```

3. 项目级：路径相对于项目根 `.cursor/hooks/`。用户级：相对于 `~/.cursor/hooks/`。

详细 hooks 格式见 Cursor **create-hook** 内置技能。

## 与 Claude 版的差异

- 不用 `PreToolUse` 或 `$CLAUDE_PROJECT_DIR`
- 不用 `.claude/settings.json`
- 失败策略建议 **fail closed**（无法解析命令时拒绝执行）
