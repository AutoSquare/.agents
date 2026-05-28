"""从用户级 local.env 注入凭据环境变量（不写入日志）。"""

from __future__ import annotations

import os

from campus_net.profile.paths import campus_net_root

_APPLIED = False


def apply_local_secrets() -> dict[str, object]:
    """读取 ~/.codex/campus-net/local.env 并合并进 os.environ（不覆盖已有变量）。"""
    global _APPLIED
    path = campus_net_root() / "local.env"
    loaded: list[str] = []
    if path.is_file():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if not key:
                continue
            if key not in os.environ or not str(os.environ.get(key, "")).strip():
                os.environ[key] = val
            loaded.append(key)
    _APPLIED = True
    return {
        "path": str(path),
        "exists": path.is_file(),
        "loaded_keys": loaded,
        "already_applied": _APPLIED,
    }


def credentials_configured(profile) -> bool:
    """当前进程是否已具备 Profile 声明的凭据环境变量。"""
    apply_local_secrets()
    u = os.environ.get(profile.credential_env.username, "").strip()
    p = os.environ.get(profile.credential_env.password, "").strip()
    return bool(u and p)
