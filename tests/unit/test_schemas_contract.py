from __future__ import annotations

import pytest
from pydantic import ValidationError

from capstan.schemas import Funding, IndexMark, OpenInterest, OrderBook, PriceLevel


def test_orderbook_happy() -> None:
    ob = OrderBook(
        ts=1,
        venue="bybit",
        symbol="BTCUSDT",
        bids=[PriceLevel(price=100.0, qty=1.0)],
        asks=[PriceLevel(price=101.0, qty=2.0)],
        seq=1,
    )
    assert ob.symbol == "BTCUSDT"
    assert ob.bids[0].price == 100.0


def test_pricelevel_negative_qty_rejected() -> None:
    with pytest.raises(ValidationError):
        PriceLevel(price=100.0, qty=-1.0)


def test_oi_nonnegative() -> None:
    oi = OpenInterest(ts=1, venue="bybit", symbol="BTCUSDT", open_interest=0.0)
    assert oi.open_interest == 0.0
    with pytest.raises(ValidationError):
        OpenInterest(ts=1, venue="bybit", symbol="BTCUSDT", open_interest=-0.1)


def test_funding_next_ts_after_ts() -> None:
    f = Funding(ts=10, venue="bybit", symbol="BTCUSDT", next_ts=10, est_rate=0.0)
    assert f.next_ts == 10


def test_index_mark_positive() -> None:
    im = IndexMark(ts=1, venue="bybit", symbol="BTCUSDT", index=100.0, mark=100.1)
    assert im.index > 0 and im.mark > 0
    with pytest.raises(ValidationError):
        IndexMark(ts=1, venue="bybit", symbol="BTCUSDT", index=0.0, mark=1.0)
