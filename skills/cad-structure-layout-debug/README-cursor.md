# CAD Structure Layout Debug — Cursor 使用说明

## 安装

在 `.agents` 目录执行：

```powershell
cd D:\你的项目路径\.agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
```

安装后重启 Cursor。Skill 位于：

```text
%USERPROFILE%\.cursor\skills\cad-structure-layout-debug\
```

在对话中使用 `@cad-structure-layout-debug`，或让 Agent 按 description 自动选用。

## 与其他 Skill 分工

| Skill | 职责 |
|-------|------|
| `cad-structure-layout-debug`（本 Skill） | CAD 出图、DXF 排版、布局引擎、预览与外部 CAD 一致性、通用烟测 |
| 项目内 backend-debug Skill（`.cursor/skills/`） | 工程文件后端计算、内力/配筋调试 |

## 推荐阅读顺序

1. `SKILL.md` — Triage 与 Debug Workflow
2. `references/layout-case-studies.md` — 匿名案例（快速对齐问题域）
3. 按问题读 `layout-engine.md` / `viewer-integration.md` / `anti-patterns.md`
4. 从零搭建时读 `cad-system-architecture.md`

## Python 依赖

验证脚本需要 Python 3.10+ 与以下包：

```powershell
pip install -r "%USERPROFILE%\.cursor\skills\cad-structure-layout-debug\requirements.txt"
```

或手动安装：`ezdxf`、`matplotlib`、`pillow`。

## 通用验证命令

```powershell
$skill = "$env:USERPROFILE\.cursor\skills\cad-structure-layout-debug"

py -3.10 "$skill\examples\minimal_engineering_drawing\generate.py" --out "$skill\out\minimal.dxf"
py -3.10 "$skill\scripts\dxf_smoke_check.py" --dxf "$skill\out\minimal.dxf" --min-entities 10
py -3.10 "$skill\scripts\render_dxf_preview.py" --dxf "$skill\out\minimal.dxf" --png "$skill\out\minimal.png"
```

## 维护者工作流

编辑源在工作区根目录 `cad-structure-layout-debug/`（非 `.agents/skills/` 手改）：

```powershell
# 1. 编辑 cad-structure-layout-debug/ 下的 SKILL.md、references、scripts 等
# 2. 同步到 .agents 发布副本
powershell -ExecutionPolicy Bypass -File "cad-structure-layout-debug\scripts\sync-to-agents.ps1"

# 3. 安装到 Cursor（及可选 Codex）
cd .agents
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1"
```

## Codex

`agents/openai.yaml` 仅供 Codex 宿主；Cursor 忽略该文件。Codex 安装路径为 `%USERPROFILE%\.codex\skills\cad-structure-layout-debug\`。
