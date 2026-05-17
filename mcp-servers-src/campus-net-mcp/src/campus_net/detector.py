"""按 Profile.library_probes 与 publisher_probe 执行 HTTP 探测。"""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlparse

import httpx

from campus_net.profile.schema import CampusProfile

_USER_AGENT = "campus-net-mcp/0.1"


def cookie_header_for_host(cookies: list[dict[str, Any]], host: str | None) -> str | None:
    """从 Playwright cookie 导出列表中为指定主机拼接 Cookie 头。"""

    if not cookies or not host:
        return None
    parts: list[str] = []
    host_l = host.lower().lstrip(".")
    seen: set[str] = set()
    for c in cookies:
        try:
            name = str(c.get("name"))
            value = str(c.get("value"))
            domain = str(c.get("domain", "") or "").lstrip(".").lower()
        except Exception:
            continue
        dom_ok = (not domain) or host_l == domain or host_l.endswith("." + domain)
        if not dom_ok:
            continue
        if name in seen:
            continue
        seen.add(name)
        parts.append(f"{name}={value}")
    if not parts:
        return None
    return "; ".join(parts)




async def probe_one_expect(
    client: httpx.AsyncClient,
    *,
    probe: Any,
    cookie_header: str | None,
) -> dict[str, Any]:
    headers = {"User-Agent": _USER_AGENT}
    if cookie_header:
        headers["Cookie"] = cookie_header
    meth = client.head if probe.method.upper() == "HEAD" else client.get
    try:
        r = await meth(
            probe.url,
            headers=headers,
            timeout=probe.timeout_seconds,
            follow_redirects=True,
        )
        within = r.status_code in probe.expect_status
        return {
            "name": probe.name,
            "url": probe.url,
            "status_code": r.status_code,
            "ok": True,
            "within_expect": within,
        }
    except Exception as e:
        return {
            "name": probe.name,
            "url": probe.url,
            "status_code": None,
            "ok": False,
            "within_expect": False,
            "error": str(e),
        }


async def probe_publisher_pdf_hint(
    client: httpx.AsyncClient,
    *,
    doi: str,
    timeout: float,
    cookie_header: str | None,
) -> dict[str, Any]:
    url = f"https://doi.org/{doi.strip()}"
    headers = {"User-Agent": _USER_AGENT}
    if cookie_header:
        headers["Cookie"] = cookie_header
    try:
        r = await client.get(url, headers=headers, timeout=timeout, follow_redirects=True)
        final = str(r.url)
        ctype = r.headers.get("content-type") or ""
        pdf_hint = "pdf" in ctype.lower()
        text_head = ""
        ct = ctype.lower()
        if "html" in ct or ct.startswith("text/"):
            text_head = (r.text or "")[:8000].lower()
        hay = ctype.lower() + "\n" + final.lower() + "\n" + text_head
        markers = ["application/pdf", "pdf", ".pdf?", "/pdf/", "full text", "全文", "pdfdownload"]
        if not pdf_hint:
            pdf_hint = any(m in hay for m in markers)
        return {
            "start_url": url,
            "final_url": final,
            "status_code": r.status_code,
            "pdf_hint": pdf_hint,
            "content_type": ctype.split(";")[0].strip() if ctype else "",
        }
    except Exception as e:
        return {"start_url": url, "pdf_hint": False, "error": str(e)}


async def run_detection(
    profile: CampusProfile,
    cookies: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """并行执行探针，返回结构化诊断。"""

    cookies_list = cookies or []
    tout = (
        max(p.timeout_seconds for p in profile.library_probes)
        if profile.library_probes
        else 15.0
    )
    if profile.publisher_probe:
        tout = max(tout, profile.publisher_probe.timeout_seconds)

    async with httpx.AsyncClient(verify=True, follow_redirects=True, timeout=tout) as client:
        probe_tasks = []
        for probe in profile.library_probes:
            host = urlparse(probe.url).hostname
            hdr = cookie_header_for_host(cookies_list, host)
            probe_tasks.append(probe_one_expect(client, probe=probe, cookie_header=hdr))
        probe_results = await asyncio.gather(*probe_tasks) if probe_tasks else []

        publisher_result = None
        if profile.publisher_probe:
            host = urlparse(f"https://doi.org/{profile.publisher_probe.doi}").hostname
            hdr = cookie_header_for_host(cookies_list, host)
            publisher_result = await probe_publisher_pdf_hint(
                client,
                doi=profile.publisher_probe.doi,
                timeout=profile.publisher_probe.timeout_seconds,
                cookie_header=hdr,
            )

    lib_ok_any = bool(probe_results) and any(r.get("within_expect") for r in probe_results)
    pub_ok = bool(publisher_result and publisher_result.get("pdf_hint"))

    if lib_ok_any and pub_ok:
        confidence = "high"
        recommendation = "likely_campus_or_subscribed"
        on_campus = True
    elif lib_ok_any:
        confidence = "medium"
        recommendation = "library_probe_ok_publisher_uncertain"
        on_campus = True
    elif pub_ok:
        confidence = "low"
        recommendation = "doi_chain_suggests_access"
        on_campus = None
    else:
        confidence = "low"
        recommendation = "off_campus_or_needs_auth"
        on_campus = False

    return {
        "school_id": profile.school_id,
        "confidence": confidence,
        "library_probes": probe_results,
        "publisher_probe": publisher_result,
        "on_campus": on_campus,
        "publisher_pdf_hint": bool(pub_ok),
        "recommendation": recommendation,
    }
