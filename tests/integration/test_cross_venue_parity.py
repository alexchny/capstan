from __future__ import annotations

import json
from pathlib import Path

import pytest


def _iter_jsonl(path: Path):
	with path.open() as f:
		for line in f:
			yield json.loads(line)


@pytest.mark.parametrize("venue", ["bybit", "bitget"])
def test_best_bid_le_best_ask(venue: str) -> None:
	books = Path(f"tests/fixtures/{venue}/books.jsonl")
	for raw in _iter_jsonl(books):
		bids = raw.get("bids", [])
		asks = raw.get("asks", [])
		if not bids or not asks:
			continue
		best_bid = max(b["price"] for b in bids)
		best_ask = min(a["price"] for a in asks)
		assert best_bid <= best_ask


@pytest.mark.parametrize("venue", ["bybit", "bitget"])
def test_oi_non_negative(venue: str) -> None:
	for raw in _iter_jsonl(Path(f"tests/fixtures/{venue}/oi.jsonl")):
		assert raw["open_interest"] >= 0


@pytest.mark.parametrize("venue", ["bybit", "bitget"])
def test_funding_interval_positive(venue: str) -> None:
	for raw in _iter_jsonl(Path(f"tests/fixtures/{venue}/funding.jsonl")):
		assert raw["next_ts"] > raw["ts"]


@pytest.mark.parametrize("venue", ["bybit", "bitget"])
def test_indexmark_positive(venue: str) -> None:
	for raw in _iter_jsonl(Path(f"tests/fixtures/{venue}/index.jsonl")):
		assert raw["index"] > 0.0 and raw["mark"] > 0.0
