from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PriceLevel(BaseModel):
	model_config = ConfigDict(frozen=True)
	price: float
	qty: float

	@field_validator("price")
	@classmethod
	def _positive_price(cls, v: float) -> float:
		if v <= 0.0:
			raise ValueError("price must be > 0")
		return v

	@field_validator("qty")
	@classmethod
	def _nonnegative_qty(cls, v: float) -> float:
		if v < 0.0:
			raise ValueError("qty must be >= 0")
		return v


class OrderBook(BaseModel):
	model_config = ConfigDict(frozen=True)
	ts: int = Field(..., ge=0)
	venue: str
	symbol: str
	bids: list[PriceLevel]
	asks: list[PriceLevel]
	seq: int = Field(..., ge=0)


class OpenInterest(BaseModel):
	model_config = ConfigDict(frozen=True)
	ts: int = Field(..., ge=0)
	venue: str
	symbol: str
	open_interest: float

	@field_validator("open_interest")
	@classmethod
	def _nonnegative_oi(cls, v: float) -> float:
		if v < 0.0:
			raise ValueError("open_interest must be >= 0")
		return v


class Funding(BaseModel):
	model_config = ConfigDict(frozen=True)
	ts: int = Field(..., ge=0)
	venue: str
	symbol: str
	next_ts: int = Field(..., ge=0)
	est_rate: float
	term_structure: Mapping[int, float] = Field(default_factory=dict)

	@model_validator(mode="after")
	def _check_next_after_ts(self) -> Funding:
		if self.next_ts < self.ts:
			raise ValueError("next_ts must be >= ts")
		return self


class IndexMark(BaseModel):
	model_config = ConfigDict(frozen=True)
	ts: int = Field(..., ge=0)
	venue: str
	symbol: str
	index: float
	mark: float

	@field_validator("index", "mark")
	@classmethod
	def _positive_values(cls, v: float) -> float:
		if v <= 0.0:
			raise ValueError("value must be > 0")
		return v
