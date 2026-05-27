# ADR-0001：ppt-maker 可编辑导出红区锁定

## 状态

已接受（2026-05-27）

## 背景

可编辑导出演进中，多次因改动基础框架导致「预览正常、导出失败」。终态为 CSS `export-layer-fg/bg` 显式分层 + `html-to-image` 双 pass，禁止回退 Playwright 或 JS visibility 管线。

## 决策

1. **终态架构**须完整保留于 `kit-template/`，不得降级为单 pass 或 Playwright 路径。
2. **红区文件**（导出引擎）对 Agent **只读**：
   - `editableLayerPipeline.js`
   - `layerCaptureBrowser.js`
   - `captureSlideLayers.js`
   - `exportEditableImages.js`
   - `export-capture.css`（双 pass 规则段）
   - `exportPptx.js`（两层组装）
   - `captureSlides.js`（export 相关段落）
3. **validate-project.mjs** 默认校验 `export-core.manifest.json` checksum；红区被改则 fail。
4. **导出问题**处理顺序：黄区补 `export-layer` 打标 → 对照 [EXPORT.md](EXPORT.md) 验收矩阵 → 仍失败则上报，**不**擅自改红区。
5. **绿区**（slides、tokens）与 **黄区**（layout、打标）不受 checksum 约束。

## 后果

- Agent 须读 [EXPORT.md](EXPORT.md) 三区契约。
- 新增 layout 时只在黄区添加 `export-layer-fg/bg` 打标。
- 维护者演进红区时须 bump `templateVersion` 并 regenerate manifest。
