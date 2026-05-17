"""按 Profile.download_rate_limit_seconds 做简单节流。"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict

_lock = asyncio.Lock()
_last: defaultdict[str, float] = defaultdict(float)


async def await_rate_limit(key: str, seconds: float) -> None:
    if seconds <= 0:
        return
    async with _lock:
        now = time.monotonic()
        last = _last[key]
        delta = seconds - (now - last)
        wait_s = delta if delta > 0 else 0.0
        _last[key] = max(now + wait_s, now)
    if wait_s > 0:
        await asyncio.sleep(wait_s)
