from __future__ import annotations

from capstan.core import (
	cancel_velocity,
	depth_weighted_sigma,
	lob10_imbalance,
	spread_z,
	sweep_detector,
)


def test_spread_z_zero_sigma() -> None:
	assert spread_z(101.0, 100.0, 0.0) == 0.0
	assert spread_z(101.0, 100.0, 1.0) == 1.0


def test_depth_weighted_sigma_basic() -> None:
	bids = [(100.0, 1.0), (99.9, 1.0)]
	asks = [(100.1, 1.0), (100.2, 1.0)]
	s = depth_weighted_sigma(bids, asks, top_n=2)
	assert s > 0.0


def test_lob10_imbalance_symmetry() -> None:
	bids = [(100.0, 1.0)] * 10
	tasks = [(100.1, 1.0)] * 10
	assert abs(lob10_imbalance(bids, tasks)) < 1e-12


def test_cancel_velocity_spoofy_depth() -> None:
	prev = [(100.0, 10.0), (99.9, 5.0), (99.8, 2.0)]
	curr = [(100.0, 1.0), (99.9, 1.0), (99.8, 1.0)]
	v = cancel_velocity(prev, curr, top_n=3)
	assert 0.0 <= v <= 1.0
	assert v > 0.5


def test_sweep_detector_thresholds() -> None:
	prev_bids = [(100.0, 1.0)]
	prev_asks = [(100.2, 1.0)]
	curr_bids = [(99.7, 1.0)]
	curr_asks = [(100.6, 1.0)]
	assert sweep_detector(prev_bids, curr_bids, prev_asks, curr_asks, threshold_bps=20.0)
	assert not sweep_detector(prev_bids, prev_bids, prev_asks, prev_asks, threshold_bps=1.0)
