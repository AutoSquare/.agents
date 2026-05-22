#!/usr/bin/env node
/**
 * 从上游同步 kit-template（维护用，不修改上游内容）。
 * 用法: node sync-template.mjs [--upstream <绝对路径>]
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { KIT_TEMPLATE_DIR, TEMPLATE_VERSION, resolveKitSourceDir } from './_paths.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const EXCLUDE_DIRS = new Set(['node_modules', 'dist', 'output', '.cache', '.git'])
const EXCLUDE_FILES = new Set(['.DS_Store'])

function shouldSkip(rel) {
  const parts = rel.split(/[/\\]/).filter(Boolean)
  if (parts.some((p) => EXCLUDE_DIRS.has(p))) return true
  const base = parts[parts.length - 1]
  if (base && EXCLUDE_FILES.has(base)) return true
  if (rel.includes('public\\assets\\slides') || rel.includes('public/assets/slides')) {
    return true
  }
  return false
}

function copyRecursive(src, dest, rel = '') {
  const entries = fs.readdirSync(src, { withFileTypes: true })
  for (const ent of entries) {
    const childRel = rel ? `${rel}/${ent.name}` : ent.name
    if (shouldSkip(childRel)) continue
    const from = path.join(src, ent.name)
    const to = path.join(dest, ent.name)
    if (ent.isDirectory()) {
      fs.mkdirSync(to, { recursive: true })
      copyRecursive(from, to, childRel)
    } else if (ent.isFile()) {
      fs.mkdirSync(path.dirname(to), { recursive: true })
      fs.copyFileSync(from, to)
    }
  }
}

function main() {
  let kitSourceDir
  try {
    kitSourceDir = resolveKitSourceDir(process.argv.slice(2))
  } catch (err) {
    console.error(err.message)
    process.exit(1)
  }
  if (!fs.existsSync(kitSourceDir)) {
    console.error(`未找到源目录: ${kitSourceDir}`)
    console.error('提示: 使用 --upstream <绝对路径>，或在工作区根放置 ppt-maker-kit/ / ppt_style/')
    process.exit(1)
  }

  if (fs.existsSync(KIT_TEMPLATE_DIR)) {
    fs.rmSync(KIT_TEMPLATE_DIR, { recursive: true, force: true })
  }
  fs.mkdirSync(KIT_TEMPLATE_DIR, { recursive: true })

  copyRecursive(kitSourceDir, KIT_TEMPLATE_DIR)

  const meta = {
    templateVersion: TEMPLATE_VERSION,
    syncedAt: new Date().toISOString(),
    source: kitSourceDir,
  }
  fs.writeFileSync(
    path.join(KIT_TEMPLATE_DIR, '.template-meta.json'),
    `${JSON.stringify(meta, null, 2)}\n`,
    'utf8',
  )

  const placeholderSrc = path.join(kitSourceDir, 'public', 'assets', 'materials', 'placeholder.png')
  const placeholderDest = path.join(KIT_TEMPLATE_DIR, 'public', 'assets', 'materials', 'placeholder.png')
  if (fs.existsSync(placeholderSrc)) {
    fs.mkdirSync(path.dirname(placeholderDest), { recursive: true })
    fs.copyFileSync(placeholderSrc, placeholderDest)
  }

  console.log(`已同步 kit-template ← ${kitSourceDir}`)
  console.log(`版本: ${TEMPLATE_VERSION}`)
}

main()
