from __future__ import annotations

import math
from collections.abc import Sequence
from statistics import pstdev

from capstan.schemas import Funding, OrderBook


def spread_z(price_a: float, price_b: float, sigma_spread: float) -> float:
    if sigma_spread <= 0.0:
        return 0.0
    return (price_a - price_b) / sigma_spread


def depth_weighted_sigma(
    bids: Sequence[tuple[float, float]],
    asks: Sequence[tuple[float, float]],
    top_n: int = 10,
) -> float:
    if not bids or not asks:
        return 0.0
    best_bid = bids[0][0]
    best_ask = asks[0][0]
    mid = 0.5 * (best_bid + best_ask)
    weights_sum = 0.0
    var_sum = 0.0
    for price, qty in list(bids)[:top_n]:
        w = max(float(qty), 0.0)
        weights_sum += w
        var_sum += w * (float(price) - mid) ** 2
    for price, qty in list(asks)[:top_n]:
        w = max(float(qty), 0.0)
        weights_sum += w
        var_sum += w * (float(price) - mid) ** 2
    if weights_sum <= 0.0:
        return 0.0
    return math.sqrt(var_sum / weights_sum)


def lob10_imbalance(
    bids: Sequence[tuple[float, float]],
    asks: Sequence[tuple[float, float]],
) -> float:
    sum_bid = sum(max(float(q), 0.0) for _p, q in list(bids)[:10])
    sum_ask = sum(max(float(q), 0.0) for _p, q in list(asks)[:10])
    den = sum_bid + sum_ask
    if den <= 0.0:
        return 0.0
    return (sum_bid - sum_ask) / den


def cancel_velocity(
    prev: Sequence[tuple[float, float]],
    curr: Sequence[tuple[float, float]],
    *,
    price_tolerance: float = 1e-9,
    top_n: int | None = None,
) -> float:
    def _to_map(levels: Sequence[tuple[float, float]]) -> dict[float, float]:
        m: dict[float, float] = {}
        for i, (p, q) in enumerate(levels):
            if top_n is not None and i >= top_n:
                break
            m[float(p)] = m.get(float(p), 0.0) + max(float(q), 0.0)
        return m

    prev_map = _to_map(prev)
    curr_map = _to_map(curr)
    prev_total = sum(prev_map.values())
    if prev_total <= 0.0:
        return 0.0
    removed = 0.0
    for p_prev, q_prev in prev_map.items():
        q_curr = 0.0
        if p_prev in curr_map:
            q_curr = curr_map[p_prev]
        else:
            for p_curr, qty_curr in curr_map.items():
                if abs(p_curr - p_prev) <= price_tolerance:
                    q_curr = qty_curr
                    break
        removed += max(q_prev - q_curr, 0.0)
    vel = removed / prev_total
    if vel < 0.0:
        return 0.0
    if vel > 1.0:
        return 1.0
    return vel


def sweep_detector(
    prev_bids: Sequence[tuple[float, float]],
    curr_bids: Sequence[tuple[float, float]],
    prev_asks: Sequence[tuple[float, float]],
    curr_asks: Sequence[tuple[float, float]],
    *,
    threshold_bps: float = 10.0,
) -> bool:
    def _best(levels: Sequence[tuple[float, float]]) -> float | None:
        if not levels:
            return None
        return float(levels[0][0])

    pb = _best(prev_bids)
    cb = _best(curr_bids)
    pa = _best(prev_asks)
    ca = _best(curr_asks)
    if pb is None or cb is None or pa is None or ca is None:
        return False
    prev_mid = 0.5 * (pb + pa)
    if prev_mid <= 0.0:
        return False
    prev_spread = max(pa - pb, 0.0)
    curr_spread = max(ca - cb, 0.0)
    widened = curr_spread > prev_spread
    widen_bps = (curr_spread - prev_spread) / prev_mid * 1e4 if widened else 0.0
    return widened and widen_bps >= threshold_bps


def oi_delta(prev_oi: float, curr_oi: float, dt_sec: float) -> tuple[float, float]:
    delta = float(curr_oi) - float(prev_oi)
    if dt_sec <= 0.0:
        return delta, 0.0
    return delta, delta / float(dt_sec)


def funding_nowcast(
    venue_est: float,
    recent_realized: Sequence[float],
    mark_spot_drift: float,
    leader_momentum: float,
    *,
    w_est: float = 0.5,
    w_realized: float = 0.2,
    w_drift: float = 0.1,
    w_momo: float = 0.2,
    clamp_abs: float = 0.01,
) -> float:
    mean_realized = 0.0
    if recent_realized:
        mean_realized = sum(float(x) for x in recent_realized) / float(
            len(recent_realized)
        )
    blend = (
        w_est * float(venue_est)
        + w_realized * mean_realized
        + w_drift * float(mark_spot_drift)
        + w_momo * float(leader_momentum)
    )
    if blend > clamp_abs:
        return clamp_abs
    if blend < -clamp_abs:
        return -clamp_abs
    return blend


def half_life_pred(features: dict[str, float]) -> float:
    z = abs(float(features.get("z", 0.0)))
    depth = max(float(features.get("depth", 0.0)), 0.0)
    health = float(features.get("health", 80.0))

    health_low = 1.0 - max(0.0, min(health, 100.0)) / 100.0
    depth_thin = 1.0 / (1.0 + depth)
    base = 3.0
    pred = base - 0.8 * min(z, 5.0) + 2.0 * health_low + 2.0 * depth_thin
    return max(0.1, min(10.0, pred))


def make_llca_features(
    books_a: Sequence[OrderBook],
    books_b: Sequence[OrderBook],
    health_a: float,
    health_b: float,
) -> dict[str, float]:
    if not books_a or not books_b:
        return {
            "z": 0.0,
            "depth_ratio": 0.0,
            "imbalance": 0.0,
            "update_rate": 0.0,
            "health_min": min(health_a, health_b),
        }

    def _mid(ob: OrderBook) -> float:
        bid_price = ob.bids[0].price if ob.bids else 0.0
        ask_price = ob.asks[0].price if ob.asks else 0.0
        return (
            0.5 * (bid_price + ask_price)
            if (bid_price > 0.0 and ask_price > 0.0)
            else 0.0
        )

    spreads: list[float] = []
    for ob_a, ob_b in zip(books_a, books_b, strict=False):
        spreads.append(_mid(ob_a) - _mid(ob_b))
    sigma = pstdev(spreads) if len(spreads) > 1 else 0.0
    z = spread_z(_mid(books_a[-1]), _mid(books_b[-1]), sigma)

    def _depth(ob: OrderBook) -> float:
        bid_qty_sum = sum(level.qty for level in ob.bids[:10])
        ask_qty_sum = sum(level.qty for level in ob.asks[:10])
        return float(bid_qty_sum + ask_qty_sum)

    depth_a = _depth(books_a[-1])
    depth_b = _depth(books_b[-1])
    depth_ratio = depth_a / depth_b if depth_b > 0.0 else 0.0

    def _imb(ob: OrderBook) -> float:
        b = [(level.price, level.qty) for level in ob.bids]
        a = [(level.price, level.qty) for level in ob.asks]
        return lob10_imbalance(b, a)

    imbalance = 0.5 * (_imb(books_a[-1]) + _imb(books_b[-1]))

    def _rate(books: Sequence[OrderBook]) -> float:
        if len(books) < 2:
            return 0.0
        span_ms = max(1, books[-1].ts - books[0].ts)
        return len(books) / (span_ms / 1000.0)

    update_rate = 0.5 * (_rate(books_a) + _rate(books_b))
    health_min = float(min(health_a, health_b))
    return {
        "z": float(z),
        "depth_ratio": float(depth_ratio),
        "imbalance": float(imbalance),
        "update_rate": float(update_rate),
        "health_min": health_min,
    }


def make_hfh_features(
    funding_window: Sequence[Funding],
    vol_est: float,
    mark_spot_drift: float,
) -> dict[str, float]:
    venue_est = float(funding_window[-1].est_rate) if funding_window else 0.0
    realized = (
        [float(f.est_rate) for f in funding_window[-5:]] if funding_window else []
    )
    momo = 0.0
    if funding_window and len(funding_window) >= 2:
        momo = float(funding_window[-1].est_rate) - float(funding_window[0].est_rate)
    E_funding_T = funding_nowcast(
        venue_est=venue_est,
        recent_realized=realized,
        mark_spot_drift=mark_spot_drift,
        leader_momentum=momo,
    )
    return {"E_funding_T": float(E_funding_T), "sigma_T": float(vol_est)}
