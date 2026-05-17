"""download_paper 前自动准备会话：local.env、Edge Cookie、CAS、httpx 引导。"""

from __future__ import annotations

import time
from typing import Any

from campus_net.auth.cookies_merge import cookies_meaningful_for_domains, merge_cookie_lists
from campus_net.auth.ensure import attempt_authentication
from campus_net.auth.local_secrets import apply_local_secrets, credentials_configured
from campus_net.auth.publisher_harvest import (
    harvest_from_edge_user_profile,
    harvest_publisher_cookies_playwright,
)
from campus_net.auth.session_bootstrap import (
    bootstrap_publisher_cookies_httpx,
    publisher_domains_for_doi,
)
from campus_net.auth.system_browser_cookies import load_edge_publisher_cookies
from campus_net.profile.schema import CampusProfile
from campus_net.session_store import StoredSession, read_session, write_session


def _persist_cookies(profile: CampusProfile, cookies: list[dict], *, meta_patch: dict) -> None:
    now = time.time()
    ttl = profile.session_ttl_hours * 3600.0
    prior = read_session(profile.school_id)
    sess = StoredSession(
        school_id=profile.school_id,
        updated_at_unix=now,
        expires_at_unix=now + ttl,
        playwright_storage_path=prior.playwright_storage_path if prior else None,
        cookies=cookies,
        meta={**(prior.meta if prior else {}), **meta_patch},
    )
    write_session(sess)


async def prepare_download_session(
    profile: CampusProfile,
    doi: str | None,
) -> dict[str, Any]:
    """
    在 httpx 下载前自动补齐出版商会话；全程不向用户索要粘贴 Cookie。

    顺序：local.env → 磁盘会话 → Edge 系统 Cookie → CAS/VPN 登录 → Playwright 采集 → httpx DOI 链。
    """
    apply_local_secrets()
    steps: list[str] = []
    domains = publisher_domains_for_doi(doi)

    sess = read_session(profile.school_id)
    cookies = list(sess.cookies) if sess else []

    if not cookies and doi:
        steps.append("httpx_bootstrap_cold")
        cookies, _ = await bootstrap_publisher_cookies_httpx(doi, [])

    need_pub = bool(domains) and not cookies_meaningful_for_domains(cookies, domains)

    if need_pub:
        edge_c, edge_meta = load_edge_publisher_cookies()
        steps.append("edge_scan")
        if edge_c:
            cookies = merge_cookie_lists(cookies, edge_c)
            _persist_cookies(
                profile,
                cookies,
                meta_patch={"edge_import": edge_meta, "source": "auto_edge"},
            )
            need_pub = not cookies_meaningful_for_domains(cookies, domains)

    if need_pub and doi:
        steps.append("edge_profile_harvest")
        edge_prof, edge_prof_meta = await harvest_from_edge_user_profile(doi)
        if edge_prof:
            cookies = merge_cookie_lists(cookies, edge_prof)
            _persist_cookies(
                profile,
                cookies,
                meta_patch={"edge_profile": edge_prof_meta},
            )
            need_pub = not cookies_meaningful_for_domains(cookies, domains)

    if need_pub and credentials_configured(profile):
        steps.append("cas_auth")
        auth = await attempt_authentication(
            profile,
            force_refresh=False,
            skip_if_valid=True,
            harvest_doi=doi,
        )
        if auth.get("success"):
            sess = read_session(profile.school_id)
            cookies = list(sess.cookies) if sess else cookies
            need_pub = not cookies_meaningful_for_domains(cookies, domains)

    if need_pub and cookies:
        steps.append("playwright_harvest")
        cookies, harvest_meta = await harvest_publisher_cookies_playwright(
            profile,
            doi=doi,
            seed_cookies=cookies,
        )
        _persist_cookies(
            profile,
            cookies,
            meta_patch={"publisher_harvest": harvest_meta},
        )
        need_pub = not cookies_meaningful_for_domains(cookies, domains)

    if doi and cookies:
        steps.append("httpx_bootstrap")
        seeds = list(profile.publisher_cookie_seeds or [])
        cookies, boot_meta = await bootstrap_publisher_cookies_httpx(
            doi,
            cookies,
            extra_urls=seeds,
        )
        _persist_cookies(profile, cookies, meta_patch={"httpx_bootstrap": boot_meta})

    return {
        "cookies": cookies,
        "cookie_count": len(cookies),
        "publisher_domains": domains,
        "publisher_cookies_ready": cookies_meaningful_for_domains(cookies, domains),
        "credentials_configured": credentials_configured(profile),
        "steps": steps,
    }
