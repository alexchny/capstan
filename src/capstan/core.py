from __future__ import annotations

import math
from collections.abc import Sequence


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
			for p_curr, qc in curr_map.items():
				if abs(p_curr - p_prev) <= price_tolerance:
					q_curr = qc
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
