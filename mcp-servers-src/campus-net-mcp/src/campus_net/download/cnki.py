"""知网机构入口下载（启发式检索，版面差异需用户更新 Profile）。"""

from __future__ import annotations

import os
import time
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from campus_net.download.http_downloader import sanitize_path_component
from campus_net.download.rate_limit import await_rate_limit
from campus_net.profile.schema import CampusProfile
from campus_net.session_store import read_session

_HTTP_PROXY = (
    os.environ.get("HTTPS_PROXY")
    or os.environ.get("https_proxy")
    or os.environ.get("HTTP_PROXY")
    or os.environ.get("http_proxy")
    or ""
).strip()


async def _click_first_pdf(page) -> None:
    locator = page.get_by_role("link", name="PDF")
    try:
        if await locator.count() > 0:
            await locator.first.click(timeout=60000)
            return
    except Exception:
        pass
    loc2 = page.locator('a:text-matches("(PDF)|(下载全文)")').first
    await loc2.click(timeout=90000)


async def download_cnki_paper(
    profile: CampusProfile,
    *,
    doi: str | None,
    title: str | None,
    cnki_article_url: str | None,
    output_dir: str,
    headless: bool | None = None,
) -> dict:
    """在会话 Cookie 加持下检索或直接打开 CNKI，首次下载对话框保存 PDF。"""
    if not profile.cnki.enabled or not profile.cnki.entry_url:
        if not (cnki_article_url and cnki_article_url.startswith("https://")):
            return {
                "success": False,
                "reason": "cnki_not_configured",
                "hint": "配置 Profile.cnki.enabled 与 cnki.entry_url，或改用 cnki_article_url 传入详情页 HTTPS。",
            }

    await await_rate_limit(
        profile.school_id + ":cnki",
        profile.download_rate_limit_seconds,
    )

    sess = read_session(profile.school_id)
    hq = True if headless is None else bool(headless)
    stem = sanitize_path_component(doi or title or "cnki")
    pdf_path = Path(output_dir).expanduser() / f"{stem}_{int(time.time())}.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        launch_kw: dict = {"headless": hq}
        if _HTTP_PROXY:
            launch_kw["proxy"] = {"server": _HTTP_PROXY}
        browser = await pw.chromium.launch(**launch_kw)
        ctx = await browser.new_context(locale="zh-CN", accept_downloads=True)
        if sess and sess.cookies:
            try:
                await ctx.add_cookies(sess.cookies)
            except Exception:
                pass
        page = await ctx.new_page()

        ok = False
        err_msg = ""

        try:
            async with page.expect_download(timeout=240000) as dl_info:
                if cnki_article_url and cnki_article_url.startswith("https://"):
                    await page.goto(cnki_article_url, timeout=90000)
                    await page.wait_for_timeout(800)
                    await _click_first_pdf(page)
                else:
                    if not profile.cnki.entry_url:
                        raise RuntimeError("缺少 cnki.entry_url")

                    await page.goto(profile.cnki.entry_url, timeout=90000)
                    qtxt = (doi or title or "").strip()
                    if not qtxt:
                        raise ValueError("doi、title、cnki_article_url 至少需要其一")

                    search_box = page.locator("input[type=search]").first
                    if await page.locator("input[type=search]").count() == 0:
                        search_box = page.locator("input[type=text]").first

                    await search_box.fill(qtxt, timeout=45000)

                    btns = page.get_by_role("button", name="检索")
                    if await btns.count() == 0:
                        btns = page.get_by_role("button", name="搜索")
                    if await btns.count() > 0:
                        await btns.first.click(timeout=45000)
                    else:
                        await search_box.press("Enter")

                    await page.wait_for_timeout(2000)

                    titles = page.get_by_role("link")
                    clicked = False
                    for i in range(min(await titles.count(), 25)):
                        t = titles.nth(i)
                        nm = await t.inner_text()
                        if title and title.strip() in nm:
                            await t.click()
                            clicked = True
                            break

                    if not clicked:
                        first_res = page.locator('[class*="result"] a').first
                        await first_res.click(timeout=60000)

                    await page.wait_for_timeout(1000)

                    await _click_first_pdf(page)

            download = await dl_info.value
            await download.save_as(str(pdf_path))
            ok = pdf_path.exists() and pdf_path.stat().st_size > 2048

        except PlaywrightTimeoutError as e:
            err_msg = str(e)
        except Exception as e:
            err_msg = str(e)
        finally:
            await ctx.close()
            await browser.close()

        if not ok and pdf_path.exists():
            try:
                pdf_path.unlink(missing_ok=True)
            except OSError:
                pass

    if ok:
        return {
            "success": True,
            "path": str(pdf_path.resolve()),
            "doi": doi,
            "title": title,
            "hint": "各校 CNKI 皮肤不同；失败时在 Profile.cnki.entry_url 中改为本校最新机构检索入口并重试 onboard。",
        }

    hint = ""
    low = err_msg.lower()
    if any(x in low for x in ("login", "sso", "auth", "验证码")):
        hint = "可能会话失效或未通过机构网关：请先 ensure_auth 或 import_browser_cookies。"
    return {
        "success": False,
        "reason": "cnki_playwright_failed",
        "message": err_msg or "未触发浏览器下载对话框。",
        "hint": hint or "可改用 cnki_article_url 直指论文详情页以降低检索歧义。",
    }
