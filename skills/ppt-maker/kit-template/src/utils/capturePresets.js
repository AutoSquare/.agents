/** 预览基准宽度（px），用于计算离屏排版缩放 */
export const PREVIEW_BASE_WIDTH = 1024

/** 预览基准高度（px），16:9 */
export const PREVIEW_BASE_HEIGHT = Math.round((PREVIEW_BASE_WIDTH * 9) / 16)

/** 默认导出分辨率档位 */
export const DEFAULT_CAPTURE_PRESET = 'uhd'

/**
 * 离屏渲染分辨率档位。
 * @type {Record<string, { id: string, width: number, height: number, label: string, shortLabel: string }>}
 */
export const CAPTURE_PRESETS = {
  hd: {
    id: 'hd',
    width: 1920,
    height: 1080,
    label: '1080p（1920×1080）',
    shortLabel: '1080p',
  },
  qhd: {
    id: 'qhd',
    width: 2560,
    height: 1440,
    label: '2K（2560×1440）',
    shortLabel: '2K',
  },
  uhd: {
    id: 'uhd',
    width: 3840,
    height: 2160,
    label: '4K（3840×2160）',
    shortLabel: '4K',
  },
}

/** 1080p 档位宽高（兼容旧引用） */
export const CAPTURE_WIDTH = CAPTURE_PRESETS.hd.width
/** 1080p 档位宽高（兼容旧引用） */
export const CAPTURE_HEIGHT = CAPTURE_PRESETS.hd.height

/**
 * 获取分辨率档位配置。
 * @param {string} [presetId]
 * @returns {{ id: string, width: number, height: number, label: string, shortLabel: string }}
 */
export function getCapturePreset(presetId = DEFAULT_CAPTURE_PRESET) {
  const preset = CAPTURE_PRESETS[presetId]
  if (!preset) {
    return CAPTURE_PRESETS[DEFAULT_CAPTURE_PRESET]
  }
  return preset
}

/**
 * 相对预览宽度的排版缩放倍率。
 * @param {number} width
 * @returns {number}
 */
export function getCaptureScale(width) {
  return width / PREVIEW_BASE_WIDTH
}
