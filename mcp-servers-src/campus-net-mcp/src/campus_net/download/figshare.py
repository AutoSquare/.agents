"""从 Figshare API 解析可下载 PDF 直链。"""

from __future__ import annotations

import re
from typing import Any

_FIGSHARE_OAI = re.compile(r"figshare\.com:article[/:](\d+)", re.I)
_FIGSHARE_URL = re.compile(r"figshare(?:\.[a-z.]+)?\.[a-z]+/articles/(?:[^/]+/)?(\d+)", re.I)


def extract_figshare_article_id(location_id: str | None) -> str | None:
    """从 OpenAlex location id 或 Figshare 页面 URL 提取文章数字 ID。"""
    if not location_id:
        return None
    m = _FIGSHARE_OAI.search(location_id)
    if m:
        return m.group(1)
    m = _FIGSHARE_URL.search(location_id)
    if m:
        return m.group(1)
    return None


_NDOWNLOADER_IN_HTML = re.compile(
    r"https://ndownloader\.figshare\.com/files/\d+",
    re.I,
)


async def _scrape_ndownloader_urls(article_id: str) -> list[str]:
    """Figshare API 被 403 时，从公开页 HTML 抽取 ndownloader 直链（纯 httpx，无浏览器）。"""
    import httpx

    from campus_net.download.http_downloader import DEFAULT_HEADERS

    found: list[str] = []
    pages = (
        f"https://figshare.com/articles/{article_id}",
        f"https://figshare.com/articles/{article_id}/versions/latest",
    )
    async with httpx.AsyncClient(
        timeout=25.0,
        follow_redirects=True,
        headers=DEFAULT_HEADERS,
    ) as client:
        for page in pages:
            try:
                r = await client.get(page)
                if r.status_code != 200 or not r.text:
                    continue
                for u in _NDOWNLOADER_IN_HTML.findall(r.text):
                    if u not in found:
                        found.append(u)
            except Exception:
                continue
    return found


async def fetch_figshare_pdf_candidates(article_id: str) -> tuple[list[str], dict[str, Any]]:
    """调用 Figshare v2 API，返回 files[].download_url 列表；API 不可用时回退 HTML 解析。"""
    import httpx

    from campus_net.download.http_downloader import DEFAULT_HEADERS

    meta: dict[str, Any] = {"article_id": article_id}
    cand: list[str] = []
    url = f"https://api.figshare.com/v2/articles/{article_id}"

    async with httpx.AsyncClient(timeout=30.0, headers=DEFAULT_HEADERS) as client:
        r = await client.get(url, headers={**DEFAULT_HEADERS, "Accept": "application/json"})
        if r.status_code == 200:
            data = r.json()
            meta["title"] = data.get("title")
            meta["figshare_url"] = data.get("url_public_html") or data.get("figshare_url")
            for f in data.get("files") or []:
                if not isinstance(f, dict):
                    continue
                dl = f.get("download_url")
                mime = (f.get("mimetype") or "").lower()
                name = (f.get("name") or "").lower()
                if not isinstance(dl, str) or not dl.startswith("https://"):
                    continue
                if ("pdf" in mime or name.endswith(".pdf")) and dl not in cand:
                    cand.append(dl)
            return cand, meta

        meta["figshare_error"] = {"status_code": r.status_code, "text": r.text[:300]}
        scraped = await _scrape_ndownloader_urls(article_id)
        if scraped:
            meta["figshare_scrape"] = True
            cand.extend(scraped)
        return cand, meta
