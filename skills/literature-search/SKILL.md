---
name: literature-search
description: 系统检索学术文献，构造检索式，调用 academic-research、zotero；需馆内/VPN全文或知网时联动 campus-net-onboarding 与 campus-net MCP。在用户要求查文献、找论文、做综述或限定数据库检索时使用。
---

# 文献检索

## 适用范围

用于从研究问题出发生成可复现的检索过程，优先调用 `academic-research` MCP，必要时使用 `zotero` 与本地库比对。**补充网页线索**时由用户浏览器或用户自行在 Cursor 配置的其它 MCP 完成；本迁移包不内置网页搜索 MCP。

### 与本任务相邻、可主动联动的 Cursor 技能

| 场景 | 建议调用的技能 |
|------|----------------|
| **校园网馆藏 / VPN / 知网 CNKI PDF** | **campus-net-onboarding**（首配问询与 onboard；执行时配合 **`campus-net` MCP**） |
| 单篇深读卡片 | paper-summary |
| 系统综述初筛纳入排除 | paper-screening |
| 参考文献格式导出 | citation-export |
| 研究空白与综述框架 | research-gap-analysis |
| 汇报类成稿结构 | academic-ppt-builder |

若任务涉及**馆内订阅全文抓取、校外 VPN 自动登录或通过机构入口下载**：在调用 **`campus-net`** 的 `download_*` / `ensure_auth` 之前，须先 **`get_active_profile`**；未完成学校配置时，**必须先按技能 `campus-net-onboarding` 的流程**调用 `discover_school_profile`→`onboard_school`→`save_school_profile`→`set_active_profile`，再下载。

### campus-net MCP 在校内全文场景的典型调用顺序

`get_active_profile` →（若 needs_onboarding 则 onboarding 链路）→ `list_school_profiles` / `set_active_profile` → `detect_network` → `ensure_auth` → `resolve_fulltext_url` 或 `download_paper` / `download_cnki`；遇验证码时 `import_browser_cookies`。细节以技能 **campus-net-onboarding** 为准。

## 工作流

1. 明确主题、学科、时间范围、语言、文献类型与排除条件；信息不足时先给出默认假设。
2. 拆分概念：核心变量、对象、方法、场景、同义词、中英文关键词。
3. 构造 2 到 4 组检索式：宽泛检索、精确检索、近五年检索、经典文献检索。
4. 优先使用 `academic-research` 覆盖 OpenAlex、Semantic Scholar、CrossRef、PubMed、arXiv、Google Scholar、ORCID、Unpaywall。
5. 对医学、生命科学主题优先 PubMed；对计算机、人工智能、数学、物理主题优先 arXiv 与 Semantic Scholar。
6. 使用 DOI、PMID、arXiv ID、标题规范化结果去重。
7. 输出候选文献池，标注检索来源、命中关键词、相关性理由与是否可获取全文。

## 输出格式

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

## 约束

- 不把单次搜索结果当作完整综述结论。
- 不伪造 DOI、期刊、年份或引用量；缺失时标注“未检得”。
- 引用量只作为辅助信号，不作为质量结论。
