# Grill Me — 宿主通道适配

本 skill 的 **行为与完成标准全宿主一致**；仅「如何把选项呈现给用户」随宿主变化。

## 能力探测（Agent 第一步）

在开始 questionnaire 前，快速判断：

1. 工具列表里是否有 **多选 / 表单 / 向用户提问** 类工具？（名称因宿主而异）
2. 若有 → 走 **通道 1**；若无 → 走 **通道 2（Markdown 选票）**

**不要**假设「只有 Cursor 才有结构化工具」；**也不要**假设「只有 Cursor 才需要结构化工具」——无工具时选票协议与工具 **同等 mandatory**。

---

## 通道对照表

| 宿主 | 结构化选题（通道 1） | 无工具时（通道 2） | 备注 |
|------|---------------------|-------------------|------|
| **Cursor**（Agent / Plan） | `AskQuestion` | Markdown 选票 | Plan 与 Agent 均可用 AskQuestion；有工具时 **禁止**纯文本代问 |
| **Claude Code** | 若会话提供 AskUser / 类似表单工具则用；否则 | Markdown 选票 | 不依赖 `/slash`；通过 `@grill-me` 或 description 触发 |
| **OpenCode** | 以当前会话 **实际注册工具** 为准 | Markdown 选票 | 默认走选票；若后续接入表单 MCP 则升通道 1 |
| **Trea** | 以 Trea Agent **实际工具面** 为准 | Markdown 选票 | 与 Cursor 类似时可能是表单类工具；无则选票 |

> 上表随宿主演进可增补行；**SKILL.md 的硬约束不变**。

---

## Cursor — `AskQuestion`（通道 1）

工具名：`AskQuestion`（非 MCP；Cursor 内置）。

### 默认：顺序 grill（每次 1 题）

**`questions` 数组长度必须为 1。** 多轮视觉 / 架构定稿均按此执行（含 ppt-maker §0.5）。

```json
{
  "title": "Pitch 视觉 · 第 1/6 轮",
  "questions": [
    {
      "id": "slide_mode",
      "prompt": "Slide 整体明暗（推荐：hybrid）",
      "options": [
        { "id": "light_saas", "label": "全浅色 SaaS" },
        { "id": "dark_full", "label": "全深色 cinematic" },
        { "id": "hybrid", "label": "浅预览 + dark slide" }
      ],
      "allow_multiple": false
    }
  ]
}
```

收答后 **停止等待** → 再发第 2 轮（accent）→ … → 全部维度闭合 → **一次** 表格复述共识 → 实现。

返回块通常含 `Question <id>: Selected option(s) <value>`。

### 批量 intake（仅用户明确要求）

- Cursor **禁止**用 AskQuestion 一次传 2 题及以上（实测易 `Invalid arguments: questions: Required` 或 UI 空题干）。
- 用户说「一次问完」→ 用 **Markdown 选票** 列出 2–4 题（仍须停止等待），**不要**强行 AskQuestion 多题。

### 故障排除

| 现象 | 处理 |
|------|------|
| `Invalid arguments: questions: Required` | 参数未传到工具；**拆成单题**重试 AskQuestion |
| 多题 UI 显示「空的问题」 | 题数过多；改 **顺序 grill** |
| 单题仍失败 | 该轮改 **Markdown 选票（1 题）** + 停止 |
| 用户已用选票回复 | 视为有效选择，勿重复 AskQuestion |

**prompt 建议**：单题 `prompt` 控制在 **120 字以内**；色值、长说明放 `label`，避免编码层截断。

---

## Claude Code

- 技能安装路径通常为 `~/.claude/skills/` 或项目 `.claude/skills/`（与 Cursor 的 `.cursor/skills/` 独立，**内容应相同**）。
- 无专用表单工具时：**必须** Markdown 选票 + 停止，行为与 Cursor 无 AskQuestion 时一致。
- 危险操作、git 等仍遵循各宿主自己的安全规则；grill-me **只负责决策 intake**。

---

## OpenCode

- 默认 **Markdown 选票**。
- 若 OpenCode 会话挂载了用户自定义「提问 / 选择」MCP，视为通道 1，优先使用。
- 选票回复格式建议支持：`1B, 2A` 与 `key=value` 两种，便于脚本化用户。

---

## Trea

- Trea Agent 工具名可能与 Cursor 不同；以 **当前会话工具 schema** 为准，不硬编码工具名。
- 探测到表单类工具 → 通道 1；否则 → Markdown 选票（与 OpenCode 相同）。
- Trea 调试 / 交接文档中的「待用户确认」项，应用本 skill 统一为选票或结构化工具，避免 Agent 自说自话定稿。

---

## 同步与发布

- **源文件**：仓库 `.agents/skills/grill-me/`（跨 Agent 真相源）
- **Cursor 副本**：`~/.cursor/skills/grill-me/`
- **Claude Code 副本**：`~/.claude/skills/grill-me/`（若使用）
- 修改 skill 时 **各宿主副本应保持一致**；禁止只改 Cursor 版导致 Trea / OpenCode 仍读旧「一次一问纯文本」。

---

## 版本原则

| 保留（Matt Pocock 原意） | 扩展（跨宿主） |
|--------------------------|----------------|
| 拷问直到共识 | 结构化工具 **或** Markdown 选票 |
| 每题推荐答案 | 批量 intake / 顺序 grill 两模式 |
| 能探索就不问 | PLATFORMS 通道表 |
| — | 全宿主「等待 + 复述」硬约束 |
