/** 缓存构造函数，避免重复动态加载 */
let cachedPptxCtor = null

/** 16:9 幻灯片尺寸（英寸），与 LAYOUT_16x9 一致 */
export const SLIDE_W = 10
export const SLIDE_H = 5.625

/**
 * 探测是否为 PptxGenJS 构造函数（bundle 中 default 可能是 JSZip，不可用 prototype 判断）。
 * @param {unknown} ctor
 * @returns {boolean}
 */
function isPptxConstructor(ctor) {
  if (typeof ctor !== 'function') return false
  try {
    const instance = new ctor()
    return (
      typeof instance.addSlide === 'function' &&
      typeof instance.writeFile === 'function'
    )
  } catch {
    return false
  }
}

/**
 * 动态加载 pptxgenjs（ES 模块 + 显式 jszip 依赖，供 Webpack 打入浏览器 chunk）。
 * @returns {Promise<new () => import('pptxgenjs').default>}
 */
export async function loadPptxGenJS() {
  if (cachedPptxCtor && isPptxConstructor(cachedPptxCtor)) {
    return cachedPptxCtor
  }
  cachedPptxCtor = null
  const jszipMod = await import('jszip')
  const JSZipCtor = jszipMod.default || jszipMod
  if (typeof window !== 'undefined') {
    window.JSZip = JSZipCtor
  }
  const mod = await import(
    /* webpackChunkName: "pptx-export-lib" */
    'pptxgenjs'
  )
  const candidates = new Set()
  if (mod != null) {
    if (typeof mod.default === 'function') candidates.add(mod.default)
    if (typeof mod.PptxGenJS === 'function') candidates.add(mod.PptxGenJS)
    if (typeof mod === 'object') {
      Object.values(mod).forEach((v) => {
        if (typeof v === 'function') candidates.add(v)
      })
    }
  }
  for (const candidate of candidates) {
    if (isPptxConstructor(candidate)) {
      cachedPptxCtor = candidate
      return cachedPptxCtor
    }
  }
  throw new Error(
    `pptxgenjs 模块无法解析为 PptxGenJS 构造函数 (candidates=${candidates.size})`,
  )
}
