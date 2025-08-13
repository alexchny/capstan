from __future__ import annotations

import json
from pathlib import Path

from capstan.normalizer import (
	normalize_funding,
	normalize_indexmark,
	normalize_oi,
	normalize_orderbook,
)


def test_bybit_e2e_orderbook() -> None:
	for raw in _iter_raw(Path("tests/fixtures/bybit/books.jsonl")):
		ob = normalize_orderbook(raw)
		assert ob.symbol == "BTCUSDT"
		break


def test_bitget_e2e_orderbook() -> None:
	for raw in _iter_raw(Path("tests/fixtures/bitget/books.jsonl")):
		ob = normalize_orderbook(raw)
		assert ob.symbol == "BTCUSDT"
		break


def test_bybit_e2e_all() -> None:
	for path, fn in [
		(Path("tests/fixtures/bybit/oi.jsonl"), normalize_oi),
		(Path("tests/fixtures/bybit/funding.jsonl"), normalize_funding),
		(Path("tests/fixtures/bybit/index.jsonl"), normalize_indexmark),
	]:
		for raw in _iter_raw(path):
			obj = fn(raw)
			assert obj.symbol == "BTCUSDT"


def test_bitget_e2e_all() -> None:
	for path, fn in [
		(Path("tests/fixtures/bitget/oi.jsonl"), normalize_oi),
		(Path("tests/fixtures/bitget/funding.jsonl"), normalize_funding),
		(Path("tests/fixtures/bitget/index.jsonl"), normalize_indexmark),
	]:
		for raw in _iter_raw(path):
			obj = fn(raw)
			assert obj.symbol == "BTCUSDT"


def _iter_raw(path: Path):
	with path.open() as f:
		for line in f:
			yield json.loads(line)
