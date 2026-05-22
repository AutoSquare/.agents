import { projectConfig } from '../config/project.js'
import { loadPptxGenJS, SLIDE_H, SLIDE_W } from './pptxLoader.js'

/** 与 design-tokens.css 对齐的导出配色 */
const COLORS = {
  background: 'FCFBF9',
  foreground: '0F1E24',
  secondary: '5A676E',
  muted: '84929A',
  accent: 'B89047',
  accentLight: 'F7F4EB',
  border: 'E1DDD4',
  hudBg: '090D16',
}

const FONT_TITLE = 'Microsoft YaHei'
const FONT_BODY = 'Microsoft YaHei'
const EXPORT_FILE_NAME = projectConfig.exports.editableFileName

const MARGIN_X = 0.35
const MARGIN_TOP = 0.28
const HEADER_H = 0.72
const FOOTER_H = 0.32
const GAP_COL = 0.12
/** 与 DualCaseLayout 左右栏内边距（约 16–20px）对应 */
const COL_PAD = 0.14

const CONTENT_Y = MARGIN_TOP + HEADER_H + 0.08
const CONTENT_H = SLIDE_H - CONTENT_Y - FOOTER_H - 0.12
const CONTENT_W = SLIDE_W - MARGIN_X * 2

/**
 * 根据 layoutRatio 计算左右栏宽度（英寸）。
 * @param {string} layoutRatio
 * @returns {{ leftW: number, rightW: number }}
 */
function getColumnWidths(layoutRatio) {
  const inner = CONTENT_W - GAP_COL
  if (layoutRatio === '60-40') {
    return { leftW: inner * 0.6, rightW: inner * 0.4 }
  }
  if (layoutRatio === '65-35') {
    return { leftW: inner * 0.65, rightW: inner * 0.35 }
  }
  return { leftW: inner * 0.5, rightW: inner * 0.5 }
}

/** @typedef {{ src: string|null, width: number, height: number }} ImageAsset */

/**
 * 估算案例面板底部文案区高度（英寸），用于为图片区留出与网页 flex 相近的空间。
 * @param {object} caseItem
 * @returns {number}
 */
function estimateCaseFooterHeight(caseItem) {
  let h = 0.12
  if (caseItem.description) h += 0.48
  if (caseItem.metadata?.length) {
    h += 0.14 + caseItem.metadata.length * 0.15
  }
  if (caseItem.tags?.length) h += 0.24
  return h
}

/**
 * 在单元格内按真实像素比例计算图片位置与尺寸（勿用 pptxgen sizing：其误将框尺寸当作图源比例）。
 * @param {number} cellW
 * @param {number} cellH
 * @param {number} natW
 * @param {number} natH
 * @param {string} fitMode
 * @returns {{ x: number, y: number, w: number, h: number }}
 */
function layoutImageInCell(cellW, cellH, natW, natH, fitMode) {
  if (!natW || !natH) {
    return { x: 0, y: 0, w: cellW, h: cellH }
  }
  const ir = natW / natH
  const br = cellW / cellH
  let layout
  if (fitMode === 'cover') {
    if (ir >= br) {
      const h = cellH
      const w = cellH * ir
      layout = { x: (cellW - w) / 2, y: 0, w, h }
    } else {
      const w = cellW
      const h = cellW / ir
      layout = { x: 0, y: (cellH - h) / 2, w, h }
    }
  } else if (ir >= br) {
    const w = cellW
    const h = cellW / ir
    layout = { x: 0, y: (cellH - h) / 2, w, h }
  } else {
    const h = cellH
    const w = cellH * ir
    layout = { x: (cellW - w) / 2, y: 0, w, h }
  }
  if (
    layout.w > cellW + 0.02 ||
    layout.h > cellH + 0.02 ||
    layout.x < -0.02 ||
    layout.y < -0.02
  ) {
    return layoutImageInCell(cellW, cellH, natW, natH, 'contain')
  }
  return layout
}

/**
 * 绘制与网页 spec-row 一致的点引导指标行。
 * @param {PptxGenJS} pptx
 * @param {import('pptxgenjs').Slide} pptSlide
 * @param {object} caseItem
 * @param {{ x: number, y: number, w: number }} box
 * @param {number} startY
 * @returns {number} 绘制结束后的 Y
 */
function addMetadataRows(pptx, pptSlide, caseItem, box, startY) {
  if (!caseItem.metadata?.length) {
    return startY
  }
  const rowH = 0.14
  const labelW = box.w * 0.56
  const valueW = box.w * 0.34
  const leaderX = box.x + labelW
  const leaderW = Math.max(0.2, box.w - labelW - valueW - 0.04)
  const valueX = box.x + box.w - valueW
  let y = startY
  pptSlide.addShape(pptx.ShapeType.line, {
    x: box.x,
    y: y,
    w: box.w,
    h: 0,
    line: { color: COLORS.border, width: 0.5, dashType: 'sysDot' },
  })
  y += 0.08
  caseItem.metadata.forEach((m) => {
    pptSlide.addText(m.label, {
      x: box.x,
      y,
      w: labelW,
      h: rowH,
      fontSize: 7,
      color: COLORS.muted,
      fontFace: FONT_BODY,
      valign: 'middle',
    })
    pptSlide.addShape(pptx.ShapeType.line, {
      x: leaderX,
      y: y + rowH * 0.72,
      w: leaderW,
      h: 0,
      line: { color: COLORS.border, width: 0.5, dashType: 'sysDot' },
    })
    pptSlide.addText(m.value, {
      x: valueX,
      y,
      w: valueW,
      h: rowH,
      fontSize: 7,
      bold: true,
      color: COLORS.foreground,
      fontFace: FONT_BODY,
      align: 'right',
      valign: 'middle',
    })
    y += rowH + 0.03
  })
  return y + 0.04
}

/**
 * 浏览器：读取图片原始像素尺寸。
 * @param {string} src
 * @returns {Promise<{ width: number, height: number }|null>}
 */
function probeImageDimensions(src) {
  if (typeof window === 'undefined' || !src) {
    return Promise.resolve(null)
  }
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve({
        width: img.naturalWidth || 0,
        height: img.naturalHeight || 0,
      })
    }
    img.onerror = () => resolve(null)
    img.src = src
  })
}

/**
 * 浏览器环境：校验素材可访问并返回 URL 与原始尺寸。
 * @param {string} filename
 * @param {string} assetBase
 * @returns {Promise<ImageAsset>}
 */
async function resolveBrowserImageAsset(filename, assetBase = '/assets/materials/') {
  const url = `${assetBase}${filename}`
  try {
    const res = await fetch(url, { method: 'HEAD' })
    if (!res.ok) {
      return { src: null, width: 0, height: 0 }
    }
    const dims = await probeImageDimensions(url)
    return {
      src: url,
      width: dims?.width || 0,
      height: dims?.height || 0,
    }
  } catch {
    return { src: null, width: 0, height: 0 }
  }
}

/**
 * 浏览器环境：校验素材可访问并返回 URL 路径（由 pptxgenjs 内部 XHR 编码）。
 * @param {string} filename
 * @param {string} assetBase
 * @returns {Promise<string|null>}
 */
async function resolveBrowserImagePath(filename, assetBase = '/assets/materials/') {
  const asset = await resolveBrowserImageAsset(filename, assetBase)
  return asset.src
}

/**
 * 浏览器环境：拉取素材并转为 base64 data URI（Node 离线导出使用）。
 * @param {string} filename
 * @param {string} assetBase
 * @returns {Promise<string|null>}
 */
async function loadImageBrowser(filename, assetBase = '/assets/materials/') {
  const url = `${assetBase}${filename}`
  try {
    const res = await fetch(url)
    if (!res.ok) return null
    const blob = await res.blob()
    const buffer = await blob.arrayBuffer()
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.length; i += 1) {
      binary += String.fromCharCode(bytes[i])
    }
    const b64 = btoa(binary)
    const ext = filename.split('.').pop().toLowerCase()
    const mime = ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg' : 'image/png'
    return `data:${mime};base64,${b64}`
  } catch {
    return null
  }
}

/**
 * 统一预加载结果为 ImageAsset。
 * @param {ImageAsset|string|null|undefined} value
 * @returns {ImageAsset}
 */
function normalizeImageAsset(value) {
  if (!value) {
    return { src: null, width: 0, height: 0 }
  }
  if (typeof value === 'string') {
    return { src: value, width: 0, height: 0 }
  }
  return {
    src: value.src ?? null,
    width: value.width || 0,
    height: value.height || 0,
  }
}

/**
 * 将素材转为 pptxgenjs addImage 参数（data URI 或 URL 路径）。
 * @param {ImageAsset} asset
 * @returns {{ data: string }|{ path: string }|null}
 */
function toAddImageSource(asset) {
  const src = asset?.src
  if (!src) return null
  if (src.startsWith('data:')) {
    return { data: src }
  }
  return { path: src }
}

/**
 * 预加载幻灯片全部素材。
 * @param {Array} slidesData
 * @param {(filename: string) => Promise<ImageAsset|string|null>} loader
 * @returns {Promise<Map<string, ImageAsset>>}
 */
async function preloadImages(slidesData, loader) {
  const names = new Set()
  slidesData.forEach((slide) => {
    slide.cases.forEach((c) => {
      c.images.forEach((f) => names.add(f))
    })
  })
  const map = new Map()
  await Promise.all(
    [...names].map(async (f) => {
      map.set(f, normalizeImageAsset(await loader(f)))
    }),
  )
  return map
}

/**
 * 绘制页眉。
 * @param {PptxGenJS} pptx
 * @param {import('pptxgenjs').Slide} pptSlide
 * @param {object} slide
 */
function addSlideHeader(pptx, pptSlide, slide) {
  const y0 = MARGIN_TOP
  pptSlide.addText(slide.sectionLabel, {
    x: MARGIN_X,
    y: y0,
    w: 3,
    h: 0.22,
    fontSize: 8,
    bold: true,
    color: COLORS.accent,
    fontFace: FONT_BODY,
    charSpacing: 2,
  })
  pptSlide.addText(`${slide.sectionIndex} // 03`, {
    x: SLIDE_W - MARGIN_X - 1.2,
    y: y0,
    w: 1.2,
    h: 0.22,
    fontSize: 8,
    bold: true,
    color: COLORS.muted,
    fontFace: FONT_BODY,
    align: 'right',
  })
  pptSlide.addText(slide.title, {
    x: MARGIN_X,
    y: y0 + 0.24,
    w: 5.5,
    h: 0.32,
    fontSize: 16,
    bold: true,
    color: COLORS.foreground,
    fontFace: FONT_TITLE,
  })
  pptSlide.addText(slide.theme, {
    x: MARGIN_X + 5.7,
    y: y0 + 0.28,
    w: SLIDE_W - MARGIN_X * 2 - 5.7,
    h: 0.28,
    fontSize: 9,
    color: COLORS.secondary,
    fontFace: FONT_BODY,
  })
  pptSlide.addShape(pptx.ShapeType.line, {
    x: MARGIN_X,
    y: MARGIN_TOP + HEADER_H,
    w: CONTENT_W,
    h: 0,
    line: { color: COLORS.border, width: 0.75 },
  })
}

/**
 * 绘制页脚。
 * @param {PptxGenJS} pptx
 * @param {import('pptxgenjs').Slide} pptSlide
 */
function addSlideFooter(pptx, pptSlide) {
  const y = SLIDE_H - FOOTER_H - 0.08
  pptSlide.addShape(pptx.ShapeType.line, {
    x: MARGIN_X,
    y: y - 0.04,
    w: CONTENT_W,
    h: 0,
    line: { color: COLORS.border, width: 0.5 },
  })
  pptSlide.addText(projectConfig.footerLeftText, {
    x: MARGIN_X,
    y,
    w: 5,
    h: FOOTER_H,
    fontSize: 6,
    bold: true,
    color: COLORS.muted,
    fontFace: FONT_BODY,
  })
  pptSlide.addText(projectConfig.exports.pptxFooterLine, {
    x: SLIDE_W - MARGIN_X - 3.5,
    y,
    w: 3.5,
    h: FOOTER_H,
    fontSize: 6,
    bold: true,
    color: COLORS.muted,
    fontFace: FONT_BODY,
    align: 'right',
  })
}

/**
 * 在指定区域内绘制单个案例面板。
 * @param {PptxGenJS} pptx
 * @param {import('pptxgenjs').Slide} pptSlide
 * @param {object} caseItem
 * @param {{ x: number, y: number, w: number, h: number }} box
 * @param {Map<string, ImageAsset>} imageMap
 * @param {string[]} missingImages
 */
function addCasePanel(pptx, pptSlide, caseItem, box, imageMap, missingImages) {
  let cursorY = box.y
  const pad = 0.06

  pptSlide.addText(`CASE // ${caseItem.index}`, {
    x: box.x,
    y: cursorY,
    w: 1.2,
    h: 0.18,
    fontSize: 7,
    bold: true,
    color: COLORS.accent,
    fontFace: FONT_BODY,
    fill: { color: COLORS.accentLight },
  })
  pptSlide.addText(caseItem.name, {
    x: box.x + 1.25,
    y: cursorY,
    w: box.w - 1.25,
    h: 0.22,
    fontSize: 11,
    bold: true,
    color: COLORS.foreground,
    fontFace: FONT_TITLE,
  })
  cursorY += 0.22
  pptSlide.addText(caseItem.subtitle, {
    x: box.x + 1.25,
    y: cursorY,
    w: box.w - 1.25,
    h: 0.16,
    fontSize: 7,
    bold: true,
    color: COLORS.accent,
    fontFace: FONT_BODY,
  })
  cursorY += 0.2

  const mediaY = cursorY
  const footerH = estimateCaseFooterHeight(caseItem)
  const availableH = box.y + box.h - footerH - mediaY
  const mediaH = Math.max(1.35, availableH - 0.04)
  const frameInset = 0.03
  const innerW = box.w - pad * 2
  const imageCount = caseItem.images.length
  const colGap = 0.06
  const isHud = caseItem.imageFrameType === 'hud'
  const fitMode = caseItem.imageFit === 'cover' ? 'cover' : 'contain'
  const multiRow = imageCount >= 2

  /**
   * 在单元格内绘制相框与按比例居中的图片（对齐网页 object-fit + 多图横排）。
   * @param {string} filename
   * @param {number} cellX
   * @param {number} cellY
   * @param {number} cellW
   * @param {number} cellH
   */
  const placeImageCell = (filename, cellX, cellY, cellW, cellH) => {
    const asset = normalizeImageAsset(imageMap.get(filename))
    if (!asset.src) {
      missingImages.push(filename)
      pptSlide.addText(`[素材缺失: ${filename}]`, {
        x: cellX,
        y: cellY,
        w: cellW,
        h: cellH,
        fontSize: 8,
        color: COLORS.muted,
        fontFace: FONT_BODY,
        align: 'center',
        valign: 'middle',
        fill: { color: COLORS.border },
      })
      return
    }
    if (isHud) {
      pptSlide.addShape(pptx.ShapeType.rect, {
        x: cellX,
        y: cellY,
        w: cellW,
        h: cellH,
        fill: { color: COLORS.hudBg },
        line: { color: '0E7490', width: 0.75 },
      })
    } else {
      pptSlide.addShape(pptx.ShapeType.rect, {
        x: cellX,
        y: cellY,
        w: cellW,
        h: cellH,
        fill: { color: COLORS.background },
        line: { color: COLORS.border, width: 0.5 },
      })
    }
    const innerCellW = cellW - frameInset * 2
    const innerCellH = cellH - frameInset * 2
    const imgX = cellX + frameInset
    const imgY = cellY + frameInset
    const layout = layoutImageInCell(
      innerCellW,
      innerCellH,
      asset.width,
      asset.height,
      fitMode,
    )
    const imageSource = toAddImageSource(asset)
    pptSlide.addImage({
      ...imageSource,
      x: imgX + layout.x,
      y: imgY + layout.y,
      w: layout.w,
      h: layout.h,
    })
  }

  if (multiRow) {
    const cellW = (innerW - colGap * (imageCount - 1)) / imageCount
    caseItem.images.forEach((filename, idx) => {
      const cellX = box.x + pad + idx * (cellW + colGap)
      placeImageCell(filename, cellX, mediaY, cellW, mediaH)
    })
  } else if (imageCount === 1) {
    placeImageCell(caseItem.images[0], box.x + pad, mediaY, innerW, mediaH)
  }

  cursorY = mediaY + mediaH + 0.1

  if (caseItem.description) {
    pptSlide.addText(caseItem.description, {
      x: box.x,
      y: cursorY,
      w: box.w,
      h: 0.55,
      fontSize: 7,
      color: COLORS.secondary,
      fontFace: FONT_BODY,
      valign: 'top',
    })
    cursorY += 0.58
  }

  if (caseItem.metadata?.length) {
    cursorY = addMetadataRows(pptx, pptSlide, caseItem, box, cursorY)
  }

  if (caseItem.tags && caseItem.tags.length) {
    pptSlide.addText(caseItem.tags.join('  ·  '), {
      x: box.x,
      y: Math.min(cursorY, box.y + box.h - 0.22),
      w: box.w,
      h: 0.2,
      fontSize: 6,
      bold: true,
      color: COLORS.secondary,
      fontFace: FONT_BODY,
      fill: { color: COLORS.accentLight },
    })
  }
}

/**
 * 构建 PPTX 实例（不写入文件）。
 * @param {Array} slidesData
 * @param {(filename: string) => Promise<string|null>} imageLoader
 * @returns {Promise<{ pptx: PptxGenJS, missingImages: string[] }>}
 */
export async function buildPptx(slidesData, imageLoader) {
  const imageMap = await preloadImages(slidesData, imageLoader)
  const missingImages = []
  const PptxGenJS = await loadPptxGenJS()
  const pptx = new PptxGenJS()
  pptx.layout = 'LAYOUT_16x9'
  pptx.author = projectConfig.exports.pptxAuthor
  pptx.title = projectConfig.exports.pptxTitle

  slidesData.forEach((slide) => {
    const pptSlide = pptx.addSlide()
    pptSlide.background = { color: COLORS.background }

    addSlideHeader(pptx, pptSlide, slide)
    addSlideFooter(pptx, pptSlide)

    const { leftW, rightW } = getColumnWidths(slide.layoutRatio || '50-50')
    const leftX = MARGIN_X
    const rightX = MARGIN_X + leftW + GAP_COL
    const caseBox = { y: CONTENT_Y, h: CONTENT_H }

    if (slide.cases[0]) {
      addCasePanel(
        pptx,
        pptSlide,
        slide.cases[0],
        {
          x: leftX + COL_PAD,
          y: caseBox.y,
          w: leftW - COL_PAD * 2,
          h: caseBox.h,
        },
        imageMap,
        missingImages,
      )
    }
    if (slide.cases[1]) {
      addCasePanel(
        pptx,
        pptSlide,
        slide.cases[1],
        {
          x: rightX + COL_PAD,
          y: caseBox.y,
          w: rightW - COL_PAD * 2,
          h: caseBox.h,
        },
        imageMap,
        missingImages,
      )
    }

    if (slide.cases.length > 1) {
      const dividerX = MARGIN_X + leftW + GAP_COL / 2
      pptSlide.addShape(pptx.ShapeType.line, {
        x: dividerX,
        y: CONTENT_Y + 0.05,
        w: 0,
        h: CONTENT_H - 0.1,
        line: { color: COLORS.accent, width: 0.5 },
      })
    }
  })

  return { pptx, missingImages: [...new Set(missingImages)] }
}

/**
 * 浏览器一键导出并下载 .pptx。
 * @param {Array} slidesData
 * @returns {Promise<{ missingImages: string[] }>}
 */
export async function exportStoryboardToPptx(slidesData) {
  const { pptx, missingImages } = await buildPptx(slidesData, (filename) =>
    resolveBrowserImageAsset(filename),
  )
  await pptx.writeFile({ fileName: EXPORT_FILE_NAME })
  return { missingImages }
}

/**
 * Node 环境：写入指定路径。
 * @param {Array} slidesData
 * @param {string} outputPath
 * @param {(filename: string) => Promise<string|null>} imageLoader
 * @returns {Promise<{ missingImages: string[], outputPath: string }>}
 */
export async function writePptxToPath(slidesData, outputPath, imageLoader) {
  const { pptx, missingImages } = await buildPptx(slidesData, imageLoader)
  await pptx.writeFile({ fileName: outputPath })
  return { missingImages, outputPath }
}

export { EXPORT_FILE_NAME, loadImageBrowser, resolveBrowserImagePath, resolveBrowserImageAsset }
