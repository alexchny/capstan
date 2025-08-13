from __future__ import annotations

from capstan.core import make_hfh_features, make_llca_features
from capstan.schemas import Funding, OrderBook, PriceLevel


def _ob(
    ts: int, bid: float, ask: float, bqty: float = 1.0, aqty: float = 1.0
) -> OrderBook:
    return OrderBook(
        ts=ts,
        venue="v",
        symbol="S",
        bids=[PriceLevel(price=bid, qty=bqty)],
        asks=[PriceLevel(price=ask, qty=aqty)],
        seq=1,
    )


def test_make_llca_features_basic() -> None:
    books_a = [_ob(1000, 100.0, 100.1), _ob(1100, 100.05, 100.15)]
    books_b = [_ob(1000, 99.9, 100.0), _ob(1100, 99.95, 100.05)]
    f = make_llca_features(books_a, books_b, health_a=90.0, health_b=80.0)
    assert set(f.keys()) == {
        "z",
        "depth_ratio",
        "imbalance",
        "update_rate",
        "health_min",
    }
    assert f["health_min"] == 80.0
    assert f["update_rate"] > 0.0


def test_make_hfh_features_basic() -> None:
    fund = [
        Funding(
            ts=1000,
            venue="v",
            symbol="S",
            next_ts=2000,
            est_rate=0.0001,
            term_structure={},
        ),
        Funding(
            ts=2000,
            venue="v",
            symbol="S",
            next_ts=3000,
            est_rate=0.0002,
            term_structure={},
        ),
    ]
    f = make_hfh_features(fund, vol_est=0.02, mark_spot_drift=0.0)
    assert set(f.keys()) == {"E_funding_T", "sigma_T"}
    assert f["sigma_T"] == 0.02
