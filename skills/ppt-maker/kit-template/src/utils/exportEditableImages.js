import { projectConfig } from '../config/project.js'
import { DEFAULT_CAPTURE_PRESET, getCapturePreset } from './capturePresets.js'
import { renderStoryboardEditableLayers } from './editableLayerPipeline.js'
import {
  prepareExportEnvironment,
  restoreExportEnvironment,
} from './captureSlides.js'

/** 可编辑分层 ZIP 默认文件名 */
export const EXPORT_EDITABLE_ZIP_FILE_NAME = projectConfig.exports.editableZipFileName

/**
 * 生成 ZIP 内背景/前景 PNG 文件名。
 * @param {number} slideId
 * @param {'background' | 'foreground'} layer
 * @param {number} width
 * @param {number} height
 * @returns {string}
 */
export function editableLayerPngFileName(slideId, layer, width, height) {
  const index = String(slideId).padStart(2, '0')
  return `slide-${index}-${layer}-${width}x${height}.png`
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
 * 浏览器一键导出可编辑分层 PNG ZIP（每页 background + foreground）。
 * @param {Array<{ id: number }>} slidesData
 * @param {{ gridState: { active: boolean } }} envCtx
 * @param {{ capturePreset?: string, onProgress?: (current: number, total: number, phase: string) => void }} [options]
 * @returns {Promise<void>}
 */
export async function exportStoryboardToEditableImageZip(slidesData, envCtx, options = {}) {
  const { capturePreset = DEFAULT_CAPTURE_PRESET, onProgress } = options
  const preset = getCapturePreset(capturePreset)
  const snapshot = prepareExportEnvironment(envCtx)
  document.body.classList.add('export-raster-active')

  try {
    const slideLayers = await renderStoryboardEditableLayers(slidesData, {
      capturePreset,
      onProgress,
    })
    onProgress?.(slidesData.length, slidesData.length, 'zip')
    const JSZip = (await import(
      /* webpackChunkName: "jszip-editable-export" */
      'jszip'
    )).default
    const zip = new JSZip()
    slidesData.forEach((slide, i) => {
      const { backgroundUrl, foregroundUrl } = slideLayers[i]
      zip.file(
        editableLayerPngFileName(slide.id, 'background', preset.width, preset.height),
        dataUrlToBlob(backgroundUrl),
      )
      zip.file(
        editableLayerPngFileName(slide.id, 'foreground', preset.width, preset.height),
        dataUrlToBlob(foregroundUrl),
      )
    })
    const blob = await zip.generateAsync({ type: 'blob' })
    downloadBlob(blob, EXPORT_EDITABLE_ZIP_FILE_NAME)
  } finally {
    document.body.classList.remove('export-raster-active')
    document.body.classList.remove('export-bg-capture')
    document.body.classList.remove('export-fg-capture')
    restoreExportEnvironment(envCtx, snapshot)
  }
}
