# ppt-maker-kit

通用 **PPT 制作套件**：用结构化数据在浏览器中预览 16:9 幻灯片，并导出可编辑 PPTX、像素级 PPTX 或 PNG ZIP。

**不包含任何业务素材**；请将图片放入 `public/assets/materials/` 后编辑 `src/data/slides.js`。

## 快速开始

```bash
npm install
npm run serve
```

浏览器打开后使用顶栏三种导出。默认使用 3 页占位数据 + `placeholder.png`。

## 命令

| 命令 | 说明 |
|------|------|
| `npm run serve` | 开发预览 |
| `npm run build` | 生产构建 |
| `npm run export:pptx` | 无浏览器 CLI 导出可编辑 PPTX → `output/` |
| `npm run example:default` | 恢复默认占位 slides |
| `npm run example:zhuanlun` | 切换转轮示例 slides（需自备 PNG） |

## 配置

[`src/config/project.js`](src/config/project.js) — 标题、导出文件名、PPTX 元数据。

## 文档

- [`docs/开发文档.md`](docs/开发文档.md) — 架构与导出管线
- [`docs/slides-schema.md`](docs/slides-schema.md) — slides 数据模型（供 Agent 生成内容）

## 与 ppt_style 的关系

[`ppt_style`](../ppt_style/) 为转轮专用实例，本仓库由其复制并通用化；**不修改** `ppt_style`。
