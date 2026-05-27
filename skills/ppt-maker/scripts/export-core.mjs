import crypto from 'crypto'
import fs from 'fs'
import path from 'path'

/** 可编辑导出红区文件（Agent 禁止修改，validate checksum 比对） */
export const EXPORT_CORE_REL_PATHS = [
  'src/utils/editableLayerPipeline.js',
  'src/utils/layerCaptureBrowser.js',
  'src/utils/captureSlideLayers.js',
  'src/utils/exportEditableImages.js',
  'src/styles/export-capture.css',
  'src/utils/exportPptx.js',
  'src/utils/captureSlides.js',
]

/**
 * 计算文件 sha256。
 * @param {string} filePath
 * @returns {string}
 */
export function sha256File(filePath) {
  const buf = fs.readFileSync(filePath)
  return crypto.createHash('sha256').update(buf).digest('hex')
}

/**
 * 写入 export-core.manifest.json。
 * @param {string} projectRoot ppt-projects/{slug} 绝对路径
 * @param {string} templateVersion
 */
export function writeExportCoreManifest(projectRoot, templateVersion) {
  const files = {}
  for (const rel of EXPORT_CORE_REL_PATHS) {
    const abs = path.join(projectRoot, rel)
    if (!fs.existsSync(abs)) {
      throw new Error(`export-core 文件缺失: ${rel}`)
    }
    files[rel] = sha256File(abs)
  }
  const manifest = {
    templateVersion,
    generatedAt: new Date().toISOString(),
    files,
  }
  fs.writeFileSync(
    path.join(projectRoot, 'export-core.manifest.json'),
    `${JSON.stringify(manifest, null, 2)}\n`,
    'utf8',
  )
  return manifest
}

/**
 * 校验项目红区文件与 manifest 一致。
 * @param {string} projectRoot
 * @returns {{ ok: boolean, errors: string[] }}
 */
export function verifyExportCore(projectRoot) {
  const manifestPath = path.join(projectRoot, 'export-core.manifest.json')
  const errors = []
  if (!fs.existsSync(manifestPath)) {
    return { ok: false, errors: ['缺少 export-core.manifest.json，请重新 scaffold'] }
  }
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
  for (const [rel, expected] of Object.entries(manifest.files || {})) {
    const abs = path.join(projectRoot, rel)
    if (!fs.existsSync(abs)) {
      errors.push(`红区文件缺失: ${rel}`)
      continue
    }
    const actual = sha256File(abs)
    if (actual !== expected) {
      errors.push(`红区文件被修改: ${rel}（导出引擎受保护，请撤销修改）`)
    }
  }
  return { ok: errors.length === 0, errors }
}
