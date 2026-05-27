# 输出模板

## 文献候选池

```markdown
## 检索策略
- 研究主题：
- 时间范围：
- 数据源：
- 检索式：

## 候选文献
1. 作者（年份）题名
   - 来源：
   - DOI/PMID/arXiv：
   - 相关性：
   - 全文状态：

## 下一步
- 建议筛选标准：
- 建议追加检索词：
```

## 论文筛选记录

```markdown
## 筛选标准
- 纳入：
- 排除：

## 纳入文献
- 文献：
  - 理由：
  - 用途：

## 待定文献
- 文献：
  - 需要补充的信息：

## 排除文献
- 文献：
  - 排除理由：
```

## 论文摘要

```markdown
## 文献信息
- 作者：
- 年份：
- 题名：
- 来源：
- DOI/链接：

## 结构化摘要
- 研究问题：
- 方法与数据：
- 主要结论：
- 局限：
- 与当前主题的关系：

## 可引用观点
- 观点：
  - 依据：
  - 使用场景：
```

## 研究空白分析

```markdown
## 研究脉络
- 阶段/主题：
  - 代表文献：
  - 主要观点：

## 共识与争议
- 共识：
- 争议：

## 研究空白
1. 空白：
   - 依据：
   - 可研究问题：
   - 可行性：

## 后续检索路线
- 关键词：
- 数据源：
- 应补充的文献类型：
```

## PPT 大纲

```markdown
## PPT 规格
- 场景：
- 时长：
- 页数：
- 风格：

## 幻灯片大纲
1. 标题
   - 核心观点：
   - 页面内容：
   - 讲述提示：
   - 图表建议：

## 生成说明
- 推荐 MCP：
- 输出文件名：
```

## 大纲 → slides.js 映射（ppt-maker 衔接）

将 `academic-ppt-builder` 产出的大纲转为 `ppt-projects/{slug}/src/data/slides.js` 时使用：

| 大纲字段 | slides.js 字段 |
|----------|----------------|
| 页标题 | `title` 或 cover 的 `subtitle` |
| 主题副题 / 章节 | `theme`、`sectionLabel` |
| 页码 | `sectionIndex`（如 `01`） |
| 页面要点 / 正文 | `description` 或 `cases[].description` |
| 封面 | `layout: 'cover'` + `partnerLogo` / `image` |
| 目录 | `layout: 'catalog'` + `catalogPreview` |
| 多要点卡片 | `layout: 'features'` + `features[]` |
| 图文页 | `layout: 'split'` + `image` / `imageFrame` |
| 成果/证书 | `layout: 'evidence'` + `images` / `table` |
| 总结/封底 | `layout: 'statement'` |
| 双栏对比（可选） | `layout: 'dual'` + `cases` 长度 2 |
| 配图 | `public/assets/materials/`（英文名）→ `image` / `images` |

映射完成后：`ui-ux-pro-max` → `map-design-system.mjs` → `validate-project.mjs` → `npm run serve`。
