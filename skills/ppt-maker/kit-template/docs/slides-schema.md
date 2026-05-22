# slides 数据模型

供人工或 Agent 编写 [`src/data/slides.js`](../src/data/slides.js) 时使用。素材须先放入 [`public/assets/materials/`](../public/assets/materials/)，再在 `images` 中写**文件名**（非绝对路径）。

## 顶层

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | number | 是 | 从 1 递增；对应 DOM `#slide-{id}` |
| `sectionLabel` | string | 是 | 页眉分区标签 |
| `sectionIndex` | string | 是 | 页码展示，如 `01` |
| `title` | string | 是 | 主标题 |
| `theme` | string | 是 | 主题副题 |
| `layoutRatio` | string | 否 | `50-50`（默认）、`60-40`、`65-35` |
| `cases` | Case[] | 是 | 长度 1–2，双栏布局 |

## Case（`cases[]` 元素）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `index` | string | 是 | 角标字母，如 `A` |
| `name` | string | 是 | 案例名称 |
| `subtitle` | string | 否 | 副标题 |
| `description` | string | 是 | 正文 |
| `images` | string[] | 是 | 素材文件名列表 |
| `imageFit` | string | 否 | `contain` / `cover` |
| `imageFrameType` | string | 否 | `hud` / `paper` |
| `tags` | string[] | 否 | 底部标签 |
| `metadata` | `{label,value}[]` | 否 | 指标行 |

## 工具函数（`slides.js` 导出）

```js
import { projectConfig } from '../config/project.js'

export const ASSET_BASE = projectConfig.content.assetBase

export function imageUrl(filename) {
  return `${ASSET_BASE}${filename}`
}

export function slideHash(id) {
  return `slide-${id}`
}
```

## 素材约定

- 目录：`public/assets/materials/`
- 默认演示：仅 [`placeholder.png`](../public/assets/materials/placeholder.png)
- 缺失素材时：预览显示占位，可编辑导出会在 `missingImages` 中列出

## 示例切换

```bash
npm run example:default   # 3 页中性占位
npm run example:zhuanlun  # 转轮数据结构（需自备 PNG）
```
