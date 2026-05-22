#!/usr/bin/env node
/**
 * 将沙箱 ppt-maker/ 同步到 .agents/skills/ppt-maker/（发布副本）。
 * 用法: node sync-to-agents.mjs [--dry-run]
 */
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { SKILL_ROOT } from './_paths.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const AGENTS_TARGET = path.resolve(SKILL_ROOT, '..', '.agents', 'skills', 'ppt-maker')
const EXCLUDE_DIRS = new Set(['node_modules', 'dist', 'output', '.cache', '.git'])
const EXCLUDE_FILES = new Set(['.DS_Store'])

function parseArgs(argv) {
  return { dryRun: argv.includes('--dry-run') }
}

function shouldSkip(rel) {
  const parts = rel.split(/[/\\]/).filter(Boolean)
  if (parts.some((p) => EXCLUDE_DIRS.has(p))) return true
  const base = parts[parts.length - 1]
  return Boolean(base && EXCLUDE_FILES.has(base))
}

function collectFiles(src, rel = '', acc = []) {
  for (const ent of fs.readdirSync(src, { withFileTypes: true })) {
    const childRel = rel ? `${rel}/${ent.name}` : ent.name
    if (shouldSkip(childRel)) continue
    const full = path.join(src, ent.name)
    if (ent.isDirectory()) {
      collectFiles(full, childRel, acc)
    } else if (ent.isFile()) {
      acc.push({ rel: childRel, full })
    }
  }
  return acc
}

function copyRecursive(src, dest, rel = '') {
  for (const ent of fs.readdirSync(src, { withFileTypes: true })) {
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
  const { dryRun } = parseArgs(process.argv.slice(2))
  if (!fs.existsSync(SKILL_ROOT)) {
    console.error(`未找到沙箱目录: ${SKILL_ROOT}`)
    process.exit(1)
  }
  const files = collectFiles(SKILL_ROOT)
  const totalBytes = files.reduce((sum, f) => sum + fs.statSync(f.full).size, 0)
  if (dryRun) {
    console.log(`[dry-run] 源: ${SKILL_ROOT}`)
    console.log(`[dry-run] 目标: ${AGENTS_TARGET}`)
    console.log(`[dry-run] 文件数: ${files.length}，合计 ${(totalBytes / 1024).toFixed(1)} KB`)
    return
  }
  if (fs.existsSync(AGENTS_TARGET)) {
    fs.rmSync(AGENTS_TARGET, { recursive: true, force: true })
  }
  fs.mkdirSync(AGENTS_TARGET, { recursive: true })
  copyRecursive(SKILL_ROOT, AGENTS_TARGET)
  console.log(`已同步 ppt-maker → ${AGENTS_TARGET}`)
  console.log(`文件数: ${files.length}，合计 ${(totalBytes / 1024).toFixed(1)} KB`)
}

main()
