#!/usr/bin/env node
/**
 * 检测 Node.js / npm；Windows 可选 winget 安装 LTS。
 * 用法: node check-node.mjs
 *       node check-node.mjs --install
 */
import { spawnSync } from 'child_process'

const MIN_MAJOR = 18
const install = process.argv.includes('--install')

function run(cmd, cmdArgs) {
  const r = spawnSync(cmd, cmdArgs, { encoding: 'utf8', shell: true })
  return {
    ok: r.status === 0,
    stdout: (r.stdout || '').trim(),
    stderr: (r.stderr || '').trim(),
    status: r.status,
  }
}

function parseMajor(versionOutput) {
  const m = versionOutput.match(/(\d+)/)
  return m ? Number(m[1]) : 0
}

const node = run('node', ['-v'])
const npm = run('npm', ['-v'])

if (node.ok && npm.ok) {
  const nodeMajor = parseMajor(node.stdout)
  if (nodeMajor < MIN_MAJOR) {
    console.error(`Node 版本过低：${node.stdout}，建议 >= ${MIN_MAJOR}`)
    process.exit(1)
  }
  console.log(JSON.stringify({ ok: true, node: node.stdout, npm: npm.stdout }, null, 2))
  process.exit(0)
}

if (!install) {
  console.error(
    JSON.stringify(
      {
        ok: false,
        node: node.stdout || null,
        npm: npm.stdout || null,
        hint: '未检测到 node/npm。Windows 可运行: node "%USERPROFILE%\\.cursor\\skills\\ppt-maker\\scripts\\check-node.mjs" --install（沙箱: node ppt-maker/scripts/check-node.mjs --install）',
      },
      null,
      2,
    ),
  )
  process.exit(1)
}

if (process.platform !== 'win32') {
  console.error('自动安装仅支持 Windows（winget）。请从 https://nodejs.org 手动安装后重开终端。')
  process.exit(1)
}

console.log('正在通过 winget 安装 Node.js LTS…')
const winget = run('winget', [
  'install',
  'OpenJS.NodeJS.LTS',
  '--accept-package-agreements',
  '--accept-source-agreements',
])

if (!winget.ok) {
  console.error(winget.stderr || winget.stdout || 'winget 安装失败')
  process.exit(1)
}

console.log('安装完成。请关闭并重新打开终端（或 Cursor 终端）后再执行 npm install。')
process.exit(0)
