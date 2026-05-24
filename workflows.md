# 工作流规范

## 检索文献

1. 应用 `literature-search`。
2. 明确主题、学科、时间范围、语言、文献类型与排除条件；信息不足时先给出默认假设。
3. 拆分概念：核心变量、对象、方法、场景、同义词、中英文关键词。
4. 优先调用 `academic-research` MCP 进行多源检索。
5. 需要补充网页证据时，由用户使用浏览器校验，或由用户在本机 Cursor 另行配置的其他 MCP（本迁移包不包含网页搜索 MCP）。
6. 需要与已有文献库比对时调用 `zotero`。
7. 使用 DOI、PMID、arXiv ID、标题规范化结果去重。
8. 输出候选文献池，并标注检索来源、相关性理由、唯一标识与全文状态。

## 筛选论文

1. 应用 `paper-screening`。
2. 根据用户主题建立纳入标准和排除标准。
3. 先按标题和摘要筛选，再对待定文献补查方法、数据、期刊或全文状态。
4. 输出“纳入、待定、排除”三类结果，并写明理由。
5. 不因标题相似直接判定重复，优先用 DOI、PMID、arXiv ID 与作者年份校验。

## 总结论文

1. 应用 `paper-summary`。
2. 优先读取全文或 Zotero 附件；无法读取全文时明确标注“基于摘要/元数据”。
3. 输出研究问题、方法与数据、主要结论、局限、与当前主题的关系。
4. 区分作者结论与智能体推断，不扩大结论适用范围。

## 整理引用

1. 应用 `citation-export`。
2. 使用 `academic-research` 校验 DOI、期刊、年份等元数据。
3. 如用户使用 Zotero，优先调用 `zotero` 导出 BibTeX 或检查已有条目。
4. 按用户指定格式输出；未指定时默认输出 Markdown 清单，并可补充 BibTeX。
5. 缺失字段标注“缺失”，不要补造。

## 分析研究空白

1. 应用 `research-gap-analysis`。
2. 仅基于已筛选文献归纳研究脉络、共识、争议和空白。
3. 每个研究空白都必须给出文献依据和可研究问题。
4. 不把“文献少”直接等同于“有研究价值”，必须说明理论或实践意义。

## 生成 PPT（分流入口）

- **默认**：`ppt-maker`（见下节「高保真视觉 PPT」）。
- **学术快出**：用户明确答辩 / 开题 / 文献综述 / 要快出 pptx → `academic-ppt-builder` → `deck-builder` 或 `ppt-markdown`。
- **商业 HTML**：Pitch → `slides` + `design-system` scripts。
- **串联**：文献链 → academic 大纲确认 → ppt-maker 高保真（`output-templates.md` 映射）。

### 学术快出（academic-ppt-builder）

1. 应用 `academic-ppt-builder`。
2. 确认汇报场景、页数、时长、语言和风格。
3. 先输出幻灯片大纲供用户确认。
4. 若用户要求生成文件：
   - 结构化演示文稿优先调用 `deck-builder`。
   - Markdown 已成稿时调用 `ppt-markdown`。
5. PPT 文件名优先使用英文，正文内容优先中文。
6. 每页标题应是观点句，不只是名词短语。
7. 用户随后要高保真视觉 → 衔接 `ppt-maker`。

## 高保真视觉 PPT（ppt-maker）

1. 应用 `ppt-maker`（用户说「做 PPT」默认此路径）。
2. 确认素材、页数、风格 brief；无风格描述时追问 1–2 题。
3. 运行 `check-node.mjs` → `scaffold.mjs` 创建 `ppt-projects/{slug}/`。
4. 调用 `ui-ux-pro-max`（`search.py --design-system --persist`）写 `design-tokens.css`。
5. 素材 → `public/assets/materials/`（英文文件名）；内容 → `slides.js`（参考副本内 `docs/slides-schema.md`）。
6. 副本内 `npm install` && `npm run serve`（后台）；告知用户实际 URL。
7. 用户在浏览器顶栏自行导出（默认不代点、不跑 CLI export）。
8. 若用户随后要快出 pptx 且已有大纲 → 可切换 `academic-ppt-builder` + MCP。

## UI/UX 设计（React Native）

1. 应用 `ui-ux-pro-max`。
2. 先运行 `search.py --design-system` 获取 pattern、style、colors、typography 等推荐（命令路径以 `%USERPROFILE%\.cursor\skills\ui-ux-pro-max\` 为准）。
3. 需要跨会话持久化时，在项目工作目录使用 `--persist`；会在**当前项目**下生成 `design-system/MASTER.md`（与 Skill 包内 `design-system/` 目录不是同一位置）。
4. 需要品牌层规范时联动 `brand` → `design-system` → `ui-styling`。
5. Logo/CIP/图标任务应用 `design`；融资或产品路演幻灯片应用 `slides` + design-system scripts。
6. **PPT 路径区分**：泛称「做 PPT」→ `ppt-maker` + `ui-ux-pro-max`；学术快出 → `academic-ppt-builder` + deck-builder MCP；商业 Pitch → `slides`。
7. `banner-design` 的 AI 生成步骤依赖未打包 Skill（ai-artist、ai-multimodal、chrome-devtools），无则仅输出规格与 references 指导。

## 编码、审查与重构

1. 应用 `karpathy-guidelines`（编写、审查、重构、减少过度复杂或定义可验证成功标准时）。
2. 按四原则执行：编码前思考 → 简洁优先 → 精准修改 → 目标驱动执行。
3. 多步骤任务列出「步骤 → 验证」计划；bug 修复优先写重现测试。
4. 需要代码对比示例时读取 Skill 包内 [examples.md](../skills/karpathy-guidelines/examples.md)。
5. Cursor 项目已通过 `-InstallRules` 安装 `karpathy-guidelines.mdc` 时，规则为 alwaysApply 基线；Skill 用于显式深度应用与示例引用。
