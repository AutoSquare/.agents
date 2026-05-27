# ppt-maker 参考

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/slug.mjs --generate` | 生成 deck-YYYYMMDD-HHmm |
| `scripts/scaffold.mjs` | 复制 kit-template → ppt-projects |
| `scripts/map-design-system.mjs --project <path>` | MASTER.md → design-tokens.css |
| `scripts/validate-project.mjs --project <path>` | tokens / slides / 打标 / 红区 checksum |
| `scripts/check-node.mjs` | Node 18+ |
| `kit-template/scripts/inspect-pptx.mjs` | 维护者检查 pptx 结构 |

映射规格：[scripts/TOKEN_MAP.md](scripts/TOKEN_MAP.md)

## Layout 选型

| 页型 | layout | 关键 props |
|------|--------|------------|
| 封面 | `cover` | `partnerLogo`, `kicker`, `image` |
| 目录 | `catalog` | `catalogPreview`：**4 image + hub** |
| 多卡/流程 | `features` | `tags`, `flowBar`, `duoPanel` |
| 图文分栏 | `split` | `imageFrame: 'browser'`, `badges` |
| 成果/证书 | `evidence` | `stats`, `table`, stack 多图 |
| 陈述/封底 | `statement` | `brandLogos` |
| 双栏案例 | `dual` | `cases`, `layoutRatio` |

**dual 非必须**（L55）；按内容选 layout，勿死守双栏。详见 [VISUAL.md](VISUAL.md)。

## 内容与素材约束（L1 / references）

| 约束 | 说明 |
|------|------|
| 主体内容 | 与用户 PDF/素材一致；可适量增减页，**不改主线** |
| Logo 三件套 | 主标识 + 合作方 Logo + 用户指定项（见 EXAMPLES §8） |
| 素材路径 | `public/assets/materials/` 英文文件名 |
| 懒加载 | 导出前滚动 storyboard 加载全部图片 |

## layout 变体索引（docs/10 抽象）

| 变体 | layout | 备注 |
|------|--------|------|
| flow 四卡 | features + flowBar | slide5 导出锚点 |
| duo + hub | features + duoPanel | ch04 L230 勿 1fr 压扁 |
| agent | statement + agentFlow | 无多余 features 卡 |
| browser 16:9 | split + imageFrame browser | PM-VIS-09 无 HUD 冲突 |
| evidence stack | evidence + stats/table | 叠露边 |

## 条件决策树

```
用户说「丑 / 难看」
  → 整页 redesign + ui-ux-pro-max
  → browser screenshot
  → 禁止只调 padding

用户说「导出不对 / 和预览不一致」
  → 读 EXPORT.md
  → 黄区补 export-layer 打标
  → 禁止改红区 + 禁止 Playwright

用户说「叠了 / 重叠」
  → browser **逐页** 截图 / CDP
  → flex 链 min-height:0（slide-frame__body → layout → card）
  → dual 禁内嵌 hero；catalog 查溢出；evidence stack 露边

用户说「预览和 slide 分不清 / 目录字看不见 / 内容怎么变了」
  → 读 PREVIEW-CHROME.md
  → 检查 :root vs .slide-frame__canvas 双层 token
  → catalog 浅底 chip 用 --color-on-light-surface
  → 勿改 slides.js 文案（AP-15）

新建 Pitch deck（未指定沿用样例）
  → grill-me 顺序 grill（每轮 1 题）→ 全部闭合后共识表格
  → 禁止默认 autosquare-pitch（AP-13）

用户说「不对称 / 缺一块 / 难看」
  → cover：meta 列数 = 项数，推荐 5 项
  → catalog：4 预览图 + hub overlay，禁止 3+1 空格子
  → 读 LAYOUT-CRAFT.md §1–2

用户纠正文案
  → 只改 slides.js 对应字段

新增自定义 layout
  → 复制内置 layout 骨架
  → export-layer-fg/bg + SlideFrame 注册
  → validate 黄区通过
```

## 反模式速查（AP-01～12）

| AP | 触发 | 正确做法 |
|----|------|----------|
| 01 | 丑 | 整页重做，非微调 |
| 02 | 交付 | browser 实看 |
| 03 | 浅色系 | Light styleBrief + map |
| 04 | Logo 裁切 | 白底 contain；cover 勿圆形强裁宽幅 Logo（ch02 L166） |
| 05 | 留白重 | 提高密度；glass/card 层次（ch02 L166） |
| 06 | 重叠 | 逐页 browser + flex 链；dual 禁 hero（LAYOUT-CRAFT §3） |
| 07 | 对称 | cover meta 等宽；catalog 2×2 满图 + hub；brand 镜像 |
| 08 | 官网截图 | split `imageFrame: 'browser'` + 16:9（ch04 L219） |
| 09 | 证书叠图 | evidence stack + stats/table（ch04 L246） |
| 10 | 文案纠正 | 只改 slides.js |
| 11 | 导出不一致 | 只改 export 链路 |
| 12 | 导出失败 | 打标，不动已验收 UI |
| 13 | 未 intake 即开工 | grill-me → styleBrief；禁默认 autosquare |
| 14 | catalog 白底字 invisible | 双层 token + --color-on-light-surface |
| 15 | 「内容变了」 | 先查 CSS 对比度，勿动 slides.js |
| 16 | dark 舞台+slide | 浅 --color-stage + slide 边框 |

## `.ppt-maker-project.json`

| 字段 | 说明 |
|------|------|
| `styleBrief` | 用户风格描述 |
| `designSystemQuery` | ui-ux 检索词（validate 必填） |
| `templateVersion` | 如 `ppt-maker-kit@0.2.0` |
| `tokenMapDebt` | 手改 token 时标记 WARN |

## 故障排除

| 现象 | 处理 |
|------|------|
| validate 红区 fail | 撤销对 export utils 的修改 |
| assert 打标不完整 | 黄区 layout 补 `export-layer-fg` |
| map 脚本失败 | 检查 MASTER.md；用户确认后可 `tokenMapDebt` |
| 中文路径 npm 失败 | workspace 改纯英文目录 |

## 更多

- 版式工艺：[LAYOUT-CRAFT.md](LAYOUT-CRAFT.md)
- 视觉质量：[VISUAL.md](VISUAL.md)
- 预览外壳：[PREVIEW-CHROME.md](PREVIEW-CHROME.md)
- 导出契约：[EXPORT.md](EXPORT.md)
- 示例：[EXAMPLES.md](EXAMPLES.md)
- academic 大纲映射：`.agents/output-templates.md`
