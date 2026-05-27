import { slideHash } from '../data/slides'
import {
  applyCaptureCssVars,
  clearCaptureCssVars,
  enterExportCaptureLayout,
  exitExportCaptureLayout,
  getPreviewCaptureSize,
  measurePreviewCanvasSize,
  renderCanvasToPng,
  scrollSlideIntoView,
  waitForCanvasReady,
  waitForLayoutPaint,
} from './captureSlides.js'
import { DEFAULT_CAPTURE_PRESET, getCapturePreset } from './capturePresets.js'
import { assertExportLayerCoverage } from './layerCaptureBrowser.js'

/**
 * 获取幻灯片画布 DOM 节点。
 * @param {number} slideId
 * @returns {HTMLElement}
 */
function getSlideCanvas(slideId) {
  const root = document.getElementById(slideHash(slideId))
  if (!root) {
    throw new Error(`未找到幻灯片节点 #${slideHash(slideId)}`)
  }
  const canvas = root.querySelector('.slide-frame__canvas')
  if (!canvas) {
    throw new Error(`幻灯片 #${slideHash(slideId)} 缺少 .slide-frame__canvas`)
  }
  return canvas
}

/**
 * 离屏渲染单页可编辑分层 PNG（背景 + 透明前景整页）。
 * @param {number} slideId
 * @param {{ width: number, height: number }} presetSize
 * @returns {Promise<{ backgroundUrl: string, foregroundUrl: string }>}
 */
export async function renderSlideEditableLayers(slideId, presetSize) {
  enterExportCaptureLayout(slideId)
  try {
    await scrollSlideIntoView(slideId)
    const canvas = getSlideCanvas(slideId)
    await waitForCanvasReady(canvas)
    await waitForLayoutPaint()

    assertExportLayerCoverage(canvas)

    document.body.classList.add('export-bg-capture')
    let backgroundUrl
    try {
      await waitForLayoutPaint()
      backgroundUrl = await renderCanvasToPng(canvas, presetSize)
    } finally {
      document.body.classList.remove('export-bg-capture')
    }

    document.body.classList.add('export-fg-capture')
    try {
      await waitForLayoutPaint()
      const foregroundUrl = await renderCanvasToPng(canvas, presetSize, {
        backgroundColor: 'transparent',
      })
      return { backgroundUrl, foregroundUrl }
    } finally {
      document.body.classList.remove('export-fg-capture')
    }
  } finally {
    exitExportCaptureLayout(slideId)
  }
}

/**
 * 离屏渲染全部幻灯片可编辑分层 PNG。
 * @param {Array<{ id: number }>} slidesData
 * @param {{ capturePreset?: string, onProgress?: (current: number, total: number, phase: string) => void }} [options]
 * @returns {Promise<Array<{ backgroundUrl: string, foregroundUrl: string }>>}
 */
export async function renderStoryboardEditableLayers(slidesData, options = {}) {
  const { capturePreset = DEFAULT_CAPTURE_PRESET, onProgress } = options
  const preset = getCapturePreset(capturePreset)
  const presetSize = { width: preset.width, height: preset.height }
  const previewSize = measurePreviewCanvasSize(slidesData[0].id)
  applyCaptureCssVars(preset, previewSize)

  const total = slidesData.length
  const results = []

  try {
    for (let i = 0; i < slidesData.length; i++) {
      const slide = slidesData[i]
      onProgress?.(i + 1, total, 'render')
      const slideLayers = await renderSlideEditableLayers(slide.id, presetSize)
      results.push(slideLayers)
    }
    return results
  } finally {
    clearCaptureCssVars()
    document.body.classList.remove('export-bg-capture')
    document.body.classList.remove('export-fg-capture')
  }
}

export { getPreviewCaptureSize }
