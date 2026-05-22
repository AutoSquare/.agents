import { projectConfig } from '../config/project.js'
import { DEFAULT_CAPTURE_PRESET, getCapturePreset } from './capturePresets.js'
import { renderStoryboardSlides } from './slideRasterPipeline.js'

/** ZIP 包默认文件名 */
export const EXPORT_ZIP_FILE_NAME = projectConfig.exports.zipFileName

/**
 * 生成 ZIP 内 PNG 文件名。
 * @param {number} slideId
 * @param {number} width
 * @param {number} height
 * @returns {string}
 */
export function slidePngFileName(slideId, width, height) {
  const index = String(slideId).padStart(2, '0')
  return `slide-${index}-${width}x${height}.png`
}

/**
 * 将 data URL 转为 Blob。
 * @param {string} dataUrl
 * @returns {Blob}
 */
function dataUrlToBlob(dataUrl) {
  const [header, base64] = dataUrl.split(',')
  const mime = header.match(/:(.*?);/)?.[1] || 'image/png'
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return new Blob([bytes], { type: mime })
}

/**
 * 触发浏览器下载 Blob。
 * @param {Blob} blob
 * @param {string} fileName
 */
function downloadBlob(blob, fileName) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = fileName
  anchor.rel = 'noopener'
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}

/**
 * 浏览器一键导出幻灯片 PNG ZIP。
 * @param {Array<{ id: number }>} slidesData
 * @param {{ gridState: { active: boolean } }} envCtx
 * @param {{ capturePreset?: string, onProgress?: (current: number, total: number, phase: string) => void }} [options]
 * @returns {Promise<void>}
 */
export async function exportStoryboardToImageZip(slidesData, envCtx, options = {}) {
  const { capturePreset = DEFAULT_CAPTURE_PRESET, onProgress } = options
  const preset = getCapturePreset(capturePreset)
  const pngDataUrls = await renderStoryboardSlides(slidesData, envCtx, {
    capturePreset,
    onProgress,
  })
  onProgress?.(slidesData.length, slidesData.length, 'zip')
  const JSZip = (await import(
    /* webpackChunkName: "jszip-export" */
    'jszip'
  )).default
  const zip = new JSZip()
  slidesData.forEach((slide, i) => {
    zip.file(
      slidePngFileName(slide.id, preset.width, preset.height),
      dataUrlToBlob(pngDataUrls[i]),
    )
  })
  const blob = await zip.generateAsync({ type: 'blob' })
  downloadBlob(blob, EXPORT_ZIP_FILE_NAME)
}
