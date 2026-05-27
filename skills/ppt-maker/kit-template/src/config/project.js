/**
 * PPT 制作套件项目配置：页眉文案、导出文件名与 PPTX 元数据。
 */
export const projectConfig = {
  appTitle: 'PPT 制作预览',
  appSubtitle: 'PPT MAKER PREVIEW',
  appDesc: '16:9 幻灯片预览与导出',
  footerText: 'PPT 制作套件',
  footerLeftText: 'PPT MAKER PREVIEW',
  sectionBadge: 'PITCH DECK',
  previewBaseWidth: 1024,
  exports: {
    editableFileName: 'ppt-editable.pptx',
    editableZipFileName: 'ppt-editable-layers.zip',
    rasterFileName: 'ppt-raster.pptx',
    zipFileName: 'ppt-slides.zip',
    pptxTitle: 'PPT Export',
    rasterPptxTitle: 'PPT Raster Export',
    pptxAuthor: 'ppt-maker-kit',
    pptxFooterLine: 'PPT 制作套件 · 可编辑导出',
  },
  content: {
    assetBase: '/assets/materials/',
  },
}
