"""Unpaywall 开放获取候选 URL 抽取。"""

from __future__ import annotations

import os
from typing import Any


async def fetch_unpaywall_candidates(doi: str) -> tuple[list[str], dict[str, Any]]:
    """返回按优先级的 HTTPS PDF 候选列表与原始条目。"""
    import httpx

    clean = doi.strip().removeprefix("https://doi.org/")
    email = (
        os.environ.get("CAMPUS_UNPAYWALL_EMAIL")
        or os.environ.get("OPENALEX_EMAIL")
        or os.environ.get("CROSSREF_EMAIL")
        or os.environ.get("OPENALEX_mail")
        or "campus-net@jlu.edu.cn"
    )
    url = f"https://api.unpaywall.org/v2/{clean}?email={email}"
    cand: list[str] = []

    meta: dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url)
        if r.status_code != 200:
            meta["unpaywall_error"] = {"status_code": r.status_code, "text": r.text[:500]}
            return cand, meta
        data = r.json()
        meta["doi"] = clean
        meta["is_oa"] = data.get("is_oa")

        bw = data.get("best_oa_location") or {}
        for key in ("url_for_pdf", "url"):
            u = bw.get(key)
            if isinstance(u, str) and u.startswith("https://"):
                cand.append(u)

        for loc in data.get("oa_locations") or []:
            if isinstance(loc, dict):
                pu = loc.get("url_for_pdf") or loc.get("url")
                if isinstance(pu, str) and pu.startswith("https://") and pu not in cand:
                    cand.append(pu)

        return cand, meta
