#!/usr/bin/env node
/**
 * 复制 kit-template 到 ppt-projects/{slug}，并写入 devServer 与项目元数据。
 * 用法: node scaffold.mjs --slug deck-xxx [--workspace path] [--force] [--style-brief "描述"]
 */
import fs from 'fs'
import path from 'path'
import {
  KIT_TEMPLATE_DIR,
  TEMPLATE_VERSION,
  defaultSlug,
  ensureDir,
  normalizeSlug,
  projectDir,
} from './_paths.mjs'

const EXCLUDE_DIRS = new Set(['node_modules', 'dist', 'output', '.cache', '.git'])

function parseArgs(argv) {
  const out = { force: false, workspace: process.cwd(), slug: null, styleBrief: null }
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--force') out.force = true
    else if (a === '--workspace' && argv[i + 1]) out.workspace = argv[++i]
    else if (a === '--slug' && argv[i + 1]) out.slug = argv[++i]
    else if (a === '--style-brief' && argv[i + 1]) out.styleBrief = argv[++i]
  }
  return out
}

function copyTemplate(src, dest) {
  const walk = (from, to, rel = '') => {
    for (const ent of fs.readdirSync(from, { withFileTypes: true })) {
      const childRel = rel ? `${rel}/${ent.name}` : ent.name
      const parts = childRel.split('/')
      if (parts.some((p) => EXCLUDE_DIRS.has(p))) continue
      if (childRel.includes('public/assets/slides')) continue
      const f = path.join(from, ent.name)
      const t = path.join(to, ent.name)
      if (ent.isDirectory()) {
        fs.mkdirSync(t, { recursive: true })
        walk(f, t, childRel)
      } else if (ent.isFile()) {
        fs.mkdirSync(path.dirname(t), { recursive: true })
        fs.copyFileSync(f, t)
      }
    }
  }
  walk(src, dest)
}

/**
 * 在用户副本 vue.config.js 注入 devServer（不改 kit-template 源文件）。
 * @param {string} vueConfigPath
 */
function patchDevServer(vueConfigPath) {
  let text = fs.readFileSync(vueConfigPath, 'utf8')
  if (text.includes('devServer:')) return
  const needle = 'module.exports = defineConfig({'
  if (!text.includes(needle)) {
    throw new Error('vue.config.js 格式无法自动注入 devServer')
  }
  const insert =
    '\n  devServer: {\n    port: 8080,\n    host: \'localhost\',\n  },'
  text = text.replace(needle, `${needle}${insert}`)
  fs.writeFileSync(vueConfigPath, text, 'utf8')
}

function main() {
  const { force, workspace, slug: rawSlug, styleBrief } = parseArgs(process.argv.slice(2))
  const slug = normalizeSlug(rawSlug || defaultSlug())

  if (!fs.existsSync(KIT_TEMPLATE_DIR)) {
    console.error(`未找到 kit-template: ${KIT_TEMPLATE_DIR}`)
    console.error('请先运行: node ppt-maker/scripts/sync-template.mjs')
    process.exit(1)
  }

  const dest = projectDir(workspace, slug)
  if (fs.existsSync(dest)) {
    if (!force) {
      console.error(`目标已存在: ${dest}\n使用 --force 覆盖（会删除原目录）`)
      process.exit(1)
    }
    fs.rmSync(dest, { recursive: true, force: true })
  }

  ensureDir(path.dirname(dest))
  copyTemplate(KIT_TEMPLATE_DIR, dest)

  const vueConfig = path.join(dest, 'vue.config.js')
  if (fs.existsSync(vueConfig)) {
    patchDevServer(vueConfig)
  }

  const meta = {
    slug,
    workspace: path.resolve(workspace),
    createdAt: new Date().toISOString(),
    templateVersion: TEMPLATE_VERSION,
  }
  if (styleBrief) {
    meta.styleBrief = styleBrief
  }
  fs.writeFileSync(
    path.join(dest, '.ppt-maker-project.json'),
    `${JSON.stringify(meta, null, 2)}\n`,
    'utf8',
  )

  console.log(JSON.stringify({ ok: true, slug, projectPath: dest }, null, 2))
}

main()
