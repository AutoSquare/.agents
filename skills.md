# Skills 使用规范

用户级 Skills 目录：

```text
Cursor: %USERPROFILE%\.cursor\skills
Codex:  %USERPROFILE%\.codex\skills
```

## 文献检索与综述

- `campus-net-onboarding`：校园网馆藏 Profile、CAS/VPN、全文下载；失败时汇总 `manual_download_required.md`。
- `literature-search`：系统检索学术文献，构造检索式，调用学术 MCP、网页检索与 Zotero 去重并形成候选文献池。
- `paper-screening`：按研究问题筛选论文，建立纳入排除标准，输出筛选记录。
- `paper-summary`：结构化总结论文，提取研究问题、方法、数据、结论、局限与可引用观点。
- `citation-export`：整理参考文献并导出 APA、GB/T 7714、BibTeX 或 Markdown 引用清单。
- `research-gap-analysis`：基于已筛选文献归纳研究脉络、争议点、证据缺口与后续选题方向。

## PPT 与汇报

- `ppt-maker`：默认路径。Vue 16:9 预览 + 浏览器导出 pptx/zip；须 **grill-me 顺序 intake** + `ui-ux-pro-max`；任务副本在 `ppt-projects/{slug}/`。详见 `skills/ppt-maker/发布说明.md`。
- `academic-ppt-builder`：学术快出。答辩、开题、文献综述或明确要快出 pptx 时，调用 deck-builder / ppt-markdown MCP。

## UI/UX 设计

- `ui-ux-pro-max`：React Native UI/UX 风格检索与设计系统推荐（`search.py --design-system`）；本地 fork 仅列 react-native 技术栈。
- `brand`：品牌指南、色彩/字体规范与资产组织。
- `design-system`：设计令牌与幻灯片文案/布局/策略检索（含 scripts）。
- `ui-styling`：shadcn/ui 与 Tailwind 配置辅助（需 Node.js）。
- `design`：Logo、CIP、图标检索与 Gemini 图像生成（需 `GEMINI_API_KEY`）。
- `slides`：融资/产品路演幻灯片结构（联动 design-system scripts）。
- `banner-design`：横幅尺寸与风格；完整 AI 生成链需自备 ai-artist / ai-multimodal / chrome-devtools。

## 工程与工作流

- `karpathy-guidelines`：Karpathy 四原则（编码前思考、简洁优先、精准修改、目标驱动执行）；编写/审查/重构代码时使用。
- `diagnose`：面向缺陷与性能回退的诊断循环。
- `tdd`：以红-绿-重构循环做测试驱动开发。
- `prototype`：在敲定设计前搭建一次性原型。
- `improve-codebase-architecture`：发现架构加深机会，提升模块边界与可测性。
- `grill-with-docs`：对照项目文档质询计划，并维护领域术语与 ADR。
- `setup-matt-pocock-skills`：为项目配置工程技能所需的 `docs/agents/` 与问题跟踪说明。
- `triage`：按状态机分拣工单。
- `to-prd`：将当前会话语境整理为 PRD。
- `to-issues`：将计划、规格或 PRD 拆成可领取工单。
- `zoom-out`：从更高层次解释陌生代码或系统区域。

## 个人效率与辅助

- `grill-me`：就计划或设计进行穷追问答。
- `handoff`：将会话整理成交接文档。
- `write-a-skill`：创建新的智能体技能。
- `adapt-mattpocock-skills-for-cursor`：将 mattpocock skills 复制并适配为 Cursor 用户级 Skills。
- `caveman`：极简沟通模式。
- `git-guardrails`：为危险 Git 命令配置 Cursor hooks 护栏。
- `migrate-to-shoehorn`：将测试文件中的 `as` 类型断言迁移到 `@total-typescript/shoehorn`。
- `scaffold-exercises`：创建练习目录结构。
- `setup-pre-commit`：配置 Husky、lint-staged、类型检查与测试。

## 选择规则

- 用户说“查文献、找论文、综述、参考文献”时，优先应用 `literature-search`。
- 用户要求“从这些论文里挑、筛核心文献、系统综述初筛”时，应用 `paper-screening`。
- 用户要求“总结论文、读 PDF、做文献卡片”时，应用 `paper-summary`。
- 用户要求“参考文献格式、BibTeX、GB/T 7714、APA”时，应用 `citation-export`。
- 用户要求“研究空白、选题价值、未来方向”时，应用 `research-gap-analysis`。
- 用户要求“做 PPT、幻灯片、演示文稿、汇报”（未说明形式）时，**默认**应用 `ppt-maker`（联动 `ui-ux-pro-max`）。
- 用户明确要求“答辩、开题、文献综述展示、要快出 pptx、deck-builder”时，应用 `academic-ppt-builder`。
- 用户要求“融资路演、Pitch Deck、商业幻灯片结构”时，应用 `slides`（联动 `design-system` scripts）；「产品发布」若需高保真视觉仍用 `ppt-maker`。
- 用户要求“RN 界面、App UI、设计系统检索、配色字体 UX”时，应用 `ui-ux-pro-max`。
- 用户要求“品牌指南、Logo 规范、视觉识别”时，应用 `brand`；Logo/CIP 生成与检索用 `design`。
- 用户要求“shadcn、Tailwind 组件主题”时，应用 `ui-styling`。
- 用户要求“设计令牌、幻灯片文案公式、布局模式”时，应用 `design-system`。
- 用户要求“横幅、Banner 尺寸规范”时，应用 `banner-design`（生成步骤可能需外部 Skill）。
- 用户要求编写、审查、重构代码，或需减少过度复杂、精准修改、定义可验证成功标准时，应用 `karpathy-guidelines`。
