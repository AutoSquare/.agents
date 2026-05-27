#!/usr/bin/env node
/**
 * 校验 ppt-projects 副本：tokens、slides、export-layer 打标、红区 checksum。
 * 用法: node validate-project.mjs --project ppt-projects/<slug> [--skip-export-core]
 */
import fs from 'fs'
import path from 'path'
import { verifyExportCore } from './export-core.mjs'

const VALID_LAYOUTS = new Set([
  'cover',
  'catalog',
  'statement',
  'features',
  'split',
  'dual',
  'evidence',
])

const DEFAULT_EDITORIAL_WARM = '#C2410C'
const DEFAULT_EDITORIAL_BG = '#FCFBF9'

function parseArgs(argv) {
  const out = { project: null, skipExportCore: false }
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--project' && argv[i + 1]) out.project = argv[++i]
    else if (argv[i] === '--skip-export-core') out.skipExportCore = true
  }
  return out
}

function readProjectMeta(projectRoot) {
  const p = path.join(projectRoot, '.ppt-maker-project.json')
  if (!fs.existsSync(p)) return null
  return JSON.parse(fs.readFileSync(p, 'utf8'))
}

function checkDesignTokens(projectRoot) {
  const errors = []
  const warnings = []
  const tokensPath = path.join(projectRoot, 'src/styles/design-tokens.css')
  if (!fs.existsSync(tokensPath)) {
    errors.push('缺少 src/styles/design-tokens.css')
    return { errors, warnings }
  }
  const text = fs.readFileSync(tokensPath, 'utf8')
  if (text.includes(`--color-accent-warm: ${DEFAULT_EDITORIAL_WARM}`)) {
    errors.push('design-tokens 仍为 Editorial 默认暖色，请运行 map-design-system.mjs')
  }
  if (text.includes(`--color-background: ${DEFAULT_EDITORIAL_BG}`) && text.includes('Crimson Pro')) {
    warnings.push('design-tokens 可能仍为 kit 默认字体/背景')
  }
  return { errors, warnings }
}

function checkSlidesSchema(projectRoot) {
  const errors = []
  const slidesPath = path.join(projectRoot, 'src/data/slides.js')
  if (!fs.existsSync(slidesPath)) {
    errors.push('缺少 src/data/slides.js')
    return errors
  }
  const text = fs.readFileSync(slidesPath, 'utf8')
  const layoutMatches = [...text.matchAll(/layout:\s*['"]([a-z]+)['"]/g)]
  for (const m of layoutMatches) {
    if (!VALID_LAYOUTS.has(m[1])) {
      errors.push(`未知 layout: ${m[1]}`)
    }
  }
  const imageRefs = [...text.matchAll(/['"]([a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|webp|svg))['"]/g)]
  const materialsDir = path.join(projectRoot, 'public/assets/materials')
  for (const m of imageRefs) {
    const file = path.join(materialsDir, m[1])
    if (!fs.existsSync(file) && m[1] !== 'placeholder.png') {
      errors.push(`素材缺失: public/assets/materials/${m[1]}`)
    }
  }
  return errors
}

function checkLayoutTagging(projectRoot) {
  const errors = []
  const layoutsDir = path.join(projectRoot, 'src/components/layouts')
  if (!fs.existsSync(layoutsDir)) return errors
  for (const name of fs.readdirSync(layoutsDir)) {
    if (!name.endsWith('.vue')) continue
    const text = fs.readFileSync(path.join(layoutsDir, name), 'utf8')
    if (!text.includes('export-layer-fg')) {
      errors.push(`layout 缺少 export-layer-fg: ${name}`)
    }
  }
  return errors
}

function main() {
  const { project, skipExportCore } = parseArgs(process.argv.slice(2))
  if (!project) {
    console.error('用法: node validate-project.mjs --project <路径> [--skip-export-core]')
    process.exit(1)
  }
  const projectRoot = path.resolve(project)
  const errors = []
  const warnings = []

  const meta = readProjectMeta(projectRoot)
  if (!meta) {
    errors.push('缺少 .ppt-maker-project.json')
  } else {
    if (!meta.designSystemQuery && !meta.tokenMapDebt) {
      errors.push('未记录 designSystemQuery，须先调用 ui-ux-pro-max')
    }
    if (meta.tokenMapDebt) {
      warnings.push('tokenMapDebt: 存在手改 design-tokens 的技术债')
    }
  }

  const tokenCheck = checkDesignTokens(projectRoot)
  errors.push(...tokenCheck.errors)
  warnings.push(...tokenCheck.warnings)
  errors.push(...checkSlidesSchema(projectRoot))
  errors.push(...checkLayoutTagging(projectRoot))

  if (!skipExportCore) {
    const core = verifyExportCore(projectRoot)
    if (!core.ok) errors.push(...core.errors)
  }

  const result = { ok: errors.length === 0, errors, warnings }
  console.log(JSON.stringify(result, null, 2))
  process.exit(result.ok ? 0 : 1)
}

main()
