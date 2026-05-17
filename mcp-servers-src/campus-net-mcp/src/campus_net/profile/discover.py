"""校内名解析与 Profile 草稿生成（不改变磁盘）。"""

from __future__ import annotations

import re
from typing import Any

from campus_net.profile.loader import builtin_index_path, load_builtin_profile, resolve_alias
from campus_net.profile.schema import CampusProfile


def slugify_school_id(name: str) -> str:
    """将校名粗略转为可用的 school_id 建议值。"""

    s = re.sub(r"\s+", "-", name.strip().lower())
    s = re.sub(r"[^a-z0-9_-]", "", s)
    return s[:48] if s else "custom"


def match_builtin_or_alias(school_query: str) -> dict[str, Any]:
    """若命中内置别名或 school_id，返回命中信息。"""
    raw = school_query.strip()
    if not raw:
        return {"matched": False, "reason": "school_query_empty"}
    rid = resolve_alias(raw)
    if rid:
        try:
            prof = load_builtin_profile(rid)
            return {
                "matched": True,
                "school_id": prof.school_id,
                "profile": prof.model_dump(mode="python"),
                "hint": "使用 list_school_profiles 与 set_active_profile 可直接激活内置配置",
            }
        except FileNotFoundError:
            pass
    q_low = raw.lower()
    bp = builtin_index_path().parent
    if bp.is_dir():
        for p in bp.glob("*.yaml"):
            if p.stem in ("index",):
                continue
            if p.stem.lower() == q_low:
                try:
                    prof = load_builtin_profile(p.stem)
                    return {
                        "matched": True,
                        "school_id": prof.school_id,
                        "profile": prof.model_dump(mode="python"),
                        "hint": "直接 set_active_profile",
                    }
                except Exception:
                    break
    return {"matched": False}


def draft_from_user_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """由 Agent / 用户提供的最小结构化字段拼装 Profile 草稿字典。"""

    name = str(fields.get("school_name") or fields.get("name") or "").strip()
    if not name:
        raise ValueError("school_name 必填")
    sid = str(fields.get("school_id") or slugify_school_id(name)).strip().lower()

    vpn_url = str(fields.get("vpn_login_url") or fields.get("vpn_url") or "").strip()
    lib_url = str(fields.get("library_url") or fields.get("library_portal_url") or "").strip()

    auth_type = str(fields.get("auth_type") or "cas_vpn").strip()
    probes: list[dict[str, Any]] = []
    if lib_url.startswith("https://"):
        probes.append(
            {"name": "library_portal", "url": lib_url, "method": "HEAD", "expect_status": [200, 302, 301]},
        )

    doi_tpl = fields.get("doi_resolver_template") or ""
    if isinstance(doi_tpl, str) and doi_tpl.strip() == "":
        doi_tpl = None

    cnki_needed = fields.get("cnki_needed")
    cnki_entry = str(fields.get("cnki_entry_url") or "").strip()

    cnki_block: dict[str, Any] = {
        "enabled": bool(cnki_entry.startswith("https://")),
        "entry_url": cnki_entry if cnki_entry.startswith("https://") else "",
        "search_by": fields.get("cnki_search_by") or ["doi", "title", "url"],
    }
    if cnki_needed is False:
        cnki_block["enabled"] = False
        cnki_block["entry_url"] = ""

    steps = fields.get("auth_steps") or _default_cas_steps()
    publisher_doi = str(fields.get("publisher_probe_doi") or "10.1038/nature12373")

    draft = {
        "school_id": sid,
        "school_name": name,
        "aliases": fields.get("aliases") or [],
        "auth": {
            "type": auth_type if auth_type in ("ip_only", "cas_vpn", "carsi", "custom") else "cas_vpn",
            "login_url": vpn_url if vpn_url.startswith("https://") else None,
            "steps": steps,
            "success_url_contains": fields.get("success_url_contains")
            or (["vpn.", ".edu.cn"] if vpn_url else []),
            "headless": fields.get("headless", True),
        },
        "credential_env": {
            "username": str(fields.get("credential_username_env") or "CAMPUS_USERNAME"),
            "password": str(fields.get("credential_password_env") or "CAMPUS_PASSWORD"),
        },
        "library_probes": probes,
        "publisher_probe": {"doi": publisher_doi, "timeout_seconds": 24.0},
        "doi_resolver_template": doi_tpl,
        "cnki": cnki_block,
        "access_modes": fields.get("access_modes") or [],
        "session_ttl_hours": float(fields.get("session_ttl_hours") or 6),
        "download_rate_limit_seconds": float(fields.get("download_rate_limit_seconds") or 3),
    }
    return draft

def _default_cas_steps() -> list[dict[str, Any]]:
    """通用占位：多数学校表单 id 近似；各校可在 onboard 中覆盖。"""

    return [
        {"action": "wait", "milliseconds": 1500},
        {"action": "fill", "selector": "#username", "field": "username"},
        {"action": "fill", "selector": "#password", "field": "password"},
        {"action": "click", "selector": "button[type='submit']"},
        {"action": "wait", "milliseconds": 3000},
    ]


def discover_public_draft(school_query: str) -> dict[str, Any]:
    """供 MCP discover_school_profile 调用：别名命中或给出检索建议。"""

    raw = school_query.strip()
    if not raw:
        return {"error": "school_query_required"}
    hit = match_builtin_or_alias(raw)
    if hit.get("matched"):
        hit["suggested_web_search_queries"] = None
        hit["needs_user_urls"] = False
        return hit
    slug = slugify_school_id(raw)
    return {
        "matched": False,
        "hint": "请先尝试 list_school_profiles；若无内置则需用户提供图书馆与 VPN HTTPS 入口",
        "suggested_web_search_queries": [
            f"{raw} 图书馆 校外访问",
            f"{raw} 图书馆 WEB VPN",
        ],
        "draft_template": draft_from_user_fields(
            {
                "school_name": raw,
                "school_id": slug,
                "auth_type": "cas_vpn",
                "vpn_login_url": "",
                "library_url": "",
                "publisher_probe_doi": "10.1038/nature12373",
                "aliases": [],
            }
        ),
        "needs_user_urls": True,
    }

