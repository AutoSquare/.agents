"""将自动下载失败的文献汇总为 Markdown，供用户手动补下。"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LEDGER_DIRNAME = ".campus-net"
LEDGER_FILENAME = "manual_download_queue.json"
REPORT_FILENAME = "manual_download_required.md"

_REASON_ZH: dict[str, str] = {
    "pdf_not_detected_in_chain": (
        "沿 DOI 与出版商候选链接未获取到 PDF 二进制；常见于 ScienceDirect 等机构刊"
        "需要订阅 Cookie、反爬拦截，或尚未完成 CAS/VPN 登录。"
    ),
    "manuscript_pdf_rejected": (
        "已拉取到 PDF，但检测为投稿稿/预印本（如带行号版式），非期刊正式刊出（VoR），"
        "已拒绝保存。"
    ),
    "publisher_blocked": "出版商站点返回机器人验证或访问拒绝，需浏览器机构登录态。",
    "no_candidates": "未解析到可用的 HTTPS 全文候选链接。",
    "no_active_profile": "未设置激活学校 Profile，无法执行馆藏下载。",
    "output_dir_missing": "未指定输出目录。",
    "cnki_session_required": "知网下载需要有效机构会话或 CNKI 详情页 URL。",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _ledger_path(output_dir: Path) -> Path:
    return output_dir / LEDGER_DIRNAME / LEDGER_FILENAME


def _report_path(output_dir: Path) -> Path:
    return output_dir / REPORT_FILENAME


def _item_key(doi: str | None, cnki_article_url: str | None) -> str:
    if doi and doi.strip():
        return f"doi:{doi.strip().removeprefix('https://doi.org/')}"
    if cnki_article_url and cnki_article_url.strip():
        return f"cnki:{cnki_article_url.strip()}"
    return f"unknown:{_utc_now_iso()}"


def human_failure_reason(result: dict[str, Any]) -> str:
    """将 MCP 返回的 reason 转为面向用户的中文说明（不含 hint，避免与补充说明重复）。"""
    code = str(result.get("reason") or result.get("error") or "unknown")
    return _REASON_ZH.get(code, f"下载未成功（代码：{code}）。")


def build_access_links(
    *,
    doi: str | None,
    crossref: dict[str, Any] | None,
    cnki_article_url: str | None,
) -> list[dict[str, str]]:
    """构造便于用户手动打开的链接列表。"""
    links: list[dict[str, str]] = []
    crossref = crossref or {}
    doi_clean = doi.strip().removeprefix("https://doi.org/") if doi else ""

    if doi_clean:
        links.append({"label": "DOI", "url": f"https://doi.org/{doi_clean}"})

    pii = crossref.get("pii")
    if pii:
        links.append(
            {
                "label": "ScienceDirect 文章页",
                "url": f"https://www.sciencedirect.com/science/article/pii/{pii}",
            }
        )
        links.append(
            {
                "label": "ScienceDirect PDF（pdfft）",
                "url": f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft",
            }
        )

    if doi_clean and doi_clean.startswith("10.1007/"):
        links.append(
            {
                "label": "Springer PDF 直链",
                "url": f"https://link.springer.com/content/pdf/{doi_clean}.pdf",
            }
        )
        links.append(
            {
                "label": "Springer 文章页",
                "url": f"https://link.springer.com/article/{doi_clean}",
            }
        )

    article_url = crossref.get("article_url")
    if isinstance(article_url, str) and article_url.startswith("https://"):
        links.append({"label": "Crossref 文章页", "url": article_url})

    if cnki_article_url and cnki_article_url.startswith("https://"):
        links.append({"label": "知网详情页", "url": cnki_article_url})

    return links


def build_access_links_from_result(
    *,
    doi: str | None,
    result: dict[str, Any],
    cnki_article_url: str | None = None,
) -> list[dict[str, str]]:
    crossref = result.get("crossref") if isinstance(result.get("crossref"), dict) else {}
    links = build_access_links(
        doi=doi, crossref=crossref, cnki_article_url=cnki_article_url
    )
    final_url = result.get("final_url")
    if isinstance(final_url, str) and final_url.startswith("https://"):
        if not any(l["url"] == final_url for l in links):
            links.append({"label": "末次访问 URL", "url": final_url})
    return links


def _load_ledger(output_dir: Path) -> dict[str, Any]:
    p = _ledger_path(output_dir)
    if not p.is_file():
        return {"failures": [], "school_id": None, "updated_at": None}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"failures": [], "school_id": None, "updated_at": None}
    if not isinstance(data.get("failures"), list):
        data["failures"] = []
    return data


def _save_ledger(output_dir: Path, data: dict[str, Any]) -> None:
    p = _ledger_path(output_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _utc_now_iso()
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _extract_title(result: dict[str, Any], title: str | None) -> str:
    if title and title.strip():
        return title.strip()
    crossref = result.get("crossref")
    if isinstance(crossref, dict):
        t = crossref.get("title")
        if isinstance(t, str) and t.strip():
            return t.strip()
    return "（标题未知）"


def _build_summary_intro(failures: list[dict[str, Any]], school_id: str | None) -> str:
    n = len(failures)
    if n == 0:
        return "当前无待手动下载条目。"

    reason_codes = Counter(str(f.get("reason_code") or "unknown") for f in failures)
    parts: list[str] = [
        f"共 **{n}** 篇文献未能由 MCP 自动保存 PDF 到本地输出目录。",
    ]
    if school_id:
        parts.append(f"当前激活学校 Profile：`{school_id}`。")

    parts.append("失败类型统计：")
    for code, cnt in reason_codes.most_common():
        zh = _REASON_ZH.get(code, code)
        parts.append(f"- **{cnt}** 篇：{zh}")

    parts.append(
        "常见处理：在校内网或网页 VPN 下用浏览器打开下列链接下载 VoR；"
        "或在 `~/.cursor/campus-net/local.env` 配置 `CAMPUS_USERNAME` / `CAMPUS_PASSWORD` 后重试自动下载。"
    )
    return "\n\n".join(parts)


def render_markdown_report(
    *,
    output_dir: Path,
    school_id: str | None,
    failures: list[dict[str, Any]],
) -> str:
    """生成完整 Markdown 文本。"""
    intro = _build_summary_intro(failures, school_id)
    lines: list[str] = [
        "# 需要手动下载的文献",
        "",
        f"> 生成时间：{_utc_now_iso()}",
        f"> 输出目录：`{output_dir.resolve()}`",
        "",
        "## 未能自动下载的原因",
        "",
        intro,
        "",
        "## 待手动下载列表",
        "",
    ]

    if not failures:
        lines.append("（无失败记录；若曾成功下载，对应条目已从本清单移除。）")
        lines.append("")
        return "\n".join(lines)

    for i, item in enumerate(failures, start=1):
        title = item.get("title") or "（标题未知）"
        lines.append(f"### {i}. {title}")
        lines.append("")
        if item.get("doi"):
            lines.append(f"- **DOI**：`{item['doi']}`")
        if item.get("cnki_article_url"):
            lines.append(f"- **知网 URL**：{item['cnki_article_url']}")
        lines.append(f"- **失败原因**：{item.get('reason_zh') or item.get('reason_code')}")
        hint = str(item.get("hint") or "").strip()
        if hint:
            lines.append(f"- **补充说明**：{hint}")
        lines.append("")
        lines.append("**手动打开链接：**")
        lines.append("")
        for link in item.get("links") or []:
            label = link.get("label") or "链接"
            url = link.get("url") or ""
            if url:
                lines.append(f"- [{label}]({url})")
        lines.append("")

    return "\n".join(lines)


def pending_manual_count(output_dir: Path) -> int:
    """当前输出目录中待手动下载的条目数。"""
    return len(_load_ledger(output_dir).get("failures") or [])


def refresh_manual_download_report(
    output_dir: Path,
    *,
    school_id: str | None,
) -> Path | None:
    """根据账本重新写入 Markdown；无失败条目时仍写入说明性文档。"""
    ledger = _load_ledger(output_dir)
    failures: list[dict[str, Any]] = ledger.get("failures") or []
    md = render_markdown_report(
        output_dir=output_dir,
        school_id=school_id or ledger.get("school_id"),
        failures=failures,
    )
    rp = _report_path(output_dir)
    rp.write_text(md, encoding="utf-8")
    return rp


def record_download_outcome(
    output_dir: Path,
    *,
    school_id: str,
    doi: str | None,
    cnki_article_url: str | None,
    title: str | None,
    result: dict[str, Any],
) -> dict[str, Any]:
    """
    成功则从失败账本移除；失败则写入账本并刷新 Markdown。

    Returns:
        附加字段：manual_download_report_path、manual_download_pending_count
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    key = _item_key(doi, cnki_article_url)
    ledger = _load_ledger(output_dir)
    ledger["school_id"] = school_id
    failures: list[dict[str, Any]] = [
        f for f in (ledger.get("failures") or []) if f.get("key") != key
    ]

    extra: dict[str, Any] = {}

    if result.get("success"):
        ledger["failures"] = failures
        _save_ledger(output_dir, ledger)
        rp = refresh_manual_download_report(output_dir, school_id=school_id)
        extra["manual_download_report_path"] = str(rp) if rp else None
        extra["manual_download_pending_count"] = len(failures)
        return extra

    reason_code = str(result.get("reason") or result.get("error") or "unknown")
    entry = {
        "key": key,
        "doi": doi.strip().removeprefix("https://doi.org/") if doi else None,
        "cnki_article_url": cnki_article_url,
        "title": _extract_title(result, title),
        "reason_code": reason_code,
        "reason_zh": human_failure_reason(result),
        "hint": result.get("hint") or result.get("message"),
        "links": build_access_links_from_result(
            doi=doi, result=result, cnki_article_url=cnki_article_url
        ),
        "recorded_at": _utc_now_iso(),
    }
    failures.append(entry)
    ledger["failures"] = failures
    _save_ledger(output_dir, ledger)
    rp = refresh_manual_download_report(output_dir, school_id=school_id)
    extra["manual_download_report_path"] = str(rp.resolve()) if rp else None
    extra["manual_download_pending_count"] = len(failures)
    extra["recorded_in_manual_report"] = True
    return extra
