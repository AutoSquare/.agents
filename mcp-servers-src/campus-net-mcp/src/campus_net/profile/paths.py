"""用户级 campus-net 数据目录路径。"""

from __future__ import annotations

import os
from pathlib import Path


def campus_net_root() -> Path:
    """返回 ~/.codex/campus-net（可由 CAMPNET_USER_ROOT 覆盖，用于测试）。"""

    override = os.environ.get("CAMPNET_USER_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".codex" / "campus-net"


def user_profiles_dir() -> Path:
    p = campus_net_root() / "profiles"
    p.mkdir(parents=True, exist_ok=True)
    return p


def sessions_dir() -> Path:
    p = campus_net_root() / "sessions"
    p.mkdir(parents=True, exist_ok=True)
    return p


def active_record_path() -> Path:
    return campus_net_root() / "active.json"


def bundled_profiles_dir() -> Path:
    """campus-net-mcp 仓库根目录下的 profiles/。"""

    # .../campus-net-mcp/src/campus_net/profile/paths.py -> repo root parents[3]
    return Path(__file__).resolve().parents[3] / "profiles"
