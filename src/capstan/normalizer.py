from __future__ import annotations

from collections.abc import Mapping, Sequence

from capstan.schemas import Funding, IndexMark, OpenInterest, OrderBook, PriceLevel


def _to_int(value: object) -> int:
	if isinstance(value, bool):
		raise ValueError("bool not allowed")
	if isinstance(value, int):
		return value
	if isinstance(value, float):
		return int(value)
	if isinstance(value, str):
		return int(value)
	raise ValueError("invalid int")


def _to_float(value: object) -> float:
	if isinstance(value, bool):
		raise ValueError("bool not allowed")
	if isinstance(value, int | float):
		return float(value)
	if isinstance(value, str):
		return float(value)
	raise ValueError("invalid float")


def _levels(obj: object, top_n: int | None) -> list[PriceLevel]:
	out: list[PriceLevel] = []
	if isinstance(obj, Sequence) and not isinstance(obj, str | bytes):
		for item in obj:
			if not isinstance(item, Mapping):
				continue
			try:
				price = _to_float(item.get("price"))
				qty = _to_float(item.get("qty"))
			except Exception:
				continue
			out.append(PriceLevel(price=price, qty=qty))
			if top_n is not None and len(out) >= top_n:
				break
	return out


def normalize_orderbook(raw: Mapping[str, object], *, top_n: int | None = 10) -> OrderBook:
	bids = _levels(raw.get("bids"), top_n)
	asks = _levels(raw.get("asks"), top_n)
	return OrderBook(
		ts=_to_int(raw["ts"]),
		venue=str(raw["venue"]),
		symbol=str(raw["symbol"]),
		bids=bids,
		asks=asks,
		seq=_to_int(raw.get("seq", 0)),
	)


def normalize_oi(raw: Mapping[str, object]) -> OpenInterest:
	return OpenInterest(
		ts=_to_int(raw["ts"]),
		venue=str(raw["venue"]),
		symbol=str(raw["symbol"]),
		open_interest=_to_float(raw["open_interest"]),
	)


def normalize_funding(raw: Mapping[str, object]) -> Funding:
	term_struct_raw = raw.get("term_structure", {})
	term_struct: dict[int, float] = {}
	if isinstance(term_struct_raw, Mapping):
		for k, v in term_struct_raw.items():
			try:
				kk = _to_int(k) if not isinstance(k, int) else k
				vv = _to_float(v)
			except Exception:
				continue
			term_struct[kk] = vv
	return Funding(
		ts=_to_int(raw["ts"]),
		venue=str(raw["venue"]),
		symbol=str(raw["symbol"]),
		next_ts=_to_int(raw["next_ts"]),
		est_rate=_to_float(raw.get("est_rate", 0.0)),
		term_structure=term_struct,
	)


def normalize_indexmark(raw: Mapping[str, object]) -> IndexMark:
	return IndexMark(
		ts=_to_int(raw["ts"]),
		venue=str(raw["venue"]),
		symbol=str(raw["symbol"]),
		index=_to_float(raw["index"]),
		mark=_to_float(raw["mark"]),
	)
