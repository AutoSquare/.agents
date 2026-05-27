# ppt-maker

将素材与结构化数据生成为 Vue 16:9 幻灯片预览，并在浏览器中导出 PPT。

**发布副本**：`.agents/skills/ppt-maker/`（随 `.agents` 分发）  
**本目录**：维护者沙箱（可选；完整 AI 规则仓库保留双树时使用）

---

## 终端用户

1. 安装 `.agents` 配置包后执行：

```powershell
cd .agents
powershell -ExecutionPolicy Bypass -File .\scripts\setup-cursor-agents.ps1
```

2. 重启 Cursor；说「做 PPT」或 `@ppt-maker/SKILL.md`
3. Agent 在 `ppt-projects/{english-slug}/` 创建副本并编写内容
4. 副本内 `npm run serve` 预览，浏览器顶栏导出 PPT

详见 [发布说明.md](发布说明.md)、[SKILL.md](SKILL.md)。

---

## 维护者（沙箱 → .agents）

```text
编辑 ppt-maker/（本目录）
  → node ppt-maker/scripts/sync-to-agents.mjs
  → cd .agents && powershell -File .\scripts\setup-cursor-agents.ps1
```

**禁止**只改 `.agents/skills/ppt-maker/` 而不回写本目录。

### 同步 kit-template（可选）

```powershell
node ppt-maker/scripts/sync-template.mjs
node ppt-maker/scripts/sync-template.mjs --upstream "D:/path/to/ppt-maker-kit"
```

---

## 文档

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | Agent 主流程 |
| [发布说明.md](发布说明.md) | 版本、安装、发布检查清单 |
| [VISUAL.md](VISUAL.md) | 好看因子与 layout 分型 |
| [PREVIEW-CHROME.md](PREVIEW-CHROME.md) | grill-me intake、预览外壳 token |
| [LAYOUT-CRAFT.md](LAYOUT-CRAFT.md) | cover / catalog / dual 工艺 |
| [REFERENCE.md](REFERENCE.md) | layout、反模式、脚本 |
| [EXPORT.md](EXPORT.md) | 可编辑导出三区契约 |
| [ADR-0001-export-core-lock.md](ADR-0001-export-core-lock.md) | 导出红区锁定 |
| [EXAMPLES.md](EXAMPLES.md) | styleBrief、grill-me 题库 |
| [VERIFICATION.md](VERIFICATION.md) | 弱模型回归 R1–R11 |
| [scripts/TOKEN_MAP.md](scripts/TOKEN_MAP.md) | MASTER → token 映射 |

---

## 变更日志

### ppt-maker-kit@0.2.0

- 7 种 layout + CSS export-layer 双 pass 可编辑导出
- scaffold 写入 `export-core.manifest.json`
- `map-design-system.mjs`、`validate-project.mjs`
- grill-me 顺序视觉 intake（6 轮 · AskQuestion 单题）
- PREVIEW-CHROME 预览外壳与 slide 画布分离

旧 0.1.0 副本建议 re-scaffold。
