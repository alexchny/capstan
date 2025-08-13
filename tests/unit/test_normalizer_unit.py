from __future__ import annotations

from capstan.normalizer import normalize_funding, normalize_indexmark, normalize_oi, normalize_orderbook
from capstan.schemas import Funding, IndexMark, OpenInterest, OrderBook


def test_normalize_orderbook_trims_topn() -> None:
    raw = {
        "ts": 1,
        "venue": "bybit",
        "symbol": "BTCUSDT",
        "bids": [{"price": 100, "qty": 1}, {"price": 99.9, "qty": 2}],
        "asks": [{"price": 100.1, "qty": 1}, {"price": 100.2, "qty": 2}],
        "seq": 1,
    }
    ob = normalize_orderbook(raw, top_n=1)
    assert isinstance(ob, OrderBook)
    assert len(ob.bids) == 1 and len(ob.asks) == 1


def test_normalize_oi_basic() -> None:
    raw = {"ts": 1, "venue": "bybit", "symbol": "BTCUSDT", "open_interest": 123.0}
    oi = normalize_oi(raw)
    assert isinstance(oi, OpenInterest)
    assert oi.open_interest == 123.0


def test_normalize_funding_defaults_and_order() -> None:
    raw = {"ts": 10, "venue": "bybit", "symbol": "BTCUSDT", "next_ts": 20}
    f = normalize_funding(raw)
    assert isinstance(f, Funding)
    assert f.est_rate == 0.0


def test_normalize_indexmark_positive() -> None:
    raw = {"ts": 1, "venue": "bybit", "symbol": "BTCUSDT", "index": 100.0, "mark": 100.1}
    im = normalize_indexmark(raw)
    assert isinstance(im, IndexMark)
