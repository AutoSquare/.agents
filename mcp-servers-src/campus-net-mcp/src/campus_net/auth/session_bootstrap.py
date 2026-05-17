"""httpx 引导 DOI 跳转链以刷新出版商 Cookie（下载阶段不启浏览器）。"""

from __future__ import annotations

from typing import Any
import httpx

from campus_net.auth.cookies_merge import merge_cookie_lists
from campus_net.download.http_downloader import DEFAULT_HEADERS


def _playwright_cookies_to_httpx(cookies: list[dict[str, Any]]) -> httpx.Cookies:
    jar = httpx.Cookies()
    for c in cookies:
        name = c.get("name")
        value = c.get("value")
        if not name or value is None:
            continue
        domain = str(c.get("domain") or "").lstrip(".")
        path = str(c.get("path") or "/")
        if not domain:
            continue
        try:
            jar.set(str(name), str(value), domain=domain, path=path)
        except Exception:
            continue
    return jar


def _httpx_cookies_to_playwright(jar: httpx.Cookies) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for cookie in jar.jar:
        domain = cookie.domain or ""
        if domain and not domain.startswith("."):
            domain = "." + domain.lstrip(".")
        out.append(
            {
                "name": cookie.name,
                "value": cookie.value,
                "domain": domain,
                "path": cookie.path or "/",
                "expires": cookie.expires or -1,
                "httpOnly": False,
                "secure": bool(cookie.secure),
                "sameSite": "Lax",
            }
        )
    return out


async def bootstrap_publisher_cookies_httpx(
    doi: str,
    cookies: list[dict[str, Any]],
    *,
    extra_urls: list[str] | None = None,
    timeout: float = 30.0,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """沿 DOI 与出版商入口访问，合并 Set-Cookie 到会话列表。"""
    meta: dict[str, Any] = {"doi": doi, "visited": []}
    doi_clean = doi.strip().removeprefix("https://doi.org/")
    urls = [f"https://doi.org/{doi_clean}"]
    if extra_urls:
        urls.extend([u for u in extra_urls if u.startswith("https://")])

    jar = _playwright_cookies_to_httpx(cookies)
    async with httpx.AsyncClient(
        cookies=jar,
        headers=DEFAULT_HEADERS,
        follow_redirects=True,
        timeout=timeout,
        verify=True,
    ) as client:
        for url in urls[:8]:
            try:
                r = await client.get(url, timeout=timeout)
                meta["visited"].append({"url": url, "status": r.status_code, "final": str(r.url)})
            except Exception as e:
                meta["visited"].append({"url": url, "error": str(e)})

        merged = merge_cookie_lists(cookies, _httpx_cookies_to_playwright(client.cookies))
        meta["cookie_count_after"] = len(merged)
        return merged, meta


def publisher_domains_for_doi(doi: str | None) -> list[str]:
    if not doi:
        return []
    d = doi.lower()
    if d.startswith("10.1016/") or "elsevier" in d:
        return ["sciencedirect.com", "sciencedirectassets.com"]
    if d.startswith("10.1007/") or "springer" in d:
        return ["springer.com", "link.springer.com", "springerlink.com"]
    return ["doi.org"]
