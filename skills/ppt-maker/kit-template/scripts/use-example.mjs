/**
 * 将 examples/{name}/slides.js 复制到 src/data/slides.js。
 * 用法: node scripts/use-example.mjs default | zhuanlun
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const name = process.argv[2] || 'default'
const allowed = ['default', 'zhuanlun']

if (!allowed.includes(name)) {
  console.error(`未知示例: ${name}。可选: ${allowed.join(', ')}`)
  process.exit(1)
}

const src = path.join(root, 'examples', name, 'slides.js')
const dest = path.join(root, 'src', 'data', 'slides.js')

if (!fs.existsSync(src)) {
  console.error(`未找到: ${src}`)
  process.exit(1)
}

fs.copyFileSync(src, dest)
console.log(`已切换为示例「${name}」: ${dest}`)
if (name === 'zhuanlun') {
  console.log('请将对应 PNG 放入 public/assets/materials/（套件不附带业务素材）。')
}
