"""
campus-net-mcp — 通用校园网馆藏 MCP。

运行前：`pip install -r requirements.txt` 且执行 `playwright install chromium`。
可将环境变量 `CAMPUS_OUTPUT_DIR` 设为项目下的 `papers` 目录以固定输出路径。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import yaml  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402

from campus_net.auth.local_secrets import apply_local_secrets  # noqa: E402
from campus_net.auth.cookies_import import import_cookies_from_json  # noqa: E402

apply_local_secrets()  # noqa: E402
from campus_net.auth.ensure import attempt_authentication  # noqa: E402
from campus_net.detector import run_detection  # noqa: E402
from campus_net.download.cnki import download_cnki_paper  # noqa: E402
from campus_net.download import papers as papers_svc  # noqa: E402
from campus_net.download.manual_download_report import (  # noqa: E402
    pending_manual_count,
    record_download_outcome,
    refresh_manual_download_report,
)
from campus_net.download.resolver import resolve_fulltext_candidates  # noqa: E402
from campus_net.profile.discover import (  # noqa: E402
    discover_public_draft,
    draft_from_user_fields,
    match_builtin_or_alias,
)
from campus_net.profile.loader import (  # noqa: E402
    load_profile,
    merge_overrides,
    save_user_profile_yaml,
    validate_profile_yaml_text,
)
from campus_net.profile.onboard import assess_profile_payload  # noqa: E402
from campus_net.profile.schema import CampusProfile  # noqa: E402
from campus_net.profile.registry import (  # noqa: E402
    builtin_alias_table,
    get_active_school_id,
    list_profiles as registry_list_profiles,
    set_active_school_id as registry_set_active,
)
from campus_net.session_store import (  # noqa: E402
    read_session,
    session_age_seconds,
    is_session_valid,
)

mcp = FastMCP("campus-net")


def _flatten_field_aliases(fields: dict[str, Any]) -> dict[str, Any]:
    """将常见扁平关键字映射进嵌套 Profile 结构。"""
    data = dict(fields)
    vul = data.pop("vpn_login_url", None)
    lib = data.pop("library_url", None)
    tpl = data.pop("doi_resolver_template", None)

    if isinstance(vul, str) and vul.strip():
        auth = dict(data.get("auth") or {})
        auth["login_url"] = vul.strip()
        data["auth"] = auth

    if isinstance(lib, str) and lib.strip():
        probes = list(data.get("library_probes") or [])
        exists = False
        for p in probes:
            if isinstance(p, dict) and p.get("name") == "library_portal_agent":
                p["url"] = lib.strip()
                exists = True
                break
        if not exists:
            probes.append(
                {
                    "name": "library_portal_agent",
                    "url": lib.strip(),
                    "method": "HEAD",
                    "expect_status": [200, 302, 301, 303, 307, 308],
                },
            )
        data["library_probes"] = probes

    if tpl is not None:
        data["doi_resolver_template"] = tpl.strip() if isinstance(tpl, str) else tpl

    return data


def _resolve_output_dir(explicit: str | None) -> Path:
    v = explicit or os.environ.get("CAMPUS_OUTPUT_DIR", "").strip()
    if not v:
        cand = Path.cwd() / "papers"
        cand.mkdir(parents=True, exist_ok=True)
        return cand
    out = Path(v).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    return out


@mcp.tool()
async def list_school_profiles() -> dict[str, Any]:
    """列出可用 school_id：builtin 与用户自定义 Profile，供 Agent / 使用者选择激活。"""
    data = registry_list_profiles()
    idx = builtin_alias_table().get("aliases") or {}
    data["builtin_index_school_ids"] = list(idx.keys())
    return data


@mcp.tool()
async def get_active_profile() -> dict[str, Any]:
    """读取当前激活学校；若未完成 onboard 给出 needs_onboarding 标志。"""
    sid = get_active_school_id()
    if not sid:
        lp = registry_list_profiles()
        builtin_rows = lp.get("builtin") or []
        return {
            "needs_onboarding": True,
            "message": (
                "尚未设置激活学校。Agent 应向用户问询学校全称，随后调用 "
                "list_school_profiles、set_active_profile 或 discover_school_profile + onboard_school。"
            ),
            "known_builtin_ids": [
                row.get("school_id")
                for row in builtin_rows
                if isinstance(row, dict) and row.get("school_id")
            ],
        }

    profile = load_profile(sid)
    sess = read_session(profile.school_id)

    auth_valid = profile.auth.type != "cas_vpn" or is_session_valid(
        sess,
        grace_seconds=60.0,
    )

    return {
        "needs_onboarding": False,
        "school_id": profile.school_id,
        "school_name": profile.school_name,
        "auth_type": profile.auth.type,
        "credential_username_env": profile.credential_env.username,
        "credential_password_env": profile.credential_env.password,
        "session_age_seconds": session_age_seconds(sess),
        "auth_session_valid_estimate": auth_valid if profile.auth.type == "cas_vpn" else True,
        "profile_summary": profile.model_dump(mode="python"),
    }


@mcp.tool()
async def set_active_profile(school_id: str) -> dict[str, Any]:
    """将 school_id（builtin 或用户目录 YAML）设为当前激活上下文。"""
    prof = registry_set_active(school_id.strip())
    return {
        "success": True,
        "school_id": prof.school_id,
        "school_name": prof.school_name,
        "auth_type": prof.auth.type,
        "credential_username_env": prof.credential_env.username,
        "credential_password_env": prof.credential_env.password,
    }


@mcp.tool()
async def discover_school_profile(school_query: str) -> dict[str, Any]:
    """按校名别名表或占位草稿匹配内置 Profile；未命中返回建议检索式（由 Agent 陪同用户在浏览器查证）。"""
    return discover_public_draft(school_query.strip())


@mcp.tool()
async def onboard_school(
    fields: dict[str, Any],
    base_profile_school_id: str | None = None,
) -> dict[str, Any]:
    """
    Agent 与用户确认结构化字段后的 Profile 预审。

    * `fields` 推荐来自 discover_school_profile 草稿并补全 HTTPS 入口；
    * 可选用 `base_profile_school_id`（如内置 jlu）再在嵌套结构上局部覆盖。
    """
    payload: dict[str, Any]

    if base_profile_school_id and base_profile_school_id.strip():
        base = load_profile(base_profile_school_id.strip().lower())
        overlay = _flatten_field_aliases(dict(fields))
        merged_prof = merge_overrides(base, overlay)
        payload = merged_prof.model_dump(mode="python")
    else:
        fsrc = dict(fields)
        if not str(fsrc.get("school_name") or fsrc.get("name") or "").strip():
            return {
                "structurally_valid": False,
                "message": "缺少 school_name；请填入学校全称或由 discover_school_profile 生成草稿后继续。",
            }
        try:
            seed_dict = draft_from_user_fields(fsrc)
        except ValueError as e:
            return {"structurally_valid": False, "message": str(e)}
        overlay = _flatten_field_aliases(dict(fsrc))
        prof_seed = CampusProfile.model_validate(seed_dict)
        merged_prof = merge_overrides(prof_seed, overlay)
        payload = merged_prof.model_dump(mode="python")

    assessment = assess_profile_payload(payload)
    assessment["preview_yaml"] = yaml.safe_dump(
        payload,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    nm = payload.get("school_name") or ""
    assessment["shortcut_match"] = (
        match_builtin_or_alias(nm) if isinstance(nm, str) else {"matched": False}
    )
    return assessment


@mcp.tool()
async def save_school_profile(
    yaml_text: str,
    set_active: bool = False,
    overwrite_existing: bool = True,
) -> dict[str, Any]:
    """将用户确认的 YAML Profile 写入当前运行时的 campus-net 用户目录。"""
    prof, err = validate_profile_yaml_text(yaml_text)
    if prof is None:
        return {"success": False, "message": err or "YAML 校验失败"}

    audit = assess_profile_payload(prof.model_dump(mode="python"))
    path = save_user_profile_yaml(prof, overwrite=overwrite_existing)
    out: dict[str, Any] = {
        "success": True,
        "path": str(path),
        "assessment": audit,
    }
    if set_active:
        registry_set_active(prof.school_id)
        out["active_school_id"] = prof.school_id
    return out


@mcp.tool()
async def detect_network() -> dict[str, Any]:
    """按激活 Profile.library_probes 运行并发 HTTP 探测，评估校内/校外与 PDF 链路。"""
    sid = get_active_school_id()
    if not sid:
        return {
            "error": "no_active_profile",
            "hint": "先 set_active_profile 或 save_school_profile(..., set_active=true)。",
        }

    profile = load_profile(sid)
    sess = read_session(profile.school_id)
    cookies = sess.cookies if sess else []

    det = await run_detection(profile, cookies=cookies)

    det["cookies_loaded"] = bool(cookies)
    det["school_id"] = profile.school_id
    det["credential_username_env_set"] = bool(
        os.environ.get(profile.credential_env.username, "").strip()
    )
    det["credential_password_env_set"] = bool(
        os.environ.get(profile.credential_env.password, "").strip()
    )
    return det


@mcp.tool()
async def ensure_auth(force_refresh: bool = False) -> dict[str, Any]:
    """按 Profile.auth.type 执行自动登录或使用现有会话缓存。"""
    sid = get_active_school_id()
    if not sid:
        return {"success": False, "message": "无激活学校。", "hint": "set_active_profile"}
    profile = load_profile(sid)

    result = await attempt_authentication(profile, force_refresh=force_refresh)
    result["credential_username_env"] = profile.credential_env.username
    result["credential_password_env"] = profile.credential_env.password
    return result


@mcp.tool()
async def get_auth_status() -> dict[str, Any]:
    """查看当前激活学校会话元数据（不落盘明文口令）。"""
    sid = get_active_school_id()
    if not sid:
        return {"active": False, "message": "未设置激活 Profile。"}

    profile = load_profile(sid)
    sess = read_session(profile.school_id)

    return {
        "active": True,
        "school_id": profile.school_id,
        "auth_type": profile.auth.type,
        "session_age_seconds": session_age_seconds(sess),
        "cookies_count": len(sess.cookies) if sess else 0,
        "session_valid": bool(
            is_session_valid(sess, grace_seconds=60.0) if sess else False
        ),
        "meta": sess.meta if sess else {},
        "credential_username_env": profile.credential_env.username,
        "credential_password_env": profile.credential_env.password,
    }


@mcp.tool()
async def resolve_fulltext_url(
    doi: str | None = None,
    cnki_article_url: str | None = None,
) -> dict[str, Any]:
    """解析英文 DOI 与 CNKI 直链组合的 HTTPS PDF 候选（不触发下载）。"""
    sid = get_active_school_id()
    if not sid:
        return {"error": "no_active_profile"}
    profile = load_profile(sid)
    doi_s = doi.strip() if doi else None
    cnki_s = cnki_article_url.strip() if cnki_article_url else None
    return await resolve_fulltext_candidates(profile, doi_s, cnki_article_url=cnki_s)


@mcp.tool()
async def download_paper(
    doi: str | None = None,
    cnki_article_url: str | None = None,
    output_dir: str | None = None,
    prefer_subscription_first: bool = False,
    skip_unpaywall: bool = False,
    prefer_publisher_page: bool = True,
    allow_browser_fallback: bool = False,
    title: str | None = None,
) -> dict[str, Any]:
    """仅用 httpx + 会话 Cookie 拉出版商 PDF 直链；不启动浏览器（避免人机验证）。"""
    sid = get_active_school_id()
    if not sid:
        return {"success": False, "reason": "no_active_profile"}

    profile = load_profile(sid)
    od = _resolve_output_dir(output_dir)

    doi_s = doi.strip() if doi else None
    cnki_s = cnki_article_url.strip() if cnki_article_url else None

    result = await papers_svc.download_paper(
        profile,
        doi=doi_s,
        cnki_article_url=cnki_s,
        output_dir=str(od),
        prefer_subscription=prefer_subscription_first,
        skip_unpaywall=skip_unpaywall,
        prefer_publisher_page=prefer_publisher_page,
        allow_browser_fallback=allow_browser_fallback,
    )
    result.update(
        record_download_outcome(
            od,
            school_id=profile.school_id,
            doi=doi_s,
            cnki_article_url=cnki_s,
            title=title.strip() if title else None,
            result=result,
        )
    )
    return result


@mcp.tool()
async def download_papers(
    dois: list[str],
    output_dir: str | None = None,
    prefer_subscription_first: bool = False,
    skip_unpaywall: bool = False,
    prefer_publisher_page: bool = True,
    titles: list[str] | None = None,
) -> dict[str, Any]:
    """批量下载 DOI 列表；成功的写入 output_dir，失败的汇总进 manual_download_required.md。"""
    sid = get_active_school_id()
    if not sid:
        return {"success": False, "reason": "no_active_profile"}

    profile = load_profile(sid)
    od = _resolve_output_dir(output_dir)
    clean_dois = [d.strip().removeprefix("https://doi.org/") for d in dois if d and d.strip()]
    if not clean_dois:
        return {"success": False, "reason": "empty_doi_list"}

    title_map: dict[str, str] = {}
    if titles:
        for i, d in enumerate(clean_dois):
            if i < len(titles) and titles[i] and str(titles[i]).strip():
                title_map[d] = str(titles[i]).strip()

    succeeded: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for d in clean_dois:
        one = await papers_svc.download_paper(
            profile,
            doi=d,
            cnki_article_url=None,
            output_dir=str(od),
            prefer_subscription=prefer_subscription_first,
            skip_unpaywall=skip_unpaywall,
            prefer_publisher_page=prefer_publisher_page,
            allow_browser_fallback=False,
        )
        one.update(
            record_download_outcome(
                od,
                school_id=profile.school_id,
                doi=d,
                cnki_article_url=None,
                title=title_map.get(d),
                result=one,
            )
        )
        row = {"doi": d, **one}
        if one.get("success"):
            succeeded.append(row)
        else:
            failed.append(row)

    report_path = refresh_manual_download_report(od, school_id=profile.school_id)

    return {
        "success": len(failed) == 0,
        "school_id": profile.school_id,
        "output_dir": str(od.resolve()),
        "total": len(clean_dois),
        "succeeded_count": len(succeeded),
        "failed_count": len(failed),
        "succeeded": succeeded,
        "failed": failed,
        "manual_download_report_path": str(report_path.resolve()) if report_path else None,
        "manual_download_pending_count": pending_manual_count(od),
    }


@mcp.tool()
async def download_cnki(
    doi: str | None = None,
    title: str | None = None,
    cnki_article_url: str | None = None,
    output_dir: str | None = None,
    headed_browser: bool = False,
) -> dict[str, Any]:
    """经由图书馆 CNKI 机构入口或其详情页抓取 PDF。"""
    sid = get_active_school_id()
    if not sid:
        return {"success": False, "reason": "no_active_profile"}

    profile = load_profile(sid)
    od = _resolve_output_dir(output_dir)

    doi_s = doi.strip() if doi else None
    cnki_s = cnki_article_url.strip() if cnki_article_url else None
    title_s = title.strip() if title else None

    result = await download_cnki_paper(
        profile,
        doi=doi_s,
        title=title_s,
        cnki_article_url=cnki_s,
        output_dir=str(od),
        headless=not headed_browser,
    )
    result.update(
        record_download_outcome(
            od,
            school_id=profile.school_id,
            doi=doi_s,
            cnki_article_url=cnki_s,
            title=title_s,
            result=result,
        )
    )
    return result


@mcp.tool()
async def import_browser_cookies(
    cookie_json_text: str,
    extend_ttl_hours: float = 12.0,
    school_id: str | None = None,
) -> dict[str, Any]:
    """写入 Cookie JSON（列表或 {\"cookies\":[...]} 结构）；domain/path 须与各校门户一致。"""
    sid = (
        school_id.strip().lower()
        if isinstance(school_id, str) and school_id.strip()
        else get_active_school_id()
    )
    if not sid:
        return {"success": False, "message": "请在参数中传入 school_id 或先 set_active_profile。"}

    return import_cookies_from_json(
        sid,
        cookie_json_text=cookie_json_text,
        extend_ttl_hours=extend_ttl_hours,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
