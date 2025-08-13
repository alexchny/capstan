from __future__ import annotations

from capstan.core import funding_nowcast, oi_delta


def test_oi_delta_and_velocity() -> None:
    # flat
    d, v = oi_delta(1000.0, 1000.0, dt_sec=60.0)
    assert d == 0.0 and v == 0.0
    # spike
    d, v = oi_delta(1000.0, 1060.0, dt_sec=60.0)
    assert d == 60.0 and v == 1.0
    # dt=0
    d, v = oi_delta(1000.0, 1020.0, dt_sec=0.0)
    assert d == 20.0 and v == 0.0


def test_funding_nowcast_monotone_and_clamp() -> None:
    base = funding_nowcast(
        venue_est=0.0001,
        recent_realized=[0.0],
        mark_spot_drift=0.0,
        leader_momentum=0.0,
    )
    higher = funding_nowcast(
        venue_est=0.0002,
        recent_realized=[0.0],
        mark_spot_drift=0.0,
        leader_momentum=0.0,
    )
    assert higher >= base
    # clamp
    clamped = funding_nowcast(
        venue_est=1.0, recent_realized=[1.0], mark_spot_drift=1.0, leader_momentum=1.0
    )
    assert clamped == 0.01
    clamped_neg = funding_nowcast(
        venue_est=-1.0,
        recent_realized=[-1.0],
        mark_spot_drift=-1.0,
        leader_momentum=-1.0,
    )
    assert clamped_neg == -0.01
