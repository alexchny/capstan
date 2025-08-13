from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from capstan import metrics
from capstan.schemas import Funding, IndexMark, OpenInterest, OrderBook


class VenueAdapter:
	def books(self, symbol: str) -> Iterator[OrderBook]:
		raise NotImplementedError

	def oi(self, symbol: str) -> Iterator[OpenInterest]:
		raise NotImplementedError

	def funding(self, symbol: str) -> Iterator[Funding]:
		raise NotImplementedError

	def indexmark(self, symbol: str) -> Iterator[IndexMark]:
		raise NotImplementedError


class FixtureRO(VenueAdapter):
	def __init__(self, root: Path | str, logger_name: str) -> None:
		self.root = Path(root)
		self.logger = logging.getLogger(logger_name)

	def books(self, symbol: str) -> Iterator[OrderBook]:
		prev = -1
		stream = "books"
		for rec in _iter_sorted_jsonl(self.root / "books.jsonl", self.logger, venue=self.venue_name(), stream=stream):
			if rec.get("symbol") != symbol:
				continue
			if prev >= 0 and int(rec.get("ts", 0)) - prev > 200:
				metrics.inc("gaps_detected_total", self.venue_name(), stream)
			prev = int(rec.get("ts", 0))
			yield OrderBook(**rec)

	def oi(self, symbol: str) -> Iterator[OpenInterest]:
		stream = "oi"
		for rec in _iter_sorted_jsonl(self.root / "oi.jsonl", self.logger, venue=self.venue_name(), stream=stream):
			if rec.get("symbol") != symbol:
				continue
			yield OpenInterest(**rec)

	def funding(self, symbol: str) -> Iterator[Funding]:
		stream = "funding"
		for rec in _iter_sorted_jsonl(self.root / "funding.jsonl", self.logger, venue=self.venue_name(), stream=stream):
			if rec.get("symbol") != symbol:
				continue
			yield Funding(**rec)

	def indexmark(self, symbol: str) -> Iterator[IndexMark]:
		stream = "index"
		for rec in _iter_sorted_jsonl(self.root / "index.jsonl", self.logger, venue=self.venue_name(), stream=stream):
			if rec.get("symbol") != symbol:
				continue
			yield IndexMark(**rec)

	def venue_name(self) -> str:
		return self.logger.name.split(".")[-1]


class BybitRO(FixtureRO):
	def __init__(self, root: Path | str = Path("tests/fixtures/bybit")) -> None:
		super().__init__(root=root, logger_name="capstan.adapters.bybit")


class BitgetRO(FixtureRO):
	def __init__(self, root: Path | str = Path("tests/fixtures/bitget")) -> None:
		super().__init__(root=root, logger_name="capstan.adapters.bitget")


def _iter_sorted_jsonl(path: Path, logger: logging.Logger, *, venue: str, stream: str) -> Iterator[dict[str, Any]]:
	if not path.exists():
		return
	records: list[dict[str, Any]] = []
	with path.open("r") as f:
		for line_no, line in enumerate(f, 1):
			line = line.strip()
			if not line:
				continue
			try:
				data = json.loads(line)
				if not isinstance(data, dict):
					raise ValueError("expected object")
			except Exception as exc:
				logger.warning("skip invalid jsonl at %s:%s: %s", path, line_no, exc)
				metrics.inc("records_skipped_total", venue, stream)
				continue
			records.append(data)
	records.sort(key=lambda r: int(r.get("ts", 0)))
	for rec in records:
		metrics.inc("records_read_total", venue, stream)
		yield rec
