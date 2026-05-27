import { projectConfig } from '../config/project.js'
import { DEFAULT_CAPTURE_PRESET, getCapturePreset } from './capturePresets.js'
import { renderStoryboardEditableLayers } from './editableLayerPipeline.js'
import {
  prepareExportEnvironment,
  restoreExportEnvironment,
} from './captureSlides.js'
import { loadPptxGenJS, SLIDE_H, SLIDE_W } from './pptxLoader.js'

/** 两层可编辑 PPT 默认文件名 */
export const EXPORT_FILE_NAME = projectConfig.exports.editableFileName

/**
 * 由背景 + 透明前景 PNG 组装两层可编辑 PPT。
 * @param {Array<{ backgroundUrl: string, foregroundUrl: string }>} slideLayers
 * @returns {Promise<import('pptxgenjs').default>}
 */
export async function buildEditablePptx(slideLayers) {
  const PptxGenJS = await loadPptxGenJS()
  const pptx = new PptxGenJS()
  pptx.layout = 'LAYOUT_16x9'
  pptx.title = projectConfig.exports.pptxTitle
  pptx.author = projectConfig.exports.pptxAuthor

  slideLayers.forEach(({ backgroundUrl, foregroundUrl }) => {
    const slide = pptx.addSlide()
    slide.addImage({
      data: backgroundUrl,
      x: 0,
      y: 0,
      w: SLIDE_W,
      h: SLIDE_H,
    })
    slide.addImage({
      data: foregroundUrl,
      x: 0,
      y: 0,
      w: SLIDE_W,
      h: SLIDE_H,
    })
  })

  return pptx
}

/**
 * 浏览器一键导出两层可编辑 PPT（背景 + 透明前景整页）。
 * @param {Array<{ id: number }>} slidesData
 * @param {{ gridState: { active: boolean } }} envCtx
 * @param {{ capturePreset?: string, onProgress?: (current: number, total: number, phase: string) => void }} [options]
 * @returns {Promise<void>}
 */
export async function exportStoryboardToPptx(slidesData, envCtx, options = {}) {
  if (typeof document === 'undefined') {
    throw new Error('可编辑 PPT 需要在浏览器预览页中导出')
  }
  if (!slidesData?.length) {
    throw new Error('没有可导出的幻灯片数据')
  }

  const { capturePreset = DEFAULT_CAPTURE_PRESET, onProgress } = options
  const snapshot = prepareExportEnvironment(envCtx)
  document.body.classList.add('export-raster-active')

  try {
    const slideLayers = await renderStoryboardEditableLayers(slidesData, {
      capturePreset,
      onProgress,
    })
    onProgress?.(slidesData.length, slidesData.length, 'write')
    const pptx = await buildEditablePptx(slideLayers)
    await pptx.writeFile({ fileName: EXPORT_FILE_NAME })
  } finally {
    document.body.classList.remove('export-raster-active')
    document.body.classList.remove('export-bg-capture')
    document.body.classList.remove('export-fg-capture')
    restoreExportEnvironment(envCtx, snapshot)
  }
}

/**
 * Node 离线导出需在浏览器预览页完成。
 * @returns {Promise<never>}
 */
export async function writePptxToPath() {
  throw new Error(
    '可编辑 PPT 请在预览页点击「导出 PowerPoint（可编辑）」；需先 npm run serve 打开浏览器。',
  )
}

export { getCapturePreset }
