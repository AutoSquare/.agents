"""主下载管线：OA 优先 → 馆藏 DOI 模板。"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import httpx

from campus_net.download.html_pdf import merge_unique_candidates
from campus_net.download.http_downloader import fetch_first_pdf_url, sanitize_path_component
from campus_net.download.crossref_meta import fetch_crossref_work
from campus_net.download.openalex import fetch_openalex_pdf_candidates
from campus_net.download.pdf_quality import inspect_pdf_bytes
from campus_net.auth.download_session import prepare_download_session
from campus_net.download.rate_limit import await_rate_limit
from campus_net.download.unpaywall import fetch_unpaywall_candidates
from campus_net.profile.schema import CampusProfile


async def resolve_fulltext_candidates(
    profile: CampusProfile,
    doi: str | None,
    *,
    cnki_article_url: str | None,
) -> dict:
    blocks: dict = {}
    cand: list[str] = []

    if doi:
        uw_cand, uw_meta = await fetch_unpaywall_candidates(doi)
        blocks["unpaywall"] = uw_meta
        cand.extend(uw_cand)
        oa_cand, oa_meta = await fetch_openalex_pdf_candidates(doi)
        blocks["openalex"] = oa_meta
        cand.extend(oa_cand)

    if profile.doi_resolver_template and doi:
        tpl = profile.doi_resolver_template
        doi_clean = doi.strip().removeprefix("https://doi.org/")
        if "{doi_encoded}" in tpl:
            inst = tpl.replace("{doi_encoded}", quote(doi_clean, safe=""))
        else:
            inst = tpl.replace("{doi}", doi_clean)
        if inst.startswith("https://") and inst not in cand:
            cand.append(inst)

    institutional: list[str] = []
    if profile.doi_resolver_template and doi:
        institutional.append(
            profile.doi_resolver_template.replace("{doi}", doi.strip().removeprefix("https://doi.org/"))
        )

    cnki_hints: dict = {}
    if cnki_article_url and cnki_article_url.startswith("https://"):
        cand.insert(0, cnki_article_url)
        cnki_hints["artifact"] = cnki_article_url

    return {
        "candidates_https": cand,
        "chunks": blocks,
        "doi_resolver_hint": institutional,
        "cnki": cnki_hints,
    }


async def save_pdf_bytes(
    data: bytes,
    *,
    output_dir: Path,
    stem: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = sanitize_path_component(stem)
    fn = output_dir / f"{safe_stem}.pdf"
    fn.write_bytes(data)
    return fn


def _publisher_https_urls(doi_clean: str, crossref: dict) -> list[str]:
    """出版商站点直链（与网页 PDF 按钮一致）。"""
    out: list[str] = []
    pii = crossref.get("pii")
    if pii:
        out.append(f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft")
        out.append(f"https://www.sciencedirect.com/science/article/pii/{pii}")
    if doi_clean.startswith("10.1007/"):
        out.append(f"https://link.springer.com/content/pdf/{doi_clean}.pdf")
        out.append(f"https://link.springer.com/article/{doi_clean}")
    return out


async def download_paper(
    profile: CampusProfile,
    *,
    doi: str | None,
    cnki_article_url: str | None,
    output_dir: str | None,
    prefer_subscription: bool = False,
    skip_unpaywall: bool = False,
    prefer_publisher_page: bool = True,
    allow_browser_fallback: bool = False,
) -> dict:
    """默认仅用 httpx + 会话 Cookie 拉取出版商 PDF 直链；不启动浏览器（避免人机验证）。"""

    await await_rate_limit(
        profile.school_id,
        profile.download_rate_limit_seconds,
    )

    doi_clean = doi.strip().removeprefix("https://doi.org/") if doi else None

    session_prep = await prepare_download_session(profile, doi_clean)
    cookies_list = session_prep.get("cookies") or []

    out = Path(output_dir or "").expanduser() if output_dir else None
    if out is None or str(out).strip() == "":
        return {"success": False, "reason": "output_dir_missing"}

    stem = doi_clean.replace("/", "_") if doi_clean else "download"

    uw_meta: dict = {}
    oa_meta: dict = {}
    crossref_meta: dict = {}
    cand: list[str] = []
    http_timeout = 45.0

    if doi_clean:
        crossref_meta = await fetch_crossref_work(doi_clean)
        if prefer_publisher_page:
            cand = merge_unique_candidates(_publisher_https_urls(doi_clean, crossref_meta), cand)

    blob: bytes | None = None
    final_u: str | None = None
    ctype = ""

    if prefer_publisher_page and cand:
        async with httpx.AsyncClient(
            verify=True, follow_redirects=True, timeout=http_timeout
        ) as client:
            blob, final_u, ctype = await fetch_first_pdf_url(
                client, cand, cookies_extra=cookies_list
            )

    if doi_clean and not skip_unpaywall and not prefer_subscription:
        uw_cands, uw_meta = await fetch_unpaywall_candidates(doi_clean)
        if prefer_publisher_page:
            uw_cands = [
                u
                for u in uw_cands
                if any(
                    h in u.lower()
                    for h in (
                        "sciencedirect",
                        "springer",
                        "elsevier",
                        "nature.com",
                        "wiley",
                    )
                )
            ]
        cand = merge_unique_candidates(uw_cands, cand)
        if not prefer_publisher_page:
            oa_cands, oa_meta = await fetch_openalex_pdf_candidates(doi_clean)
            cand = merge_unique_candidates(oa_cands, cand)

    tpl_cands = []
    if profile.doi_resolver_template and doi_clean:
        tpl = profile.doi_resolver_template
        d = doi_clean
        tpl_url = tpl.replace("{doi_encoded}", quote(d, safe="")).replace("{doi}", d)
        if tpl_url.startswith("https://"):
            tpl_cands.append(tpl_url)

    if prefer_subscription and tpl_cands:
        cand = tpl_cands + cand
    else:
        cand = cand + tpl_cands

    if cnki_article_url and cnki_article_url.startswith("https://"):
        cand.insert(0, cnki_article_url)

    if doi_clean:
        cand = merge_unique_candidates(cand, [f"https://doi.org/{doi_clean}"])

    if not cand:
        return {
            "success": False,
            "reason": "no_candidates",
            "doi": doi_clean,
            "crossref": crossref_meta,
            "unpaywall": uw_meta,
            "openalex": oa_meta,
        }

    if blob is None and cand:
        async with httpx.AsyncClient(
            verify=True, follow_redirects=True, timeout=http_timeout
        ) as client:
            blob, final_u, ctype = await fetch_first_pdf_url(
                client, cand, cookies_extra=cookies_list
            )

    if blob is None:
        from campus_net.profile.paths import campus_net_root

        local_env = str(campus_net_root() / "local.env")
        hint = (
            "未使用浏览器下载 PDF。已自动尝试 Edge 系统 Cookie 与 CAS 会话引导。"
            f"若仍失败：在 {local_env} 配置 CAMPUS_USERNAME 与 CAMPUS_PASSWORD（吉大统一身份），"
            "或在 Edge 登录 ScienceDirect 后重试 download_paper；无需向对话粘贴 Cookie。"
        )
        if allow_browser_fallback:
            hint += " allow_browser_fallback 已弃用。"
        return {
            "success": False,
            "reason": "pdf_not_detected_in_chain",
            "tried": cand[:20],
            "crossref": crossref_meta,
            "unpaywall": uw_meta,
            "openalex": oa_meta,
            "cookies_loaded": bool(cookies_list),
            "session_prep": session_prep,
            "hint": hint,
        }

    is_ms, ms_reason = inspect_pdf_bytes(blob)
    if is_ms:
        return {
            "success": False,
            "reason": "manuscript_pdf_rejected",
            "manuscript_hint": ms_reason,
            "final_url": final_u,
            "hint": "已拒绝仓储投稿稿；请确保 VoR 来自出版商站点（自动会话准备后重试 download_paper）",
            "session_prep": session_prep,
            "tried": cand[:20],
            "crossref": crossref_meta,
            "unpaywall": uw_meta,
            "openalex": oa_meta,
        }

    saved = await save_pdf_bytes(blob, output_dir=out, stem=stem)
    return {
        "success": True,
        "path": str(saved.resolve()),
        "final_url": final_u,
        "content_type": ctype,
        "source": "http_chain",
        "used_doi_resolver": bool(profile.doi_resolver_template and doi_clean),
        "crossref": crossref_meta,
        "unpaywall": uw_meta,
        "openalex": oa_meta,
        "session_prep": session_prep,
    }
