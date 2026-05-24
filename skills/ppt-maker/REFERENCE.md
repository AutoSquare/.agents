# ppt-maker 参考

## 目录

| 路径 | 说明 |
|------|------|
| `ppt-maker/SKILL.md` | Agent 主流程（沙箱编辑源） |
| `.agents/skills/ppt-maker/` | 发布副本（由 sync-to-agents 生成） |
| `%USERPROFILE%\.cursor\skills\ppt-maker\` | 安装后运行时路径 |
| `ppt-maker/kit-template/` | 只读模板（勿改） |
| `ppt-maker/scripts/` | 脚手架与检测脚本 |
| `ppt-projects/{slug}/` | 用户单次任务副本 |
| `ppt-maker-kit/` 或 `ppt_style/` | 模板同步源（维护者用） |

## 安装

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
```

## 脚本

```bash
# 维护：沙箱 → .agents 发布副本
node ppt-maker/scripts/sync-to-agents.mjs
node ppt-maker/scripts/sync-to-agents.mjs --dry-run

# 维护：从 ppt-maker-kit（或 ppt_style）刷新 kit-template
node ppt-maker/scripts/sync-template.mjs
node ppt-maker/scripts/sync-template.mjs --upstream "D:/path/to/ppt-maker-kit"

# 生成 slug
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\slug.mjs" --generate

# 检测 Node（JSON 输出）
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\check-node.mjs"
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\check-node.mjs" --install

# 创建项目副本
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\scaffold.mjs" --slug deck-20260521-2030 --workspace "D:/path/to/workspace"
node "$env:USERPROFILE\.cursor\skills\ppt-maker\scripts\scaffold.mjs" --slug deck-test --workspace "." --force --style-brief "科技产品发布，深色霓虹"
```

沙箱调试时将上述 `$env:USERPROFILE\.cursor\skills\ppt-maker` 换为 `ppt-maker`。

## slug 规则

- 仅 `a-z0-9-`，小写，1–48 字符
- 不得以连字符开头/结尾
- 中文项目名 → 转英文 slug 或使用 `deck-YYYYMMDD-HHmm`

## `.ppt-maker-project.json` 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `slug` | string | 英文项目目录名 |
| `workspace` | string | 工作区绝对路径 |
| `createdAt` | string | ISO 时间 |
| `templateVersion` | string | 模板版本（如 `ppt-maker-kit@0.1.0`） |
| `styleBrief` | string? | 用户风格描述 |
| `designSystemQuery` | string? | 传入 `search.py` 的英文检索词 |

## 路径与中文

- **文件夹**必须英文：`ppt-projects/my-deck/`
- **文案**可中文：`project.js`、`slides.js`
- 若 `npm install` / `serve` 因路径报错，将 `--workspace` 指到纯英文目录

## 预览与端口

- 脚手架在副本 `vue.config.js` 注入 `devServer: { port: 8080, host: 'localhost' }`
- 8080 被占用时可能改用 8081+；以终端 `App running at` 为准

## 导出

| 方式 | 需要 | Skill 默认 |
|------|------|------------|
| 浏览器三导出 | `npm run serve` + 用户点击 | 不代点 |
| `npm run export:pptx` | 副本内 Node + 素材文件 | 不执行 |

## ui-ux-pro-max（风格定制）

执行 Agent 须在对话中调用 **`/ui-ux-pro-max`**。

| 项 | 说明 |
|----|------|
| Skill 路径 | `~/.cursor/skills/ui-ux-pro-max/SKILL.md` |
| 检索脚本 | `~/.cursor/skills/ui-ux-pro-max/scripts/search.py` |
| 依赖 | Python 3 |
| 工作目录 | `ppt-projects/<slug>/` |
| 落地文件 | `design-system/MASTER.md`、`src/styles/design-tokens.css` |

### 推荐命令（Windows，在副本目录执行）

```powershell
cd ppt-projects/<slug>
python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py" "<英文检索词>" --design-system --persist -p "<slug>" -f markdown
```

## 故障排除

| 现象 | 处理 |
|------|------|
| 未找到 kit-template | 重新运行 setup-cursor-agents；或维护者 sync-to-agents |
| scaffold 目标已存在 | 换 slug 或 `--force` |
| 导出缺图 | 预览中滚动加载各页后再导出 |
| 素材缺失 | 检查 `materials/` 文件名与 `slides.js` 的 `images` 一致 |
| Node 安装后仍找不到 | 重开终端后再 `npm install` |
| `search.py` 报错 | 检查 Python；换英文检索词 |
| 风格与描述不符 | 确认已调用 ui-ux-pro-max 且已改 `design-tokens.css` |
