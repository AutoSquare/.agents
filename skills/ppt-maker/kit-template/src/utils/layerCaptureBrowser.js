const MIN_SIZE = 2

/**
 * 判断节点是否含直接可见内容（非仅子节点聚合）。
 * @param {Element} el
 * @returns {boolean}
 */
function hasDirectVisibleContent(el) {
  if (el.matches('img, svg, video, canvas')) return true
  for (const child of el.childNodes) {
    if (child.nodeType === Node.TEXT_NODE && child.textContent.trim()) return true
  }
  return false
}

/**
 * 判断元素是否在 export-layer-fg 子树内。
 * @param {Element} el
 * @returns {boolean}
 */
function isInsideForegroundLayer(el) {
  return Boolean(el.closest('.export-layer-fg'))
}

/**
 * 判断元素是否为纯装饰层或位于装饰层内。
 * @param {Element} el
 * @returns {boolean}
 */
function isBackgroundDecor(el) {
  return Boolean(el.closest('.export-layer-bg'))
}

/**
 * 生成便于排查的节点描述。
 * @param {Element} el
 * @returns {string}
 */
function describeElement(el) {
  const tag = el.tagName.toLowerCase()
  const id = el.id ? `#${el.id}` : ''
  const classes = el.classList.length ? `.${Array.from(el.classList).join('.')}` : ''
  return `${tag}${id}${classes}`
}

/**
 * 校验画布内可见内容均已标 export-layer-fg 或 export-layer-bg，否则阻塞导出。
 * @param {Element} canvas
 */
export function assertExportLayerCoverage(canvas) {
  const untagged = []
  canvas.querySelectorAll('*').forEach((el) => {
    if (el.classList.contains('slide-canvas-backdrop')) return
    if (isBackgroundDecor(el)) return
    if (isInsideForegroundLayer(el)) return
    const style = getComputedStyle(el)
    if (style.display === 'none' || style.visibility === 'hidden') return
    const rect = el.getBoundingClientRect()
    if (rect.width <= MIN_SIZE || rect.height <= MIN_SIZE) return
    if (!hasDirectVisibleContent(el)) return
    untagged.push(describeElement(el))
  })
  if (untagged.length) {
    throw new Error(
      `可编辑导出打标不完整，以下节点缺少 export-layer-fg 祖先：${untagged.slice(0, 8).join('；')}${
        untagged.length > 8 ? ` 等共 ${untagged.length} 处` : ''
      }`,
    )
  }
}
