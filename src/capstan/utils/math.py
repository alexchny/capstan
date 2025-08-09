from __future__ import annotations

from collections.abc import Iterable


def zscore(delta: float, sigma: float) -> float:
    if sigma <= 0.0:
        return 0.0
    return delta / sigma


def ewma(values: Iterable[float], alpha: float) -> float:
    iterator = iter(values)
    try:
        s = float(next(iterator))
    except StopIteration:
        return 0.0
    for v in iterator:
        s = alpha * float(v) + (1.0 - alpha) * s
    return s 