"""从 OpenAlex 抽取开放获取 PDF 候选链接。"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from campus_net.download.figshare import extract_figshare_article_id, fetch_figshare_pdf_candidates


async def fetch_openalex_pdf_candidates(doi: str) -> tuple[list[str], dict[str, Any]]:
    """返回 OpenAlex 记录中的 pdf_url 与 locations 候选。"""
    import httpx

    clean = doi.strip().removeprefix("https://doi.org/")
    meta: dict[str, Any] = {"doi": clean}
    cand: list[str] = []

    url = f"https://api.openalex.org/works/https://doi.org/{quote(clean, safe='')}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url)
        if r.status_code != 200:
            meta["openalex_error"] = {"status_code": r.status_code, "text": r.text[:500]}
            return cand, meta

        data = r.json()
        oa_block = data.get("open_access") or {}
        meta["is_oa"] = oa_block.get("is_oa")
        meta["title"] = data.get("title")
        oa_url = oa_block.get("oa_url")
        if isinstance(oa_url, str) and oa_url.startswith("https://"):
            if oa_url.lower().endswith(".pdf") and oa_url not in cand:
                cand.append(oa_url)

        figshare_ids: set[str] = set()
        for loc in data.get("locations") or []:
            if not isinstance(loc, dict):
                continue
            fid = extract_figshare_article_id(loc.get("id"))
            if fid:
                version = (loc.get("version") or "").lower()
                if version in ("submittedversion", "acceptedversion") and not loc.get("is_published"):
                    meta.setdefault("figshare_skipped", []).append(
                        {"article_id": fid, "version": loc.get("version"), "reason": "not_published_version"}
                    )
                    continue
                figshare_ids.add(fid)
            for key in ("pdf_url", "landing_page_url"):
                u = loc.get(key)
                if isinstance(u, str) and u.startswith("https://") and u not in cand:
                    cand.append(u)

        primary = data.get("primary_location") or {}
        if isinstance(primary, dict):
            for key in ("pdf_url", "landing_page_url"):
                u = primary.get(key)
                if isinstance(u, str) and u.startswith("https://") and u not in cand:
                    cand.append(u)

        best = data.get("best_oa_location") or {}
        if isinstance(best, dict):
            for key in ("pdf_url", "landing_page_url"):
                u = best.get(key)
                if isinstance(u, str) and u.startswith("https://") and u not in cand:
                    cand.append(u)

        figshare_meta: dict[str, Any] = {}
        for fid in sorted(figshare_ids):
            fs_cands, fs_meta = await fetch_figshare_pdf_candidates(fid)
            figshare_meta[fid] = fs_meta
            for u in fs_cands:
                if u not in cand:
                    cand.insert(0, u)
        if figshare_meta:
            meta["figshare"] = figshare_meta

        return cand, meta
