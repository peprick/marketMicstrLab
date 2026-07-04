from decimal import Decimal
from typing import Any

from market_micstr_lab.data.schemas import DEFAULT_SOURCE, SCHEMA_VERSION


def _as_str(value: Any) -> str:
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def _levels(levels: list[dict]) -> list[list[str]]:
    return [[_as_str(level["price"]), _as_str(level["qty"])] for level in levels]




def normalize_message(raw_envelope: dict, bookChannelFlag: int) -> list[dict]:
    payload = raw_envelope["payload"]

    if (payload.get("channel") != "book" and bookChannelFlag == 0) or (payload.get("channel") != "trade" and bookChannelFlag == 1):
        return []

    msg_type = payload.get("type")
    if msg_type not in {"snapshot", "update"}:
        return []

    events = []
    for item in payload.get("data", []):
        if(bookChannelFlag == 0):
            events.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "source": raw_envelope.get("source", DEFAULT_SOURCE),
                    "channel": "book",
                    "event_type": msg_type,
                    "symbol": item["symbol"],
                    "depth": raw_envelope.get("depth"),
                    "exchange_ts": item["timestamp"],
                    "capture_ts_ns": raw_envelope["capture_ts_ns"],
                    "recv_seq": raw_envelope["recv_seq"],
                    "checksum": item.get("checksum"),
                    "bids": _levels(item.get("bids", [])),
                    "asks": _levels(item.get("asks", []))
                }
            )
        else:
            events.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "source": raw_envelope.get("source", DEFAULT_SOURCE),
                    "channel": "trade",
                    "event_type": "trade",
                    "symbol": item["symbol"],
                    "exchange_ts": item["timestamp"],
                    "capture_ts_ns": raw_envelope["capture_ts_ns"],
                    "recv_seq": raw_envelope["recv_seq"],
                    "side": item["side"],
                    "price": _as_str(item["price"]),
                    "qty": _as_str(item["qty"]),
                    "ord_type": item.get("ord_type"),
                    "trade_id": item.get("trade_id"),
                    "message_type": msg_type
                }
            )

    return events
