from __future__ import annotations

_counters: dict[tuple[str, str, str], int] = {}


def inc(name: str, venue: str, stream: str, value: int = 1) -> None:
	key = (name, venue, stream)
	_counters[key] = _counters.get(key, 0) + value


def get(name: str, venue: str, stream: str) -> int:
	return _counters.get((name, venue, stream), 0)


def reset() -> None:
	_counters.clear()
