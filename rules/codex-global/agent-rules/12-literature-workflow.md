# 文献工作流

## 触发条件

查文献、下全文、筛论文、写综述、整理引用、做学术 PPT 或汇报材料时读取。

## Skill 与 MCP 选用顺序

| 用户意图 | 优先 Skill | 常用 MCP |
| --- | --- | --- |
| 查文献、检索式、候选池 | `literature-search` | `academic-research`、`zotero` |
| 筛文献、纳入排除 | `paper-screening` | - |
| 读论文、文献卡片 | `paper-summary` | - |
| 参考文献表、BibTeX | `citation-export` | `zotero` |
| 研究空白、选题 | `research-gap-analysis` | - |
| 校内/VPN 全文 PDF | `campus-net-onboarding` | `campus-net` |
| 做 PPT / 幻灯片（默认） | `ppt-maker` | 联动 `ui-ux-pro-max` |
| 学术快出 PPT | `academic-ppt-builder` | `deck-builder`、`ppt-markdown` |

## 全文下载

- 优先 `download_papers` / `download_paper`。
- 失败时告知 `manual_download_required.md`，勿要求用户向对话粘贴 Cookie。
