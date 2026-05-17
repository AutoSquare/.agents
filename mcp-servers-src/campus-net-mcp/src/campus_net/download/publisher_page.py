"""按出版商网页所见下载 PDF（ScienceDirect / Springer 等）。"""

from __future__ import annotations

import asyncio
from typing import Any

from campus_net.download.crossref_meta import fetch_crossref_work
from campus_net.download.http_downloader import DEFAULT_HEADERS, _is_pdf_response

_CONSENT_SELECTORS = (
    "#onetrust-accept-btn-handler",
    "button:has-text('Accept all cookies')",
    "button:has-text('Accept All Cookies')",
    "button:has-text('接受所有 Cookie')",
    "button:has-text('I accept')",
)


def _publisher_kind(publisher: str, doi: str) -> str:
    p = publisher.lower()
    if "elsevier" in p or doi.startswith("10.1016/"):
        return "elsevier"
    if "springer" in p or doi.startswith("10.1007/"):
        return "springer"
    return "unknown"


async def fetch_publisher_page_pdf(
    doi: str,
    *,
    cookies_extra: list[dict] | None = None,
    headless: bool = True,
    timeout_ms: int = 50_000,
) -> tuple[bytes | None, str | None, str, dict[str, Any]]:
    """
    打开出版商文章页，点击与站点一致的 PDF/下载按钮，返回浏览器拿到的 PDF 字节。

    Returns:
        (pdf_bytes, final_url, content_type, debug_meta)
    """
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    from playwright.async_api import async_playwright

    meta = await fetch_crossref_work(doi)
    kind = _publisher_kind(meta.get("publisher") or "", doi)
    meta["publisher_kind"] = kind

    if kind == "elsevier":
        pii = meta.get("pii")
        if not pii:
            meta["error"] = "missing_pii"
            return None, None, "", meta
        start_url = f"https://www.sciencedirect.com/science/article/pii/{pii}"
    elif kind == "springer":
        clean = doi.removeprefix("https://doi.org/")
        start_url = f"https://link.springer.com/article/{clean}"
    else:
        meta["error"] = "unsupported_publisher"
        return None, None, "", meta

    meta["start_url"] = start_url
    cookies_extra = cookies_extra or []
    captured: dict[str, bytes | str] = {}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=DEFAULT_HEADERS["User-Agent"],
            accept_downloads=True,
            locale="en-US",
        )
        if cookies_extra:
            try:
                await context.add_cookies(cookies_extra)
            except Exception:
                pass

        page = await context.new_page()

        async def _on_response(resp) -> None:
            try:
                url = str(resp.url)
                ctype = (resp.headers.get("content-type") or "").split(";")[0]
                if "pdf" not in ctype.lower() and "sciencedirectassets.com" not in url:
                    return
                body = await resp.body()
                if _is_pdf_response(body, ctype):
                    captured["body"] = body
                    captured["final"] = url
            except Exception:
                return

        page.on("response", _on_response)

        try:
            await page.goto(start_url, wait_until="domcontentloaded", timeout=timeout_ms)
            await page.wait_for_timeout(2500)
            for sel in _CONSENT_SELECTORS:
                try:
                    btn = page.locator(sel).first
                    if await btn.count() > 0 and await btn.is_visible():
                        await btn.click(timeout=4000)
                        await page.wait_for_timeout(800)
                        break
                except Exception:
                    continue

            if kind == "springer":
                pdf_selectors = [
                    'a[data-track-action="Download PDF"]',
                    'a[href*="/content/pdf/"]',
                    'a:has-text("Download PDF")',
                ]
            else:
                pdf_selectors = [
                    "a#pdfLink",
                    'a.link-button--primary[href*="pdfft"]',
                    'a:has-text("View PDF")',
                ]

            clicked = False
            for sel in pdf_selectors:
                try:
                    loc = page.locator(sel).first
                    if await loc.count() > 0 and await loc.is_visible():
                        async with page.expect_download(timeout=20_000) as dl_info:
                            await loc.click(timeout=8_000)
                        download = await dl_info.value
                        path = await download.path()
                        if path:
                            from pathlib import Path

                            data = Path(path).read_bytes()
                            if _is_pdf_response(data, "application/pdf"):
                                await browser.close()
                                return (
                                    data,
                                    download.url or start_url,
                                    "application/pdf",
                                    meta,
                                )
                        clicked = True
                        break
                except PlaywrightTimeoutError:
                    if captured.get("body"):
                        await browser.close()
                        return (
                            captured["body"],  # type: ignore[arg-type]
                            str(captured.get("final") or start_url),
                            "application/pdf",
                            meta,
                        )
                except Exception:
                    continue

            if not clicked and kind == "springer":
                pdf_url = f"https://link.springer.com/content/pdf/{doi.removeprefix('https://doi.org/')}.pdf"
                await page.goto(pdf_url, wait_until="commit", timeout=timeout_ms)
                await page.wait_for_timeout(2000)

            if captured.get("body"):
                await browser.close()
                return (
                    captured["body"],  # type: ignore[arg-type]
                    str(captured.get("final") or start_url),
                    "application/pdf",
                    meta,
                )

            title = await page.title()
            meta["page_title"] = title
            if "403" in title or "denied" in title.lower() or "robot" in (await page.content()).lower():
                meta["error"] = "publisher_blocked"
            else:
                meta["error"] = "pdf_button_not_found"
        except Exception as exc:
            meta["error"] = f"playwright:{type(exc).__name__}"
            if captured.get("body"):
                await browser.close()
                return (
                    captured["body"],  # type: ignore[arg-type]
                    str(captured.get("final") or start_url),
                    "application/pdf",
                    meta,
                )
        finally:
            try:
                await browser.close()
            except Exception:
                pass

    return None, None, "", meta


async def fetch_publisher_page_pdf_bounded(
    doi: str,
    *,
    cookies_extra: list[dict] | None = None,
    headless: bool = True,
    total_timeout_s: float = 55.0,
) -> tuple[bytes | None, str | None, str, dict[str, Any]]:
    """带总时长上限的出版商页下载，避免终端长时间假死。"""
    try:
        return await asyncio.wait_for(
            fetch_publisher_page_pdf(
                doi,
                cookies_extra=cookies_extra,
                headless=headless,
            ),
            timeout=total_timeout_s,
        )
    except asyncio.TimeoutError:
        return None, None, "", {"error": "publisher_page_timeout", "doi": doi}
