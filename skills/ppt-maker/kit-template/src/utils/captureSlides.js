import { slideHash } from '../data/slides'
import {
  DEFAULT_CAPTURE_PRESET,
  getCapturePreset,
  getCaptureScale,
  PREVIEW_BASE_HEIGHT,
  PREVIEW_BASE_WIDTH,
} from './capturePresets'

export { CAPTURE_HEIGHT, CAPTURE_WIDTH } from './capturePresets'

const IMAGE_WAIT_MS = 12000
const SCROLL_SETTLE_MS = 400

const CAPTURE_CSS_VARS = [
  '--capture-width',
  '--capture-height',
  '--capture-scale',
  '--slide-export-scale',
  '--preview-capture-width',
  '--preview-capture-height',
]

/** @type {{ width: number, height: number } | null} */
let activePreviewCaptureSize = null

/**
 * 预览基准画布尺寸（导出离屏排版用）。
 * @returns {{ width: number, height: number }}
 */
export function getPreviewCaptureSize() {
  if (activePreviewCaptureSize) {
    return activePreviewCaptureSize
  }
  return { width: PREVIEW_BASE_WIDTH, height: PREVIEW_BASE_HEIGHT }
}

/**
 * 读取当前预览态幻灯片画布的实际 DOM 尺寸。
 * @param {number} slideId
 * @returns {{ width: number, height: number }}
 */
export function measurePreviewCanvasSize(slideId) {
  const canvas = getSlideCanvas(slideId)
  const width = canvas.offsetWidth
  const height = canvas.offsetHeight
  if (!width || !height) {
    return { width: PREVIEW_BASE_WIDTH, height: PREVIEW_BASE_HEIGHT }
  }
  return { width, height }
}

/**
 * 将分辨率档位写入根节点 CSS 变量，供 export-capture.css 使用。
 * @param {{ width: number, height: number }} preset
 * @param {{ width: number, height: number }} [previewSize]
 */
export function applyCaptureCssVars(preset, previewSize = getPreviewCaptureSize()) {
  const scale = getCaptureScale(preset.width)
  activePreviewCaptureSize = previewSize
  const root = document.documentElement
  root.style.setProperty('--capture-width', `${preset.width}px`)
  root.style.setProperty('--capture-height', `${preset.height}px`)
  root.style.setProperty('--capture-scale', String(scale))
  root.style.setProperty('--slide-export-scale', String(scale))
  root.style.setProperty('--preview-capture-width', `${previewSize.width}px`)
  root.style.setProperty('--preview-capture-height', `${previewSize.height}px`)
}

/**
 * 清除离屏导出 CSS 变量。
 */
export function clearCaptureCssVars() {
  const root = document.documentElement
  CAPTURE_CSS_VARS.forEach((name) => root.style.removeProperty(name))
  activePreviewCaptureSize = null
}

/**
 * 准备像素级导出环境：关闭对齐网格并记录原状态。
 * @param {{ gridState: { active: boolean } }} ctx
 * @returns {{ gridWasActive: boolean, scrollX: number, scrollY: number }}
 */
export function prepareExportEnvironment(ctx) {
  const gridWasActive = ctx.gridState.active
  ctx.gridState.active = false
  return {
    gridWasActive,
    scrollX: window.scrollX,
    scrollY: window.scrollY,
  }
}

/**
 * 恢复导出前的网格与滚动位置。
 * @param {{ gridState: { active: boolean } }} ctx
 * @param {{ gridWasActive: boolean, scrollX: number, scrollY: number }} snapshot
 */
export function restoreExportEnvironment(ctx, snapshot) {
  ctx.gridState.active = snapshot.gridWasActive
  window.scrollTo(snapshot.scrollX, snapshot.scrollY)
}

/**
 * 进入离屏导出排版。
 * @param {number} slideId
 */
export function enterExportCaptureLayout(slideId) {
  const root = document.getElementById(slideHash(slideId))
  if (!root) {
    throw new Error(`未找到幻灯片节点 #${slideHash(slideId)}`)
  }
  root.classList.add('storyboard__item--export-capture')
}

/**
 * 退出离屏导出排版。
 * @param {number} slideId
 */
export function exitExportCaptureLayout(slideId) {
  const root = document.getElementById(slideHash(slideId))
  if (root) {
    root.classList.remove('storyboard__item--export-capture')
  }
}

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
 * 将幻灯片滚入视口并等待布局稳定。
 * @param {number} slideId
 * @returns {Promise<void>}
 */
export async function scrollSlideIntoView(slideId) {
  const root = document.getElementById(slideHash(slideId))
  if (!root) return
  root.scrollIntoView({ behavior: 'auto', block: 'center' })
  await new Promise((resolve) => setTimeout(resolve, SCROLL_SETTLE_MS))
}

/**
 * 等待布局绘制完成。
 * @returns {Promise<void>}
 */
export async function waitForLayoutPaint() {
  await new Promise((resolve) =>
    requestAnimationFrame(() => requestAnimationFrame(resolve)),
  )
}

/**
 * 等待画布内图片与 Web 字体就绪。
 * @param {HTMLElement} canvas
 * @returns {Promise<void>}
 */
export async function waitForCanvasReady(canvas) {
  const imgs = [...canvas.querySelectorAll('img')]
  await Promise.all(
    imgs.map(
      (img) =>
        new Promise((resolve) => {
          if (img.complete && img.naturalWidth > 0) {
            resolve()
            return
          }
          const done = () => resolve()
          img.addEventListener('load', done, { once: true })
          img.addEventListener('error', done, { once: true })
          setTimeout(done, IMAGE_WAIT_MS)
          if (img.loading === 'lazy') {
            img.loading = 'eager'
            if (!img.complete) {
              const src = img.src
              img.src = ''
              img.src = src
            }
          }
        }),
    ),
  )
  const decodeTasks = imgs
    .filter((img) => img.decode)
    .map((img) => img.decode().catch(() => {}))
  if (decodeTasks.length) {
    await Promise.all(decodeTasks)
  }
  if (document.fonts?.ready) {
    await document.fonts.ready
  }
  await waitForLayoutPaint()
}

/**
 * 校验画布 DOM 尺寸。
 * @param {HTMLElement} canvas
 * @param {{ width: number, height: number }} size
 */
function assertCanvasDimensions(canvas, size) {
  const w = canvas.offsetWidth
  const h = canvas.offsetHeight
  if (w !== size.width || h !== size.height) {
    throw new Error(
      `导出画布尺寸异常（${w}×${h}），预期 ${size.width}×${size.height}。请刷新页面后重试。`,
    )
  }
}

/**
 * 校验 PNG data URL 解码后的像素尺寸。
 * @param {string} dataUrl
 * @param {{ width: number, height: number }} size
 * @returns {Promise<void>}
 */
function verifyPngDimensions(dataUrl, size) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      if (img.naturalWidth !== size.width || img.naturalHeight !== size.height) {
        reject(
          new Error(
            `PNG 尺寸异常（${img.naturalWidth}×${img.naturalHeight}），预期 ${size.width}×${size.height}`,
          ),
        )
        return
      }
      resolve()
    }
    img.onerror = () => reject(new Error('PNG 解码失败'))
    img.src = dataUrl
  })
}

/**
 * 将 PNG data URL 归一化到目标像素尺寸。
 * @param {string} dataUrl
 * @param {{ width: number, height: number }} size
 * @returns {Promise<string>}
 */
function normalizePngDimensions(dataUrl, size) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      if (img.naturalWidth === size.width && img.naturalHeight === size.height) {
        resolve(dataUrl)
        return
      }
      const canvas = document.createElement('canvas')
      canvas.width = size.width
      canvas.height = size.height
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('无法创建 PNG 尺寸归一化画布'))
        return
      }
      ctx.drawImage(img, 0, 0, size.width, size.height)
      resolve(canvas.toDataURL('image/png'))
    }
    img.onerror = () => reject(new Error('PNG 解码失败'))
    img.src = dataUrl
  })
}

/**
 * 将画布离屏渲染为 PNG data URL（尺寸与 DOM 一致）。
 * @param {HTMLElement} canvas
 * @param {{ width: number, height: number }} presetSize
 * @param {{ backgroundColor?: string | null }} [options]
 * @returns {Promise<string>}
 */
export async function renderCanvasToPng(canvas, presetSize, options = {}) {
  const previewSize = getPreviewCaptureSize()
  assertCanvasDimensions(canvas, previewSize)
  const pixelRatio = presetSize.width / previewSize.width
  const { toPng } = await import(
    /* webpackChunkName: "html-to-image" */
    'html-to-image'
  )
  const toPngOptions = {
    width: previewSize.width,
    height: previewSize.height,
    pixelRatio,
    cacheBust: true,
  }
  if (options.backgroundColor !== undefined) {
    toPngOptions.backgroundColor = options.backgroundColor
  }
  const dataUrl = await toPng(canvas, toPngOptions)
  const normalizedDataUrl = await normalizePngDimensions(dataUrl, presetSize)
  await verifyPngDimensions(normalizedDataUrl, presetSize)
  return normalizedDataUrl
}

/**
 * 按顺序离屏渲染全部幻灯片画布，返回 PNG data URL 数组。
 * @param {Array<{ id: number }>} slides
 * @param {{ capturePreset?: string, onProgress?: (current: number, total: number, phase: string) => void }} [options]
 * @returns {Promise<string[]>}
 */
export async function captureAllSlideCanvases(slides, options = {}) {
  const { capturePreset = DEFAULT_CAPTURE_PRESET, onProgress } = options
  const preset = getCapturePreset(capturePreset)
  const size = { width: preset.width, height: preset.height }
  const previewSize = measurePreviewCanvasSize(slides[0].id)
  applyCaptureCssVars(preset, previewSize)

  const total = slides.length
  const results = []

  try {
    for (let i = 0; i < slides.length; i++) {
      const slide = slides[i]
      onProgress?.(i + 1, total, 'render')
      enterExportCaptureLayout(slide.id)
      try {
        await scrollSlideIntoView(slide.id)
        const canvas = getSlideCanvas(slide.id)
        await waitForCanvasReady(canvas)
        await waitForLayoutPaint()
        const dataUrl = await renderCanvasToPng(canvas, size)
        results.push(dataUrl)
      } finally {
        exitExportCaptureLayout(slide.id)
      }
    }
    return results
  } finally {
    clearCaptureCssVars()
  }
}
