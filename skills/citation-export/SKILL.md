---
name: citation-export
description: 整理参考文献并导出 APA、GB/T 7714、BibTeX 或 Markdown 引用清单。在用户要求生成参考文献、规范引用格式、导出 BibTeX、校验 DOI 或整理 Zotero 文献时使用。
---

# 引用导出

## 适用范围

用于将检索或筛选后的文献转换为指定引用格式。优先使用 `zotero` MCP 和 `academic-research` MCP 校验元数据。

## 工作流

1. 确认引用格式：APA 7、GB/T 7714、BibTeX、Markdown 或用户指定格式。
2. 校验每条文献的作者、年份、题名、来源、卷期页码、DOI 或 URL。
3. 对缺失字段标注“缺失”，不要补造。
4. 同一文献多来源冲突时，优先 DOI/CrossRef/出版社页面，其次 Zotero，本地手录信息最后。
5. 输出引用清单和异常项。

## 输出格式

```markdown
## 参考文献
1. ...

## 元数据异常
- 文献：
  - 问题：
  - 建议处理：
```

## BibTeX 输出要求

- key 使用 `authorYearKeyword`，仅含英文字母、数字与短横线。
- DOI 字段不加 `https://doi.org/` 前缀，除非用户要求 URL 形式。
- 中文文献保留中文题名。

## 约束

- 不伪造出版社、页码、卷期或 DOI。
- 引用格式有不确定项时，优先说明不确定原因。
