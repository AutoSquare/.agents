"""合并 Playwright / 浏览器导出的 Cookie 列表。"""

from __future__ import annotations

from typing import Any


def _cookie_key(c: dict[str, Any]) -> tuple[str, str]:
    domain = str(c.get("domain") or "").lower().lstrip(".")
    name = str(c.get("name") or "")
    return domain, name


def merge_cookie_lists(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """按 (domain, name) 去重；后出现的条目覆盖先前的。"""
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for group in groups:
        for c in group:
            if not isinstance(c, dict):
                continue
            if not c.get("name"):
                continue
            merged[_cookie_key(c)] = c
    return list(merged.values())


_BOT_COOKIE_NAMES = frozenset({"__cf_bm", "visitorId"})


def cookies_meaningful_for_domains(
    cookies: list[dict[str, Any]], domains: list[str]
) -> bool:
    """排除仅 Cloudflare/访客追踪类 Cookie 后的域名覆盖判断。"""
    filtered = [c for c in cookies if str(c.get("name") or "") not in _BOT_COOKIE_NAMES]
    return cookies_cover_domains(filtered, domains)


def cookies_cover_domains(cookies: list[dict[str, Any]], domains: list[str]) -> bool:
    """判断是否至少有一个 cookie 可作用于给定域名后缀之一。"""
    if not cookies:
        return False
    want = [d.lower().lstrip(".") for d in domains if d]
    for c in cookies:
        dom = str(c.get("domain") or "").lstrip(".").lower()
        if not dom:
            continue
        for w in want:
            if dom == w or dom.endswith("." + w) or w.endswith("." + dom):
                return True
    return False
