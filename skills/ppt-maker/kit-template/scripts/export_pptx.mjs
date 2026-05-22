/**
 * 离线导出可编辑 .pptx（无需浏览器）。
 * 用法: npm run export:pptx
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath, pathToFileURL } from 'url'
import sizeOf from 'image-size'
import { projectConfig } from '../src/config/project.js'
import { writePptxToPath } from '../src/utils/exportPptx.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const materialsDir = path.join(root, 'public', 'assets', 'materials')
const outputDir = path.join(root, 'output')

/**
 * 从本地 materials 目录读取图片为 data URI，并附带原始像素尺寸。
 * @param {string} filename
 * @returns {{ src: string|null, width: number, height: number }}
 */
function loadImageNode(filename) {
  const filePath = path.join(materialsDir, filename)
  if (!fs.existsSync(filePath)) {
    return { src: null, width: 0, height: 0 }
  }
  const buf = fs.readFileSync(filePath)
  const dim = sizeOf(buf)
  const ext = filename.split('.').pop().toLowerCase()
  const mime = ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg' : 'image/png'
  return {
    src: `data:${mime};base64,${buf.toString('base64')}`,
    width: dim.width || 0,
    height: dim.height || 0,
  }
}

async function main() {
  const slidesModulePath = path.join(root, 'src', 'data', 'slides.js')
  const { slides } = await import(pathToFileURL(slidesModulePath).href)

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true })
  }

  const outputPath = path.join(outputDir, projectConfig.exports.editableFileName)
  const { missingImages } = await writePptxToPath(
    slides,
    outputPath,
    (filename) => Promise.resolve(loadImageNode(filename)),
  )

  console.log(`已写入: ${outputPath}`)
  if (missingImages.length > 0) {
    console.warn(`缺失素材 (${missingImages.length}): ${missingImages.join(', ')}`)
  } else {
    console.log('全部素材已嵌入。')
  }
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
