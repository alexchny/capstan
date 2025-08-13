from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterator

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
		for rec in _iter_sorted_jsonl(self.root / "books.jsonl", self.logger):
			if rec.get("symbol") != symbol:
				continue
			yield OrderBook(**rec)

	def oi(self, symbol: str) -> Iterator[OpenInterest]:
		for rec in _iter_sorted_jsonl(self.root / "oi.jsonl", self.logger):
			if rec.get("symbol") != symbol:
				continue
			yield OpenInterest(**rec)

	def funding(self, symbol: str) -> Iterator[Funding]:
		for rec in _iter_sorted_jsonl(self.root / "funding.jsonl", self.logger):
			if rec.get("symbol") != symbol:
				continue
			yield Funding(**rec)

	def indexmark(self, symbol: str) -> Iterator[IndexMark]:
		for rec in _iter_sorted_jsonl(self.root / "index.jsonl", self.logger):
			if rec.get("symbol") != symbol:
				continue
			yield IndexMark(**rec)


class BybitRO(FixtureRO):
	def __init__(self, root: Path | str = Path("tests/fixtures/bybit")) -> None:
		super().__init__(root=root, logger_name="capstan.adapters.bybit")


class BitgetRO(FixtureRO):
	def __init__(self, root: Path | str = Path("tests/fixtures/bitget")) -> None:
		super().__init__(root=root, logger_name="capstan.adapters.bitget")


def _iter_sorted_jsonl(path: Path, logger: logging.Logger) -> Iterator[dict[str, Any]]:
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
				continue
			records.append(data)
	records.sort(key=lambda r: int(r.get("ts", 0)))
	for rec in records:
		yield rec
