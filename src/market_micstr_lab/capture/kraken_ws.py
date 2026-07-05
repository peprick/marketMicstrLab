import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import websockets

from market_micstr_lab.data.jsonl import append_jsonl
from market_micstr_lab.data.schemas import DEFAULT_SOURCE, SCHEMA_VERSION

KRAKEN_WS_URL = "wss://ws.kraken.com/v2"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def subscribe_message(
    channel: str,
    symbol: str,
    depth: int = 10,
    snapshot: bool = True,
) -> dict:
    if channel not in {"book", "trade"}:
        raise ValueError(f"Unsupported channel: {channel}")

    params = {
        "channel": channel,
        "symbol": [symbol],
        "snapshot": snapshot,
    }

    if channel == "book":
        params["depth"] = depth

    return {"method": "subscribe", "params": params}


def capture_envelope(payload: dict, recv_seq: int, depth: int | None = None) -> dict:
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "source": DEFAULT_SOURCE,
        "capture_ts_ns": time.time_ns(),
        "capture_time_utc": utc_now_iso(),
        "recv_seq": recv_seq,
        "payload": payload,
    }

    if depth is not None:
        envelope["depth"] = depth

    return envelope


async def capture_messages(
    output_path: str | Path,
    channel: str,
    symbol: str,
    depth: int = 10,
    snapshot: bool = True,
    max_messages: int | None = None,
    seconds: float | None = None,
    url: str = KRAKEN_WS_URL,
    connect: Any = websockets.connect,
) -> int:
    if max_messages is None and seconds is None:
        raise ValueError("max_messages or seconds must be provided")

    stop_at = time.monotonic() + seconds if seconds is not None else None
    subscription = subscribe_message(channel, symbol, depth, snapshot)
    count = 0

    async with connect(url) as websocket:
        await websocket.send(json.dumps(subscription))

        while max_messages is None or count < max_messages:
            timeout = None
            if stop_at is not None:
                timeout = stop_at - time.monotonic()
                if timeout <= 0:
                    break

            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            except (
                asyncio.TimeoutError,
                TimeoutError,
                websockets.exceptions.ConnectionClosed,
            ):
                break

            count += 1
            payload = json.loads(message)
            envelope_depth = depth if channel == "book" else None
            append_jsonl(output_path, capture_envelope(payload, count, envelope_depth))

    return count
