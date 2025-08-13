from __future__ import annotations

from pathlib import Path

from capstan.venue_adapters import BybitRO, VenueAdapter


def test_contract_methods_exist() -> None:
	adapter: VenueAdapter = BybitRO()
	for name in ("books", "oi", "funding", "indexmark"):
		assert hasattr(adapter, name)


def test_iterates_to_eof_ordered() -> None:
	adapter = BybitRO(root=Path("tests/fixtures/bybit"))
	# books
	prev = -1
	count = 0
	for ob in adapter.books("BTCUSDT"):
		assert ob.ts >= prev
		prev = ob.ts
		count += 1
	assert count > 0
	# oi
	prev = -1
	count = 0
	for oi in adapter.oi("BTCUSDT"):
		assert oi.ts >= prev
		prev = oi.ts
		count += 1
	assert count > 0
	# funding
	prev = -1
	count = 0
	for f in adapter.funding("BTCUSDT"):
		assert f.ts >= prev
		prev = f.ts
		count += 1
	assert count > 0
	# index
	prev = -1
	count = 0
	for im in adapter.indexmark("BTCUSDT"):
		assert im.ts >= prev
		prev = im.ts
		count += 1
	assert count > 0
