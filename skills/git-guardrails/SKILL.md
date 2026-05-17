---
name: git-guardrails-claude-code
description: 配置 Claude Code 钩子，在危险 git 命令执行前拦截（push、reset --hard、clean、branch -D 等）。用于用户想阻止破坏性 git 操作、加 git 安全钩或在 Claude Code 里禁止 push/reset。
---

# Setup Git Guardrails（Git 护栏）

配置 PreToolUse 钩子：在 Claude 执行前拦截并阻止危险 git 命令。

## 会拦截的内容

- `git push`（含 `--force` 等变体）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

被拦时 Claude 会看到提示：无权使用这些命令。

## 步骤

### 1. 确认范围

问用户：**仅本项目**（`.cursor/hooks.json`）还是 **所有项目**（`~/.cursor/hooks.json`）？

### 2. 复制钩子脚本

捆绑脚本位置：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

按范围复制：

- **项目**：`.claude/hooks/block-dangerous-git.sh`
- **全局**：`~/.claude/hooks/block-dangerous-git.sh`

`chmod +x` 赋可执行。

### 3. 写入 settings

加入对应配置文件：

**项目**（`.cursor/hooks.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**全局**（`~/.cursor/hooks.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

若 settings 已存在，把钩子 **合并进**既有 `hooks.PreToolUse` 数组 —— 勿覆盖其它设置。

### 4. 定制

询问是否要在拦截列表增减模式；按需编辑已复制脚本。

### 5. 验证

快速测：

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

应退出码 2，stderr 打印 BLOCKED 信息。

## Cursor

Adapted from git-guardrails-claude-code. Use Cursor hooks (beforeShellExecution), not .claude/settings.json.
See: ~/.cursor/skills/adapt-mattpocock-skills-for-cursor/CURSOR-GIT-GUARDRAILS.md
