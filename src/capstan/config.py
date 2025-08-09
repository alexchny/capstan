from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, Field


class PositionCaps(BaseModel):
    per_pair_usd: int = Field(..., ge=0)
    per_venue_usd: int = Field(..., ge=0)
    global_usd: int = Field(..., ge=0)


class HFHConfig(BaseModel):
    k_by_pair: Mapping[str, float]
    vol_window_min: int = Field(..., ge=1)


class LLCAConfig(BaseModel):
    z_in: float
    z_out: float
    max_hold_sec: int = Field(..., ge=1)


class RiskConfig(BaseModel):
    intraday_dd_pct: float
    venue_health_thresholds: Mapping[str, int]


class RuntimeConfig(BaseModel):
    pairs: list[str]
    venues: list[str]
    position_caps: PositionCaps
    hfh: HFHConfig
    llca: LLCAConfig
    risk: RiskConfig
    latency_penalty_lambda: float


def env(key: str, default: str = "") -> str:
    import os

    return os.environ.get(key, default) 