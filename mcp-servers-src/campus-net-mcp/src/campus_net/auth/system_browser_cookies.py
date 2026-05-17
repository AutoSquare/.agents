"""从本机 Edge 用户配置读取 Cookie（免手动粘贴 JSON）。"""

from __future__ import annotations

import time
from typing import Any

_PUBLISHER_DOMAIN_SUFFIXES = (
    "sciencedirect.com",
    "elsevier.com",
    "springer.com",
    "link.springer.com",
    "springerlink.com",
    "doi.org",
)


def _cookie_to_playwright(c) -> dict[str, Any]:
    domain = c.domain or ""
    if domain and not domain.startswith("."):
        domain = "." + domain.lstrip(".")
    exp = c.expires
    return {
        "name": c.name,
        "value": c.value,
        "domain": domain,
        "path": c.path or "/",
        "expires": float(exp) if exp else time.time() + 86400 * 7,
        "httpOnly": False,
        "secure": bool(c.secure),
        "sameSite": "Lax",
    }


def load_edge_publisher_cookies() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    尝试从 Edge 默认配置读取出版商相关 Cookie。

    Returns:
        (cookies, meta) — 失败时 cookies 为空列表。
    """
    meta: dict[str, Any] = {"source": "edge", "domains_tried": list(_PUBLISHER_DOMAIN_SUFFIXES)}
    try:
        import browser_cookie3  # type: ignore
    except ImportError:
        meta["error"] = "browser_cookie3 未安装"
        return [], meta

    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for suffix in _PUBLISHER_DOMAIN_SUFFIXES:
        try:
            jar_iter = browser_cookie3.edge(domain_name=suffix)
        except Exception as e:
            meta.setdefault("domain_errors", {})[suffix] = str(e)
            continue
        try:
            for c in jar_iter:
                key = (str(c.domain or "").lower(), c.name)
                if key in seen:
                    continue
                seen.add(key)
                try:
                    out.append(_cookie_to_playwright(c))
                except Exception:
                    continue
        except Exception as e:
            meta.setdefault("domain_errors", {})[suffix] = str(e)

    meta["cookie_count"] = len(out)
    return out, meta
