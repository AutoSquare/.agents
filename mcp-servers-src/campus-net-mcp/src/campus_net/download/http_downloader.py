"""PDF 二进制拉取与安全文件名。"""

from __future__ import annotations

import re
from pathlib import Path

import httpx

from campus_net.detector import cookie_header_for_host
from campus_net.download.html_pdf import extract_pdf_links_from_html

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}


def sanitize_path_component(raw: str) -> str:
    s = raw.strip().lower()
    s = re.sub(r"[^a-z0-9_.-]+", "_", s, flags=re.IGNORECASE)
    return s.strip("._") or "paper"


def _is_pdf_response(blob: bytes, ctype: str) -> bool:
    low = (ctype or "").lower()
    head = blob[:6] if len(blob) >= 6 else b""
    return "pdf" in low or head.startswith(b"%PDF")


async def fetch_binary(
    client: httpx.AsyncClient,
    url: str,
    *,
    cookies_extra: list[dict] | None = None,
    timeout: float = 120.0,
) -> tuple[bytes, str, str]:
    """返回 (bytes, content_type, resolved_url)。"""
    from urllib.parse import urlparse

    host = urlparse(url).hostname
    hdr_cookie = cookie_header_for_host(cookies_extra or [], host)
    headers = dict(DEFAULT_HEADERS)
    if hdr_cookie:
        headers["Cookie"] = hdr_cookie
    r = await client.get(url, headers=headers, timeout=timeout, follow_redirects=True)
    ctype = (r.headers.get("content-type") or "").split(";")[0].strip()
    data = r.content
    final = str(r.url)
    return data, ctype, final


async def fetch_first_pdf_url(
    client: httpx.AsyncClient,
    candidates: list[str],
    *,
    cookies_extra: list[dict] | None = None,
    max_html_follow: int = 8,
) -> tuple[bytes | None, str | None, str]:
    """依次访问候选 HTTPS URL；若返回 HTML 则解析其中 PDF 链接继续尝试。"""
    queue: list[str] = []
    seen: set[str] = set()

    def _enqueue(urls: list[str]) -> None:
        for u in urls:
            if u.startswith("https://") and u not in seen:
                seen.add(u)
                queue.append(u)

    _enqueue(candidates)
    html_followed = 0

    while queue:
        u = queue.pop(0)
        blob, ctype, final = await fetch_binary(client, u, cookies_extra=cookies_extra)
        if _is_pdf_response(blob, ctype):
            return blob, final, ctype

        low = (ctype or "").lower()
        if "html" in low and html_followed < max_html_follow:
            html_followed += 1
            discovered = extract_pdf_links_from_html(blob.decode("utf-8", errors="ignore"), final)
            _enqueue(discovered)

    return None, None, ""
