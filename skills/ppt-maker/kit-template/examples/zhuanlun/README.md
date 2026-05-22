# 转轮项目示例（仅数据）

本目录提供从 `ppt_style` 迁出的 **slides 数据结构示例**，不包含任何业务 PNG。

## 使用步骤

1. 切换数据：

   ```bash
   npm run example:zhuanlun
   ```

2. 将 `slides.js` 中引用的图片文件放入 [`public/assets/materials/`](../../public/assets/materials/)（文件名需与 `images` 数组一致）。

3. 启动预览并导出：

   ```bash
   npm run serve
   ```

## 恢复默认占位

```bash
npm run example:default
```

仅含 `placeholder.png` 即可预览版式。
