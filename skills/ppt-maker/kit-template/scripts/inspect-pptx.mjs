import fs from 'fs'
import JSZip from 'jszip'

const pptxPath = process.argv[2] || 'output/ppt-editable.pptx'
const buf = fs.readFileSync(pptxPath)
const zip = await JSZip.loadAsync(buf)
const media = Object.keys(zip.files).filter((k) => k.startsWith('ppt/media/') && !zip.files[k].dir)
console.log('media count', media.length)
for (const m of media.slice(0, 3)) {
  const d = await zip.file(m).async('nodebuffer')
  console.log(m, 'bytes', d.length)
}
const slideN = process.argv[3] || '18'
const slideXml = await zip.file(`ppt/slides/slide${slideN}.xml`).async('string')
const embeds = slideXml.match(/r:embed="[^"]+"/g) || []
console.log(`slide${slideN} embeds`, embeds.length)
const offs = [...slideXml.matchAll(/<a:off x="(\d+)" y="(\d+)"/g)].map((m) => ({
  x: Number(m[1]),
  y: Number(m[2]),
  xIn: (Number(m[1]) / 914400).toFixed(2),
  yIn: (Number(m[2]) / 914400).toFixed(2),
}))
const exts = [...slideXml.matchAll(/<a:ext cx="(\d+)" cy="(\d+)"/g)].map((m) => ({
  cx: Number(m[1]),
  cy: Number(m[2]),
  wIn: (Number(m[1]) / 914400).toFixed(2),
  hIn: (Number(m[2]) / 914400).toFixed(2),
}))
console.log('positions', offs.slice(0, 10))
console.log('extents', exts.slice(0, 10))
