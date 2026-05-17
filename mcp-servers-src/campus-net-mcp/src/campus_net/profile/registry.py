"""当前激活 school_id 与用户/内建枚举。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from campus_net.profile.loader import builtin_index_path, builtin_profile_path, load_profile
from campus_net.profile.paths import active_record_path, user_profiles_dir
from campus_net.profile.schema import CampusProfile


def read_active_record() -> dict[str, Any]:
    p = active_record_path()
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_active_record(data: dict[str, Any]) -> None:
    p = active_record_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_active_school_id() -> str | None:
    sid = read_active_record().get("school_id")
    return sid.strip() if isinstance(sid, str) and sid.strip() else None


def set_active_school_id(school_id: str) -> CampusProfile:
    """切换激活学校（须已存在 builtin 或 user Profile）。"""

    sid = school_id.strip().lower()
    prof = load_profile(sid)
    write_active_record({"school_id": prof.school_id})
    return prof


def _profile_preview(prof: CampusProfile, *, source: str) -> dict[str, Any]:
    return {
        "school_id": prof.school_id,
        "school_name": prof.school_name,
        "aliases": prof.aliases,
        "auth_type": prof.auth.type,
        "builtin": source == "builtin",
        "source": source,
    }


def list_profiles() -> dict[str, Any]:
    """返回 builtin / user 可用的 school_id 摘要列表。"""

    builtin_entries: list[dict[str, Any]] = []
    bu_dir = builtin_profile_path("").parent
    if bu_dir.is_dir():
        from campus_net.profile.loader import load_builtin_profile

        for f in sorted(bu_dir.glob("*.yaml")):
            if f.name.startswith("_") or f.name == "index.yaml":
                continue
            sid = f.stem
            try:
                prof = load_builtin_profile(sid)
                builtin_entries.append(_profile_preview(prof, source="builtin"))
            except Exception as e:
                builtin_entries.append(
                    {
                        "school_id": sid,
                        "school_name": sid,
                        "error": str(e),
                        "builtin": True,
                        "source": "builtin",
                    }
                )

    user_entries: list[dict[str, Any]] = []
    ud = user_profiles_dir()
    for f in sorted(ud.glob("*.yaml")):
        sid = f.stem
        try:
            from campus_net.profile.loader import load_user_profile

            prof = load_user_profile(sid)
            user_entries.append(_profile_preview(prof, source="user"))
        except Exception as e:
            user_entries.append(
                {
                    "school_id": sid,
                    "school_name": sid,
                    "error": str(e),
                    "builtin": False,
                    "source": "user",
                }
            )

    return {"builtin": builtin_entries, "user": user_entries}


def builtin_alias_table() -> dict[str, Any]:
    p = builtin_index_path()
    if not p.is_file():
        return {}
    import yaml

    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}
