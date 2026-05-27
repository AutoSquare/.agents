/**
 * 前景内容块选择器对照表（可编辑导出须在模板标 export-layer-fg）。
 * 实现见 layerCaptureBrowser.assertExportLayerCoverage。
 */
export const LAYER_SELECTOR = [
  '.slide-frame__header',
  '.slide-frame__footer',
  '.cover-kicker',
  '.cover-partner',
  '.cover-logo-wrap',
  '.cover-title',
  '.cover-desc',
  '.meta-item',
  '.catalog-header',
  '.catalog-item',
  '.preview-card',
  '.preview-hub',
  '.features-header',
  '.features-title',
  '.features-subtitle',
  '.feature-card',
  '.duo-flow-card',
  '.duo-flow-hub',
  '.flow-bar',
  '.features-callout',
  '.stat-chip',
  '.pill-badge',
  '.split-title',
  '.split-subtitle',
  '.split-content',
  '.split-badges',
  '.split-callout',
  '.media-container',
  '.statement-title',
  '.statement-desc',
  '.statement-tags',
  '.agent-core',
  '.agent-node',
  '.brand-collab',
  '.feature-item',
  '.statement-brand-panel',
  '.evidence-heading',
  '.evidence-stat',
  '.evidence-table',
  '.evidence-doc',
  '.evidence-caption',
  '.slide-frame__canvas li',
].join(',')

/** 16:9 PPT 尺寸（英寸） */
export const SLIDE_W = 10
export const SLIDE_H = 5.625

/**
 * 将 DOM 矩形映射为 PPT 坐标（英寸）。
 * @param {{ left: number, top: number, width: number, height: number }} canvasRect
 * @param {{ left: number, top: number, width: number, height: number }} rect
 */
export function mapRectToSlide(canvasRect, rect) {
  return {
    x: ((rect.left - canvasRect.left) / canvasRect.width) * SLIDE_W,
    y: ((rect.top - canvasRect.top) / canvasRect.height) * SLIDE_H,
    w: (rect.width / canvasRect.width) * SLIDE_W,
    h: (rect.height / canvasRect.height) * SLIDE_H,
  }
}
