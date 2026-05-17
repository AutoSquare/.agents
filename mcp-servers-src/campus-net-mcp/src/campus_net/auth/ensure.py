"""按 Profile.auth.type 调度 Playwright/CAS/IP；会话 TTL 与时间戳在此处持久化。"""
from __future__ import annotations

import time
from typing import Any

from campus_net.auth.factory import authenticate_unpersisted
from campus_net.profile.schema import CampusProfile
from campus_net.session_store import (
    StoredSession,
    read_session,
    write_session,
    is_session_valid,
)


async def attempt_authentication(
    profile: CampusProfile,
    *,
    force_refresh: bool = False,
    skip_if_valid: bool = True,
    harvest_doi: str | None = None,
) -> dict[str, Any]:
    """执行自动登录并按 session_ttl_hours 写入会话磁盘。"""
    sid = profile.school_id
    existing = read_session(sid)
    if (
        skip_if_valid
        and not force_refresh
        and profile.auth.type in ("cas_vpn",)
        and existing is not None
        and len(existing.cookies) > 0
        and is_session_valid(existing, grace_seconds=30.0)
    ):
        return {
            "success": True,
            "skipped": True,
            "school_id": sid,
            "message": "已存在有效期内会话，跳过重新登录",
            "cookie_count": len(existing.cookies),
        }

    outcome = await authenticate_unpersisted(profile, harvest_doi=harvest_doi)
    if not outcome.success:
        return {
            "success": False,
            "school_id": sid,
            "message": outcome.message,
            "cookie_count": 0,
        }

    ttl = profile.session_ttl_hours * 3600.0
    now = time.time()

    if profile.auth.type in ("cas_vpn", "ip_only"):
        sess = StoredSession(
            school_id=sid,
            updated_at_unix=now,
            expires_at_unix=now + ttl,
            playwright_storage_path=None,
            cookies=outcome.cookies,
            meta={"mode": profile.auth.type},
        )
        write_session(sess)
        return {
            "success": True,
            "skipped": False,
            "school_id": sid,
            "message": outcome.message,
            "cookie_count": len(outcome.cookies),
        }

    return {
        "success": True,
        "skipped": False,
        "school_id": sid,
        "message": outcome.message,
        "cookie_count": len(outcome.cookies),
    }
