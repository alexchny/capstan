from __future__ import annotations

import json
from pathlib import Path

from capstan.venue_adapters import BybitRO

FIX = Path("tests/fixtures/bybit")


def _count_lines(path: Path) -> int:
	with path.open() as f:
		return sum(1 for _ in f)


def test_bybit_books_monotonic_and_keys() -> None:
	adapter = BybitRO(root=FIX)
	prev = -1
	c = 0
	for ob in adapter.books("BTCUSDT"):
		assert ob.ts >= prev
		prev = ob.ts
		assert ob.symbol == "BTCUSDT"
		c += 1
	assert c == _count_lines(FIX / "books.jsonl")


def test_bybit_oi_counts() -> None:
	adapter = BybitRO(root=FIX)
	c = sum(1 for _ in adapter.oi("BTCUSDT"))
	assert c == _count_lines(FIX / "oi.jsonl")


def test_bybit_funding_counts() -> None:
	adapter = BybitRO(root=FIX)
	c = sum(1 for _ in adapter.funding("BTCUSDT"))
	assert c == _count_lines(FIX / "funding.jsonl")


def test_bybit_index_counts() -> None:
	adapter = BybitRO(root=FIX)
	c = sum(1 for _ in adapter.indexmark("BTCUSDT"))
	assert c == _count_lines(FIX / "index.jsonl")
