---
name: campus-net-onboarding
description: 在用户需要校园网馆藏全文、校外 VPN 文献下载或未配置激活学校时，引导 MCP campus-net 的 Profile 选择与 onboard_school/save_school_profile 全流程；明确联动 literature-search、paper-summary、citation-export、academic-ppt-builder 及 academic-research、zotero 等 MCP。
---

# 校园网馆藏 MCP 引导

## 适用范围

在用户需要：**自动判断是否具备校内馆藏条件**、**网页 VPN/CAS 自动登录抓取 PDF**、**知网 CNKI（机构入口）下载**或**首次配置学校**时使用。依赖已启用的 `campus-net` MCP。

## 须联动的 Cursor 技能

按任务择优选用（本技能不承担文献元数据综述主流程）：

| 技能 | 何时调用 |
|------|----------|
| **literature-search** | 从研究问题出检索式、多库候选文献池、snowball/open_access 等策略衔接 |
| **paper-summary** | 单篇/多篇精读摘要、方法与局限 |
| **paper-screening** | 系统性纳入排除与筛选日志 |
| **citation-export** | 导出 GB/T/BibTeX 等参考文献表 |
| **academic-ppt-builder** | 将综述或汇报素材生成演示结构 |
| **research-gap-analysis** | 在已定文献集合上归纳研究缺口与选题 |

说明：馆藏认证与 Profile 全流程以本技能 + **`campus-net` MCP** 为主；检索与写作类输出由上表技能承接。

### 须联动或并行的 MCP（工具名）

- **`campus-net`**（必选，本场景核心）：见下文「必选流程」中列出的工具名。
- **`academic-research`**：在用户尚未获得 DOI/开放获取链时，`smart_search` / `find_paper` / `open_access`。
- **网页检索**：本迁移包未内置网页搜索 MCP；无内置学校 Profile 时，用 `discover_school_profile` 返回的 **`suggested_web_search_queries`**，指导用户**在浏览器**中检索图书馆 HTTPS、VPN、`doi_resolver_template` 等，并将用户确认的 URL 写入 `onboard_school`。
- **`zotero`**：条目与附件同步时 `zotero_import`（或等价写入工具，以本机 MCP 为准）。

## Agent 必选流程

### 前置检查

在执行 `campus-net` 的 `download_paper`、`download_cnki`、`ensure_auth` **之前**，必须先调用 `get_active_profile`。

- 若 `needs_onboarding == true`，**不得猜测 school_id**。向用户问询**学校全称**及获取全文的主要方式（在校 IP、校外网页 VPN、是否需 CNKI）。
- 若用户提供简称或中文校名：调用 `discover_school_profile`；若内置命中，直接使用返回的 `school_id`。

### Profile 选择与新建

1. `list_school_profiles` — 枚举 `builtin` 与 `user` 两类。
2. 若与用户学校匹配：**`set_active_profile(school_id)`**。
3. 若无内置匹配：
   - 使用 `discover_school_profile` 的 `suggested_web_search_queries`，引导用户**在浏览器**检索并确认图书馆主页、HTTPS 校外访问入口、`doi_resolver_template`，将结果填入 **`onboard_school`**（本包不依赖网页搜索 MCP）。
   - 将确认后的结构化字段送入 **`onboard_school`**，必要时 `base_profile_school_id` 选相近内置校做模板。
   - 用户校对 `preview_yaml` 后：**`save_school_profile`**（`yaml_text=` 终审文本，`set_active=true`）。

### 凭据与安全

1. Profile 指定 `credential_env.username` / `password`（默认 `CAMPUS_USERNAME`、`CAMPUS_PASSWORD`）。
2. 提示用户在系统环境变量或 Cursor MCP server `env` 中配置变量名对应的值；**不向对话回显明文密码**。
3. 遇验证码或多因素：**`import_browser_cookies`** 导入导出 Cookie JSON；或暂改 `headed_browser=true` 仅在用户可见环境下排障。

### 下载与馆藏联合工作流建议

1. 元数据与开放获取：**`academic-research`**（`smart_search` / `find_paper` / `open_access`）。
2. 环境与会话：**`detect_network`** → **`ensure_auth`**（`cas_vpn`/`ip_only`）。
3. 全文：
   - 单篇：**`download_paper`**（可选 `title` 便于失败清单展示）。
   - 多篇：**`download_papers`**（`dois` 列表；可选 `titles` 与 `dois` 一一对应）。
   - 落地目录默认为工作区 `papers/` 或环境变量 `CAMPUS_OUTPUT_DIR`。
4. CNKI：**`download_cnki`** — 须在 Profile 启用 `cnki` 并提供有效的 `cnki.entry_url`，或直接使用 `cnki_article_url` 详情页 HTTPS。
5. 入库：**`zotero_import`**。

### 自动下载失败时的手动清单（必读）

`download_paper` / `download_papers` / `download_cnki` 在**未能保存 PDF** 时，会在输出目录生成或更新：

```text
{output_dir}/manual_download_required.md
```

Agent **必须**在回复用户时：

1. 说明**未能自动下载的总体原因**（可读该 Markdown 开头「未能自动下载的原因」一节，勿让用户自行翻账本）。
2. 给出 **`manual_download_report_path`** 的完整路径。
3. 若部分成功、部分失败，分别列出已下载文件路径与待手动条目数量（`manual_download_pending_count`）。

清单中每篇文献须包含：**标题**、**DOI**、**DOI/出版商/知网可点击链接**、**本篇失败原因**。用户可在校内网或 VPN 浏览器中按链接手动下载 VoR。

成功下载的 DOI 会从待办清单中**自动移除**；同一 `output_dir` 下多次调用会合并更新同一 Markdown。

## 输出要求

回答中须明确当前激活 **school_id**、是否已通过 **CAS/VPN**、已下载 PDF 的**路径**，以及（若有）**`manual_download_required.md`** 路径与待手动篇数。

## 约束

- 仅下载用户有权访问或通过开放获取合法的文献；遵守本校图书馆与数据库使用条款。
- 不把探针误判当作「一定可以下载」的保证；失败后根据 `blocking_missing`、`warnings` 调整 Profile 或由用户手工验证入口。
