# MASTER.md → design-tokens.css 映射规格

`map-design-system.mjs` 从 `design-system/<slug>/MASTER.md`（ui-ux-pro-max 产出）提取下列变量并写入 `src/styles/design-tokens.css`。

## 颜色（Color Palette 表格）

| MASTER `CSS Variable` | design-tokens.css | 必填 |
|----------------------|-------------------|------|
| `--color-primary` | `--color-primary` | 是 |
| `--color-on-primary` | `--color-on-primary` | 否 |
| `--color-secondary` | `--color-secondary` | 是 |
| `--color-accent` | `--color-accent` | 是 |
| `--color-background` | `--color-background` | 是 |
| `--color-foreground` | `--color-foreground` | 是 |
| `--color-border` | `--color-border` | 否 |
| `--color-muted` | `--color-muted-text` | 否 |

派生（脚本自动计算，不读 MASTER）：

- `--color-primary-soft`：primary 略浅
- `--color-accent-light`：background 略深
- `--color-accent-warm`：等于 `--color-accent`（覆盖 Editorial 默认 `#C2410C`）
- `--color-surface` / `--color-canvas` / `--color-border-light`：由 background/border 推导

## 字体（Typography + CSS Import）

1. 提取 ` ```css ` 代码块中的 `@import url(...)` 替换文件首行 `@import`
2. `--font-heading`：Heading Font 名称 + 后备 serif
3. `--font-body`：Body Font 名称 + 后备 sans-serif

若 MASTER 无 Google Fonts 链接，保留 kit 默认并仅更新色值。

## 失败条件

- 找不到 MASTER.md
- 必填色值缺失
- 解析后 `--color-accent-warm` 仍为 `#C2410C` 且 `--color-background` 仍为 `#FCFBF9`（视为未定制）

## 逃生口

仅当用户明确确认且脚本失败时，Agent 可临时手改 `design-tokens.css`，并在 `.ppt-maker-project.json` 写入 `"tokenMapDebt": true`。
