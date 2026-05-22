import {
  captureAllSlideCanvases,
  prepareExportEnvironment,
  restoreExportEnvironment,
} from './captureSlides.js'
import { DEFAULT_CAPTURE_PRESET } from './capturePresets.js'

/**
 * 离屏渲染全部幻灯片为 PNG data URL 列表。
 * @param {Array<{ id: number }>} slidesData
 * @param {{ gridState: { active: boolean } }} envCtx
 * @param {{ capturePreset?: string, onProgress?: (current: number, total: number, phase: string) => void }} [options]
 * @returns {Promise<string[]>}
 */
export async function renderStoryboardSlides(slidesData, envCtx, options = {}) {
  const { capturePreset = DEFAULT_CAPTURE_PRESET, onProgress } = options
  const snapshot = prepareExportEnvironment(envCtx)
  try {
    return await captureAllSlideCanvases(slidesData, {
      capturePreset,
      onProgress: (current, total) => onProgress?.(current, total, 'render'),
    })
  } finally {
    restoreExportEnvironment(envCtx, snapshot)
  }
}
