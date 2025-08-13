from __future__ import annotations

from typing import Iterator

from capstan.venue_adapters import VenueAdapter
from capstan.schemas import Funding, IndexMark, OpenInterest, OrderBook


class Dummy(VenueAdapter):
	def books(self, symbol: str) -> Iterator[OrderBook]:
		if False:
			yield
		return

	def oi(self, symbol: str) -> Iterator[OpenInterest]:
		if False:
			yield
		return

	def funding(self, symbol: str) -> Iterator[Funding]:
		if False:
			yield
		return

	def indexmark(self, symbol: str) -> Iterator[IndexMark]:
		if False:
			yield
		return


def test_dummy_adapter_instantiates() -> None:
	dummy = Dummy()
	assert isinstance(dummy, VenueAdapter)
	assert list(dummy.books("BTCUSDT")) == []
	assert list(dummy.oi("BTCUSDT")) == []
	assert list(dummy.funding("BTCUSDT")) == []
	assert list(dummy.indexmark("BTCUSDT")) == [] 