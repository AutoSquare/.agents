"""基于 Playwright 的网页 VPN/CAS 声明式登录。"""

from __future__ import annotations

import os
import time
import asyncio
from typing import Any

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from campus_net.auth.base import AuthOutcome
from campus_net.profile.schema import CampusProfile, ProbeStep

_HTTP_PROXY = (
    os.environ.get("HTTPS_PROXY")
    or os.environ.get("https_proxy")
    or os.environ.get("HTTP_PROXY")
    or os.environ.get("http_proxy")
    or ""
).strip()


async def authenticate_cas_vpn(
    profile: CampusProfile,
    *,
    username: str | None,
    password: str | None,
    harvest_doi: str | None = None,
) -> AuthOutcome:
    """加载 login_url 后执行 YAML `auth.steps`。username/password 必须由调用方读出环境变量传入。"""

    if not username or not password:
        return AuthOutcome(success=False, message="缺少用户名或密码环境变量。", cookies=[])

    if not profile.auth.login_url or not profile.auth.login_url.startswith("https://"):
        return AuthOutcome(
            success=False,
            message="cas_vpn 需要提供 auth.login_url（HTTPS）。",
            cookies=[],
        )

    headless = True if profile.auth.headless is None else bool(profile.auth.headless)

    async with async_playwright() as pw:
        launch_kwargs: dict[str, Any] = {
            "headless": headless,
            "args": ["--disable-blink-features=AutomationControlled"],
        }
        if _HTTP_PROXY:
            launch_kwargs["proxy"] = {"server": _HTTP_PROXY}

        browser = await pw.chromium.launch(**launch_kwargs)
        ctx = await browser.new_context(locale="zh-CN", accept_downloads=True)
        page = await ctx.new_page()

        ok = False
        err_txt = ""
        try:
            await page.goto(profile.auth.login_url, timeout=90000)
            steps = [_step_from_schema(s) for s in profile.auth.steps]
            await _execute_steps(page, steps, username=username, password=password)
            await page.wait_for_timeout(500)
            final_url = page.url or ""
            if profile.auth.success_url_contains:
                ok = any(s in final_url for s in profile.auth.success_url_contains)
            else:
                ok = bool(final_url) and not _looks_like_login_placeholder(final_url, page.url)
            if not ok:
                err_txt = f"会话 URL 未达到 success_url_contains：{final_url}"
        except PlaywrightTimeoutError as e:
            err_txt = f"超时：{e}"
        except Exception as e:
            err_txt = str(e)

        cookies: list[dict[str, Any]] = []
        if ok:
            seeds = list(profile.publisher_cookie_seeds or [])
            if harvest_doi:
                d = harvest_doi.strip().removeprefix("https://doi.org/")
                seeds.append(f"https://doi.org/{d}")
            for url in seeds[:6]:
                if not url.startswith("https://"):
                    continue
                try:
                    await page.goto(url, timeout=28000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(1500)
                except Exception:
                    pass
            try:
                cookies = await ctx.cookies()
            except Exception:
                cookies = []

        await ctx.close()
        await browser.close()

    if ok:
        return AuthOutcome(success=True, message="统一身份认证 / 网页 VPN 登录成功。", cookies=cookies)

    hint = ""
    low = err_txt.lower()
    if any(x in low for x in ["captcha", "验证码"]):
        hint = "检测到疑似验证码拦截，请先浏览器登录后使用 import_browser_cookies。"
    return AuthOutcome(
        success=False,
        message=(err_txt or "登录未完成。") + (f" {hint}" if hint else ""),
        cookies=[],
    )


def _step_from_schema(s: ProbeStep) -> ProbeStep:
    return s


async def _execute_steps(page, steps: list[ProbeStep], *, username: str, password: str) -> None:
    for raw in steps:
        action = raw.action
        if action == "goto":
            if not raw.url or not raw.url.startswith("https://"):
                raise ValueError("goto 步骤需要 https url")
            await page.goto(raw.url, timeout=90000)
        elif action == "wait":
            ms = raw.milliseconds or 1000
            await page.wait_for_timeout(ms)
        elif action == "click":
            if not raw.selector:
                raise ValueError("click 缺少 selector")
            await page.click(raw.selector, timeout=45000)
        elif action == "fill":
            if not raw.selector or not raw.field:
                raise ValueError("fill 需要 selector 与 field")
            value = username if raw.field == "username" else password
            await page.fill(raw.selector, value, timeout=45000)
        elif action == "wait_for_url":
            if not raw.substring:
                raise ValueError("wait_for_url 需要 substring")
            sub = raw.substring
            deadline = time.monotonic() + 90.0
            found = False
            while time.monotonic() < deadline:
                if sub in (page.url or ""):
                    found = True
                    break
                await asyncio.sleep(0.28)
            if not found:
                raise TimeoutError(f"wait_for_url 超时：未见 {sub!r}")


def _looks_like_login_placeholder(final_url: str, current_url: str) -> bool:
    needles = ["login", "sso", "cas", "auth"]
    u = (final_url + current_url).lower()
    return any(n in u for n in needles)
