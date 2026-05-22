#!/usr/bin/env node
/**
 * 校验或生成英文项目 slug。
 * 用法: node slug.mjs [slug]
 *        node slug.mjs --generate
 */
import { defaultSlug, normalizeSlug } from './_paths.mjs'

const args = process.argv.slice(2)

if (args.includes('--generate') || args.length === 0) {
  console.log(defaultSlug())
  process.exit(0)
}

try {
  console.log(normalizeSlug(args[0]))
} catch (err) {
  console.error(err.message)
  process.exit(1)
}
