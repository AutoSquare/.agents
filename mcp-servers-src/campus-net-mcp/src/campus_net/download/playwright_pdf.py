"""Playwright 回退：在 httpx 被出版商拦截时尝试浏览器拉取 PDF。"""

from __future__ import annotations

from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from campus_net.download.http_downloader import DEFAULT_HEADERS, _is_pdf_response


async def fetch_pdf_via_playwright(
    candidates: list[str],
    *,
    cookies_extra: list[dict] | None = None,
    headless: bool = True,
    timeout_ms: int = 90000,
) -> tuple[bytes | None, str | None, str]:
    """用 Chromium 访问候选链接，拦截 PDF 响应或触发下载。"""
    if not candidates:
        return None, None, ""

    cookies_extra = cookies_extra or []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=DEFAULT_HEADERS["User-Agent"],
            accept_downloads=True,
        )
        if cookies_extra:
            try:
                await context.add_cookies(cookies_extra)
            except Exception:
                pass

        page = await context.new_page()
        captured: dict[str, bytes | str] = {}

        async def _on_response(resp) -> None:
            try:
                ctype = (resp.headers.get("content-type") or "").split(";")[0]
                if "pdf" not in ctype.lower():
                    return
                body = await resp.body()
                if _is_pdf_response(body, ctype):
                    captured["body"] = body
                    captured["final"] = str(resp.url)
            except Exception:
                return

        page.on("response", _on_response)

        for url in candidates:
            if not url.startswith("https://"):
                continue
            captured.clear()
            try:
                async with page.expect_download(timeout=timeout_ms) as dl_info:
                    await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                    try:
                        pdf_btn = page.get_by_role("link", name="View PDF")
                        if await pdf_btn.count() > 0:
                            await pdf_btn.first.click(timeout=15000)
                    except Exception:
                        pass
                    try:
                        pdf_btn2 = page.locator('a:has-text("PDF")').first
                        if await pdf_btn2.count() > 0:
                            await pdf_btn2.click(timeout=15000)
                    except Exception:
                        pass
                download = await dl_info.value
                path = await download.path()
                if path:
                    data = Path(path).read_bytes()
                    if _is_pdf_response(data, "application/pdf"):
                        await browser.close()
                        return data, download.url or url, "application/pdf"
            except PlaywrightTimeoutError:
                if captured.get("body"):
                    await browser.close()
                    final = str(captured.get("final") or url)
                    return captured["body"], final, "application/pdf"  # type: ignore[return-value]
            except Exception:
                if captured.get("body"):
                    await browser.close()
                    final = str(captured.get("final") or url)
                    return captured["body"], final, "application/pdf"  # type: ignore[return-value]
                continue

        await browser.close()
    return None, None, ""
