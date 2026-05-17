"""Crossref 元数据：解析 DOI 对应的出版商与 PII。"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


async def fetch_crossref_work(doi: str) -> dict[str, Any]:
    """查询 Crossref，返回 publisher、PII、落地页等。"""
    import httpx

    clean = doi.strip().removeprefix("https://doi.org/")
    meta: dict[str, Any] = {"doi": clean}
    url = f"https://api.crossref.org/works/{clean}"

    async with httpx.AsyncClient(timeout=25.0) as client:
        r = await client.get(url, headers={"Accept": "application/json"})
        if r.status_code != 200:
            meta["crossref_error"] = {"status_code": r.status_code}
            return meta
        data = r.json().get("message") or {}

    meta["publisher"] = (data.get("publisher") or "").strip()
    meta["title"] = (data.get("title") or [""])[0] if isinstance(data.get("title"), list) else data.get("title")

    pii = ""
    article_url = ""
    for link in data.get("link") or []:
        if not isinstance(link, dict):
            continue
        href = link.get("URL") or ""
        if "elsevier.com/content/article/PII:" in href:
            pii = href.split("PII:")[-1].split("?")[0].strip()
        if "sciencedirect.com" in href and not article_url:
            article_url = href

    if not pii:
        for link in data.get("link") or []:
            href = (link or {}).get("URL") or ""
            if "/pii/" in href.lower():
                pii = href.rsplit("/pii/", 1)[-1].split("?")[0].split("/")[0]

    meta["pii"] = pii or None
    meta["article_url"] = article_url or None
    host = ""
    for item in data.get("license") or []:
        u = (item or {}).get("URL") or ""
        if u.startswith("https://"):
            host = urlparse(u).netloc
            break
    meta["license_host"] = host
    return meta
