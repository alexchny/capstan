from __future__ import annotations

from capstan.core import half_life_pred


def test_halflife_z_increases_decreases_thalf() -> None:
    f1 = {"z": 0.5, "depth": 2.0, "health": 90.0}
    f2 = {"z": 2.0, "depth": 2.0, "health": 90.0}
    t1 = half_life_pred(f1)
    t2 = half_life_pred(f2)
    assert t2 < t1


def test_halflife_low_health_increases_thalf() -> None:
    good = {"z": 1.0, "depth": 2.0, "health": 90.0}
    bad = {"z": 1.0, "depth": 2.0, "health": 40.0}
    assert half_life_pred(bad) > half_life_pred(good)


def test_halflife_thin_depth_increases_thalf() -> None:
    deep = {"z": 1.0, "depth": 5.0, "health": 90.0}
    thin = {"z": 1.0, "depth": 0.5, "health": 90.0}
    assert half_life_pred(thin) > half_life_pred(deep)
