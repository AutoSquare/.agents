import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

/** ppt-maker 技能根目录 */
export const SKILL_ROOT = path.resolve(__dirname, '..')

/** 内嵌模板目录 */
export const KIT_TEMPLATE_DIR = path.join(SKILL_ROOT, 'kit-template')

/**
 * 解析 kit-template 上游目录（sync-template 维护者用）。
 * 顺序：--upstream → 工作区 ppt-maker-kit → ppt_style
 * @param {string[]|undefined} argv
 * @returns {string}
 */
export function resolveKitSourceDir(argv = process.argv.slice(2)) {
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--upstream' && argv[i + 1]) {
      const upstream = path.resolve(argv[++i])
      if (!fs.existsSync(upstream)) {
        throw new Error(`--upstream 路径不存在: ${upstream}`)
      }
      return upstream
    }
  }
  const workspaceRoot = path.resolve(SKILL_ROOT, '..')
  const kit = path.join(workspaceRoot, 'ppt-maker-kit')
  if (fs.existsSync(kit)) return kit
  const style = path.join(workspaceRoot, 'ppt_style')
  if (fs.existsSync(style)) return style
  return kit
}

/** 开发基座目录（sync-template 源；无上游时可能不存在） */
export const KIT_SOURCE_DIR = resolveKitSourceDir()

export const TEMPLATE_VERSION = 'ppt-maker-kit@0.2.0'

const SLUG_RE = /^[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?$/

/**
 * 解析并校验英文 slug。
 * @param {string} raw
 * @returns {string}
 */
export function normalizeSlug(raw) {
  const slug = String(raw || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, '-')
    .replace(/^-+|-+$/g, '')
  if (!slug || !SLUG_RE.test(slug)) {
    throw new Error(
      `无效 slug「${raw}」：仅允许小写 a-z、0-9、连字符，长度 1–48，且不能以连字符开头或结尾。`,
    )
  }
  return slug
}

/**
 * 生成默认 slug：deck-YYYYMMDD-HHmm
 * @returns {string}
 */
export function defaultSlug() {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`
  return `deck-${stamp}`
}

/**
 * @param {string} workspace
 * @param {string} slug
 * @returns {string}
 */
export function projectDir(workspace, slug) {
  return path.join(path.resolve(workspace), 'ppt-projects', slug)
}

/**
 * @param {string} dir
 */
export function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true })
}
