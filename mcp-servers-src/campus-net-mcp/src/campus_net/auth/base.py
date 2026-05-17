"""认证适配器返回值。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AuthOutcome:
    """自动登录或非交互认证的结果摘要。"""

    success: bool
    message: str
    cookies: list[dict[str, Any]]
