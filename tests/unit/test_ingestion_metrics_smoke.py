from __future__ import annotations

from capstan import metrics
from capstan.venue_adapters import BitgetRO, BybitRO


def test_ingestion_metrics_increment() -> None:
	metrics.reset()
	bybit = BybitRO()
	bitget = BitgetRO()
	list(bybit.books("BTCUSDT"))
	list(bybit.oi("BTCUSDT"))
	list(bitget.funding("BTCUSDT"))
	list(bitget.indexmark("BTCUSDT"))
	assert metrics.get("records_read_total", "bybit", "books") > 0
	assert metrics.get("records_read_total", "bybit", "oi") > 0
	assert metrics.get("records_read_total", "bitget", "funding") > 0
	assert metrics.get("records_read_total", "bitget", "index") > 0
