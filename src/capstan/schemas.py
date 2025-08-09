from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel


class PriceLevel(BaseModel):
    price: float
    qty: float


class OrderBook(BaseModel):
    ts: int
    venue: str
    symbol: str
    bids: list[PriceLevel]
    asks: list[PriceLevel]
    seq: int
    latency_ms: int


class Trade(BaseModel):
    ts: int
    venue: str
    symbol: str
    side: Literal["buy", "sell"]
    price: float
    qty: float


class Funding(BaseModel):
    ts: int
    venue: str
    symbol: str
    next_ts: int
    est_rate: float
    term_structure: Mapping[int, float]


class IndexMark(BaseModel):
    ts: int
    venue: str
    symbol: str
    index: float
    mark: float


class Position(BaseModel):
    qty: float
    entry_px: float
    u_pnl: float


class Account(BaseModel):
    ts: int
    venue: str
    balances: dict[str, float]
    positions: dict[str, Position]


class VenueHealth(BaseModel):
    ts: int
    venue: str
    rest_p95_ms: int
    ws_gap_ms: int
    error_rate: float
    partial_fill_pct: float
    cancel_rate: float
    mark_drift_bps: float
    status: Literal["OK", "DEGRADED", "BAD"] 