"""登录后短时打开出版商页以采集 Cookie（仅会话准备，不用于 PDF 二进制下载）。"""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright

from campus_net.auth.cookies_merge import merge_cookie_lists
from campus_net.profile.schema import CampusProfile


def _normalize_for_playwright(cookies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    now = time.time()
    for c in cookies:
        if not c.get("name"):
            continue
        domain = str(c.get("domain") or "")
        if domain and not domain.startswith("."):
            domain = "." + domain.lstrip(".")
        exp = c.get("expires")
        if exp is None or exp == -1:
            exp = now + 86400 * 7
        out.append(
            {
                "name": str(c["name"]),
                "value": str(c.get("value", "")),
                "domain": domain,
                "path": str(c.get("path") or "/"),
                "expires": float(exp),
                "httpOnly": bool(c.get("httpOnly", False)),
                "secure": bool(c.get("secure", False)),
                "sameSite": c.get("sameSite") or "Lax",
            }
        )
    return out


async def harvest_from_edge_user_profile(
    doi: str | None,
    *,
    total_timeout_s: float = 55.0,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """复用本机 Edge 用户配置访问 DOI（免管理员读 Cookie 库）。"""
    meta: dict[str, Any] = {"source": "edge_persistent"}
    edge_root = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Edge/User Data"
    if not edge_root.is_dir():
        meta["error"] = "未找到 Edge User Data"
        return [], meta

    async def _run() -> list[dict[str, Any]]:
        async with async_playwright() as pw:
            ctx = await pw.chromium.launch_persistent_context(
                user_data_dir=str(edge_root),
                channel="msedge",
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            if doi:
                d = doi.strip().removeprefix("https://doi.org/")
                await page.goto(f"https://doi.org/{d}", timeout=40000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2500)
            cookies = await ctx.cookies()
            await ctx.close()
            return cookies

    try:
        cookies = await asyncio.wait_for(_run(), timeout=total_timeout_s)
        meta["cookie_count"] = len(cookies)
        return cookies, meta
    except Exception as e:
        meta["error"] = str(e)
        return [], meta


async def harvest_publisher_cookies_playwright(
    profile: CampusProfile,
    *,
    doi: str | None,
    seed_cookies: list[dict[str, Any]],
    total_timeout_s: float = 75.0,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """在独立 Chromium 上下文中注入已有 Cookie 并访问 DOI / 种子 URL。"""
    meta: dict[str, Any] = {"visited": [], "doi": doi}

    async def _run() -> list[dict[str, Any]]:
        seeds = list(profile.publisher_cookie_seeds or [])
        if doi:
            d = doi.strip().removeprefix("https://doi.org/")
            seeds.append(f"https://doi.org/{d}")

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True if profile.auth.headless is not False else False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            ctx = await browser.new_context(locale="zh-CN", accept_downloads=False)
            norm = _normalize_for_playwright(seed_cookies)
            if norm:
                try:
                    await ctx.add_cookies(norm)
                except Exception as e:
                    meta["add_cookies_error"] = str(e)

            page = await ctx.new_page()
            for url in seeds[:6]:
                if not url.startswith("https://"):
                    continue
                try:
                    await page.goto(url, timeout=28000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(1800)
                    meta["visited"].append({"url": url, "final": page.url})
                except Exception as e:
                    meta["visited"].append({"url": url, "error": str(e)})

            collected = await ctx.cookies()
            await ctx.close()
            await browser.close()
            return merge_cookie_lists(seed_cookies, collected)

    try:
        merged = await asyncio.wait_for(_run(), timeout=total_timeout_s)
        meta["cookie_count"] = len(merged)
        return merged, meta
    except asyncio.TimeoutError:
        meta["error"] = f"harvest 超时（>{total_timeout_s}s）"
        return seed_cookies, meta
