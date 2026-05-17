"""按 school_id 读写浏览器会话与安全时间戳（不含明文密码）。"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class StoredSession:
    """内存中的会话快照。"""

    school_id: str
    updated_at_unix: float
    expires_at_unix: float
    playwright_storage_path: str | None
    cookies: list[dict[str, Any]]
    meta: dict[str, Any]


def session_file(school_id: str) -> Path:
    from campus_net.profile.paths import sessions_dir

    return sessions_dir() / f"{school_id.strip().lower()}.json"


def read_session(school_id: str) -> StoredSession | None:
    """读取上次保存的会话；文件不存在返回 None。"""
    p = session_file(school_id)
    if not p.is_file():
        return None
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    cookies = raw.get("cookies") or []
    if not isinstance(cookies, list):
        cookies = []
    return StoredSession(
        school_id=raw.get("school_id") or school_id,
        updated_at_unix=float(raw.get("updated_at_unix") or 0),
        expires_at_unix=float(raw.get("expires_at_unix") or 0),
        playwright_storage_path=raw.get("playwright_storage_path"),
        cookies=cookies,
        meta=raw.get("meta") if isinstance(raw.get("meta"), dict) else {},
    )


def write_session(sess: StoredSession) -> Path:
    p = session_file(sess.school_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "school_id": sess.school_id,
        "updated_at_unix": sess.updated_at_unix,
        "expires_at_unix": sess.expires_at_unix,
        "playwright_storage_path": sess.playwright_storage_path,
        "cookies": sess.cookies,
        "meta": sess.meta,
    }
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
    return p


def is_session_valid(sess: StoredSession | None, *, grace_seconds: float = 120.0) -> bool:
    if sess is None:
        return False
    now = time.time()
    return sess.expires_at_unix > now + grace_seconds


def session_age_seconds(sess: StoredSession | None) -> float | None:
    if sess is None:
        return None
    return max(0.0, time.time() - sess.updated_at_unix)

