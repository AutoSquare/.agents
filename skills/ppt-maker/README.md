# ppt-maker（开发沙箱）

将素材与结构化数据生成为 Vue 幻灯片预览，并在浏览器中导出 PPT。

## 使用方式（终端用户）

1. 在项目根执行 `.agents/scripts/setup-cursor-agents.ps1 -OverwriteSkills`
2. 重启 Cursor；说「做 PPT」或 `@ppt-maker/SKILL.md`
3. Agent 在 `ppt-projects/{english-slug}/` 创建副本并编写内容
4. 副本内 `npm run serve` 预览，浏览器顶栏导出 PPT

## 维护者流程（唯一编辑源）

```text
编辑 ppt-maker/（本目录，沙箱）
  → node ppt-maker/scripts/sync-to-agents.mjs
  → powershell -File .\.agents\scripts\setup-cursor-agents.ps1 -OverwriteSkills
  → （可选）e2e 冒烟
```

**禁止**直接手改 `.agents/skills/ppt-maker/` 而不回写沙箱。

### 同步 kit-template（可选）

```bash
node ppt-maker/scripts/sync-template.mjs
node ppt-maker/scripts/sync-template.mjs --upstream "D:/path/to/ppt-maker-kit"
```

## 文档

- [SKILL.md](SKILL.md) — Agent 主流程
- [REFERENCE.md](REFERENCE.md) — 命令与故障排除
