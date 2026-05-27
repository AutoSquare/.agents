#!/usr/bin/env node
/**
 * 从 ui-ux-pro-max 产出的 MASTER.md 映射到 design-tokens.css。
 * 用法: node map-design-system.mjs --project ppt-projects/<slug>
 */
import fs from 'fs'
import path from 'path'

const DEFAULT_EDITORIAL = {
  accentWarm: '#C2410C',
  background: '#FCFBF9',
}

const REQUIRED_VARS = [
  '--color-primary',
  '--color-accent',
  '--color-background',
  '--color-foreground',
]

function parseArgs(argv) {
  const out = { project: null }
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--project' && argv[i + 1]) out.project = argv[++i]
  }
  return out
}

function findMasterMd(projectRoot) {
  const designDir = path.join(projectRoot, 'design-system')
  if (!fs.existsSync(designDir)) return null
  const candidates = []
  const walk = (dir) => {
    for (const name of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, name.name)
      if (name.isDirectory()) walk(full)
      else if (name.name === 'MASTER.md') candidates.push(full)
    }
  }
  walk(designDir)
  if (!candidates.length) return null
  let best = candidates[0]
  let bestScore = 0
  for (const c of candidates) {
    const text = fs.readFileSync(c, 'utf8')
    const score = (text.match(/\|\s*[^|\n]+\|\s*`#[0-9A-Fa-f]{3,8}`\s*\|\s*`--color-/g) || [])
      .length
    if (score > bestScore) {
      bestScore = score
      best = c
    }
  }
  return best
}

function parseColorTable(masterText) {
  const vars = {}
  const rowRe =
    /\|\s*[^|\n]+\|\s*`(#[0-9A-Fa-f]{3,8})`\s*\|\s*`(--color-[a-z-]+)`\s*\|/g
  let m
  while ((m = rowRe.exec(masterText)) !== null) {
    vars[m[2]] = m[1]
  }
  return vars
}

function parseCssImport(masterText) {
  const block = masterText.match(/```css\s*([\s\S]*?)```/i)
  if (!block) return null
  const imp = block[1].match(/@import\s+url\([^)]+\)\s*;/)
  return imp ? imp[0] : null
}

function parseFontNames(masterText) {
  const heading = masterText.match(/\*\*Heading Font:\*\*\s*(.+)/i)
  const body = masterText.match(/\*\*Body Font:\*\*\s*(.+)/i)
  return {
    heading: heading ? heading[1].trim() : null,
    body: body ? body[1].trim() : null,
  }
}

function buildTokensCss(colors, cssImport, fonts) {
  const c = (k, fallback) => colors[k] || fallback
  const primary = c('--color-primary', '#0F172A')
  const background = c('--color-background', '#F8FAFC')
  const accent = c('--color-accent', '#0369A1')
  const importLine =
    cssImport ||
    "@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Rubik:wght@300;400;500;600;700&display=swap');"
  const headingFont = fonts.heading
    ? `'${fonts.heading}', Georgia, 'Times New Roman', serif`
    : "'Outfit', system-ui, sans-serif"
  const bodyFont = fonts.body
    ? `'${fonts.body}', system-ui, sans-serif`
    : "'Rubik', system-ui, sans-serif"

  return `${importLine}

:root {
  --color-primary: ${primary};
  --color-primary-soft: ${c('--color-secondary', '#334155')};
  --color-on-primary: ${c('--color-on-primary', '#FFFFFF')};
  --color-accent: ${accent};
  --color-accent-light: ${background};
  --color-accent-warm: ${accent};
  --color-background: ${background};
  --color-surface: ${background};
  --color-canvas: ${c('--color-border', '#E2E8F0')};
  --color-foreground: ${c('--color-foreground', '#020617')};
  --color-secondary: ${c('--color-secondary', '#334155')};
  --color-muted-text: ${c('--color-muted', c('--color-secondary', '#64748B'))};
  --color-border: ${c('--color-border', '#E2E8F0')};
  --color-border-light: ${c('--color-border', '#E2E8F0')};
  --font-heading: ${headingFont};
  --font-body: ${bodyFont};
  --slide-max-width: 1024px;
  --slide-gap: 64px;
  --slide-radius: 6px;
  --slide-shadow: 0 32px 64px -16px rgba(15, 23, 42, 0.08), 0 0 0 1px rgba(15, 23, 42, 0.02);
  --card-radius: 4px;
  --transition-fast: 240ms cubic-bezier(0.16, 1, 0.3, 1);
  --focus-ring: 0 0 0 3px rgba(3, 105, 161, 0.35);
  --z-nav: 100;
  --z-skip: 1000;
  --type-display: clamp(1.125rem, 2.2vw, 1.375rem);
  --type-title: clamp(0.875rem, 1.6vw, 1rem);
  --type-body: 0.75rem;
  --type-caption: 0.6875rem;
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-fast: 0ms;
  }
}
`
}

function isStillDefaultEditorial(cssText) {
  return (
    cssText.includes(`--color-accent-warm: ${DEFAULT_EDITORIAL.accentWarm}`) &&
    cssText.includes(`--color-background: ${DEFAULT_EDITORIAL.background}`)
  )
}

function main() {
  const { project } = parseArgs(process.argv.slice(2))
  if (!project) {
    console.error('用法: node map-design-system.mjs --project <ppt-projects/slug 路径>')
    process.exit(1)
  }
  const projectRoot = path.resolve(project)
  const masterPath = findMasterMd(projectRoot)
  if (!masterPath) {
    console.error('未找到 design-system/*/MASTER.md，请先运行 ui-ux-pro-max')
    process.exit(1)
  }
  const masterText = fs.readFileSync(masterPath, 'utf8')
  const colors = parseColorTable(masterText)
  const missing = REQUIRED_VARS.filter((k) => !colors[k])
  if (missing.length) {
    console.error(`MASTER.md 缺少必填色值: ${missing.join(', ')}`)
    process.exit(1)
  }
  const cssImport = parseCssImport(masterText)
  const fonts = parseFontNames(masterText)
  const outCss = buildTokensCss(colors, cssImport, fonts)
  if (isStillDefaultEditorial(outCss)) {
    console.error('映射结果仍为 Editorial 默认色，请检查 MASTER.md 或 styleBrief')
    process.exit(1)
  }
  const tokensPath = path.join(projectRoot, 'src/styles/design-tokens.css')
  fs.writeFileSync(tokensPath, outCss, 'utf8')
  console.log(JSON.stringify({ ok: true, masterPath, tokensPath }, null, 2))
}

main()
