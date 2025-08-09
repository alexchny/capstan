from __future__ import annotations

import time


def monotonic_ts_ns() -> int:
    return time.monotonic_ns()


def utc_now_ms() -> int:
    return int(time.time() * 1000)


def is_ntp_sane(offset_ms: int, threshold_ms: int = 100) -> bool:
    return abs(offset_ms) <= threshold_ms 