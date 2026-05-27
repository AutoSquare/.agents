# Grill Me — 示例

## A. 结构化工具（Cursor `AskQuestion` 等）

### 顺序 grill — PPT 视觉（**默认 · 每轮 1 题**）

第 1 轮：

```json
{
  "title": "Pitch 视觉 · 第 1/6 轮",
  "questions": [
    {
      "id": "slide_mode",
      "prompt": "Slide 明暗（推荐：hybrid）",
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

第 2 轮起依次：`accent` → `type` → `stage` → `density` → `scope`（ppt-maker 见 EXAMPLES §12）。**每轮单独调用、单独等待。**

### 批量 intake — 仅用户说「一次问完」

Cursor 上 **不用** AskQuestion 多题；改用 Markdown 选票（见 B 节）。Claude Code / 其它宿主若有稳定多题表单，最多 **2–4 题**，仍非默认。

### 顺序 grill — 架构第 1 轮

```json
{
  "title": "范围定稿 · 第 1 轮",
  "questions": [
    {
      "id": "scope",
      "prompt": "本轮交付范围（推荐：mvp）",
      "options": [
        { "id": "mvp", "label": "MVP — 核心路径" },
        { "id": "full", "label": "完整交付" }
      ]
    }
  ]
}
```

### 解析返回（各宿主类似）

```
Question style_direction: Selected option(s) dark_cinematic
Question color_mode: Selected option(s) dark
```

→ 表格复述 → 再实现。

---

## B. Markdown 选票（Claude Code / OpenCode / Trea / 无工具时）

### 批量 intake 示例

```markdown
## 待你定稿 · 转轮 Pitch 视觉

### 1. style_direction — 整体视觉方向（推荐：B）

- **A** · Trust & Authority 学院浅蓝
- **B** · Modern Dark cinematic（推荐：暗场演示、科技感）
- **C** · Swiss 极简网格

### 2. color_mode — 明暗模式（推荐：dark）

- **light** · 浅色，打印/投影友好
- **dark** · 深色，大屏演示

### 3. accent_color — 强调色（推荐：indigo）

- **blue** · #0369A1 工程蓝
- **indigo** · #4F46E5 科技靛
- **teal** · #0D9488 地质青

请回复：`1B, 2dark, 3indigo`（或逐条说明）。
**在你回复前我不会开始改 deck。**
```

### 顺序 grill — 第 1 轮示例

```markdown
## 待你定稿 · 架构 · 第 1/3 轮

### scope — 交付范围（推荐：mvp）

- **mvp** · 仅核心链路，先验证
- **full** · 完整功能一次交付
- **poc** · 只验证可行性，不写生产代码

请回复：`scope=mvp`
**第 1 轮定稿前不进入第 2 轮。**
```

---

## C. 复述共识（通道无关）

定稿后 Agent 输出：

| 维度 | 你的选择 |
|------|----------|
| style_direction | Modern Dark cinematic |
| color_mode | dark |
| accent_color | indigo |

然后才执行后续 skill / 代码变更。
