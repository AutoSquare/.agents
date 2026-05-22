import { projectConfig } from '../config/project.js'
import { DEFAULT_CAPTURE_PRESET } from './capturePresets.js'
import { loadPptxGenJS, SLIDE_H, SLIDE_W } from './pptxLoader.js'
import { renderStoryboardSlides } from './slideRasterPipeline.js'

/** 像素级导出默认文件名 */
export const EXPORT_RASTER_FILE_NAME = projectConfig.exports.rasterFileName

/**
 * 将 PNG data URL 列表写入 16:9 全幅图片幻灯片。
 * @param {string[]} pngDataUrls 与 slides 顺序一致的 PNG data URL
 * @returns {Promise<import('pptxgenjs').default>}
 */
export async function buildRasterPptx(pngDataUrls) {
  const PptxGenJS = await loadPptxGenJS()
  const pptx = new PptxGenJS()
  pptx.layout = 'LAYOUT_16x9'
  pptx.author = projectConfig.exports.pptxAuthor
  pptx.title = projectConfig.exports.rasterPptxTitle

  pngDataUrls.forEach((dataUrl) => {
    const slide = pptx.addSlide()
    slide.addImage({
      data: dataUrl,
      x: 0,
      y: 0,
      w: SLIDE_W,
      h: SLIDE_H,
    })
  })

  return pptx
}

/**
 * 浏览器一键导出像素级 PPT：离屏渲染后整页贴图。
 * @param {Array<{ id: number }>} slidesData
 * @param {{ gridState: { active: boolean } }} envCtx App 提供的 gridState
 * @param {{ capturePreset?: string, onProgress?: (current: number, total: number, phase: string) => void }} [options]
 * @returns {Promise<void>}
 */
export async function exportStoryboardToRasterPptx(slidesData, envCtx, options = {}) {
  const { capturePreset = DEFAULT_CAPTURE_PRESET, onProgress } = options
  const pngDataUrls = await renderStoryboardSlides(slidesData, envCtx, {
    capturePreset,
    onProgress,
  })
  onProgress?.(slidesData.length, slidesData.length, 'write')
  const pptx = await buildRasterPptx(pngDataUrls)
  await pptx.writeFile({ fileName: EXPORT_RASTER_FILE_NAME })
}
