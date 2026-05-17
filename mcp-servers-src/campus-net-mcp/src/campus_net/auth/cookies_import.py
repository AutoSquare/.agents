"""将 JSON cookie 写入当前学校会话磁盘。"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from campus_net.profile.paths import campus_net_root
from campus_net.session_store import StoredSession, read_session, write_session


def import_cookies_from_json(
    school_id: str,
    *,
    cookie_json_text: str,
    extend_ttl_hours: float = 12.0,
) -> dict[str, Any]:
    """由浏览器导出或手动粘贴的 Cookie JSON 写入会话存储。"""

    sid = school_id.strip().lower()
    try:
        parsed = json.loads(cookie_json_text)
    except json.JSONDecodeError as e:
        return {"success": False, "message": f"JSON 解析失败：{e}"}

    cookies: list[dict[str, Any]]
    if isinstance(parsed, dict) and isinstance(parsed.get("cookies"), list):
        cookies = parsed["cookies"]  # type: ignore
    elif isinstance(parsed, list):
        cookies = parsed
    else:
        return {"success": False, "message": "根节点须为 cookie 数组或 {\"cookies\":[...]}"}

    if not cookies:
        return {"success": False, "message": "cookie 列表为空"}

    now = time.time()
    ttl = extend_ttl_hours * 3600.0
    prior = read_session(sid)

    sess = StoredSession(
        school_id=sid,
        updated_at_unix=now,
        expires_at_unix=now + ttl,
        playwright_storage_path=prior.playwright_storage_path if prior else None,
        cookies=cookies,
        meta={"source": "import_browser_cookies"},
    )
    path = write_session(sess)
    return {
        "success": True,
        "school_id": sid,
        "cookie_count": len(cookies),
        "session_path": str(path),
        "expires_at_unix": sess.expires_at_unix,
        "hint": (
            "请使用浏览器导出含 name/value/domain/path 的 Cookie 列表；扩展程序导出的字段名可能不同，须先规整。"
        ),
    }


def import_cookies_from_export_file(path_str: str) -> dict[str, Any]:
    """从本地 UTF-8 文本读取 JSON cookie 导出（需要 school_id）。"""

    p = Path(path_str).expanduser()
    if not p.is_file():
        return {"success": False, "message": f"找不到文件：{p}"}

    txt = p.read_text(encoding="utf-8")

    parsed = json.loads(txt)
    school_id_val: str | None = None

    if isinstance(parsed, dict) and isinstance(parsed.get("school_id"), str):
        school_id_val = parsed["school_id"]
        blob = parsed.get("cookies")
        txt = json.dumps(blob if blob is not None else parsed)

    if not school_id_val:
        return {
            "success": False,
            "message": "文件须为 {\"school_id\":\"...\",\"cookies\":[...]} 结构，或直接使用 import_cookies_from_json 并提供 school_id 参数的工具入口。",
        }

    return import_cookies_from_json(school_id_val, cookie_json_text=txt)

