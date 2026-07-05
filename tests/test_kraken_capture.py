import asyncio
import json
import subprocess
import sys

import pytest

from market_micstr_lab.capture.kraken_ws import (
    capture_envelope,
    capture_messages,
    subscribe_message,
)
from market_micstr_lab.data.jsonl import read_jsonl


class FakeWebSocket:
    def __init__(self, messages: list[dict]) -> None:
        self.messages = [json.dumps(message) for message in messages]
        self.sent_messages: list[dict] = []

    async def send(self, message: str) -> None:
        self.sent_messages.append(json.loads(message))

    async def recv(self) -> str:
        if not self.messages:
            raise TimeoutError("No fake messages left")
        return self.messages.pop(0)


class FakeConnect:
    def __init__(self, websocket: FakeWebSocket) -> None:
        self.websocket = websocket
        self.urls: list[str] = []

    def __call__(self, url: str):
        self.urls.append(url)
        return self

    async def __aenter__(self) -> FakeWebSocket:
        return self.websocket

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


def test_subscribe_message_for_book_includes_depth() -> None:
    message = subscribe_message("book", "BTC/USD", depth=10, snapshot=True)

    assert message == {
        "method": "subscribe",
        "params": {
            "channel": "book",
            "symbol": ["BTC/USD"],
            "snapshot": True,
            "depth": 10,
        },
    }


def test_subscribe_message_for_trade_omits_depth() -> None:
    message = subscribe_message("trade", "BTC/USD", depth=10, snapshot=False)

    assert message == {
        "method": "subscribe",
        "params": {
            "channel": "trade",
            "symbol": ["BTC/USD"],
            "snapshot": False,
        },
    }


def test_subscribe_message_rejects_unknown_channel() -> None:
    with pytest.raises(ValueError, match="Unsupported channel"):
        subscribe_message("ticker", "BTC/USD")


def test_capture_envelope_adds_metadata() -> None:
    payload = {"channel": "book", "type": "snapshot", "data": []}

    envelope = capture_envelope(payload, recv_seq=3, depth=10)

    assert envelope["schema_version"] == 1
    assert envelope["source"] == "kraken_ws_v2"
    assert envelope["recv_seq"] == 3
    assert envelope["depth"] == 10
    assert envelope["payload"] == payload
    assert isinstance(envelope["capture_ts_ns"], int)
    assert envelope["capture_time_utc"].endswith("Z")


def test_capture_messages_writes_raw_jsonl_with_fake_websocket(tmp_path) -> None:
    output_path = tmp_path / "raw_book.jsonl"
    websocket = FakeWebSocket(
        [
            {"channel": "book", "type": "snapshot", "data": [{"symbol": "BTC/USD"}]},
            {"channel": "book", "type": "update", "data": [{"symbol": "BTC/USD"}]},
        ]
    )
    fake_connect = FakeConnect(websocket)

    count = asyncio.run(
        capture_messages(
            output_path=output_path,
            channel="book",
            symbol="BTC/USD",
            depth=10,
            max_messages=2,
            url="wss://example.test",
            connect=fake_connect,
        )
    )

    rows = list(read_jsonl(output_path))

    assert count == 2
    assert fake_connect.urls == ["wss://example.test"]
    assert websocket.sent_messages == [subscribe_message("book", "BTC/USD", depth=10)]
    assert rows[0]["recv_seq"] == 1
    assert rows[1]["recv_seq"] == 2
    assert rows[0]["depth"] == 10
    assert rows[0]["payload"]["type"] == "snapshot"
    assert rows[1]["payload"]["type"] == "update"


def test_capture_messages_stops_when_socket_has_no_more_messages(tmp_path) -> None:
    output_path = tmp_path / "raw_book.jsonl"
    websocket = FakeWebSocket(
        [
            {"channel": "book", "type": "snapshot", "data": [{"symbol": "BTC/USD"}]},
        ]
    )

    count = asyncio.run(
        capture_messages(
            output_path=output_path,
            channel="book",
            symbol="BTC/USD",
            depth=10,
            max_messages=5,
            url="wss://example.test",
            connect=FakeConnect(websocket),
        )
    )

    rows = list(read_jsonl(output_path))

    assert count == 1
    assert len(rows) == 1
    assert rows[0]["recv_seq"] == 1


def test_capture_messages_requires_stop_condition(tmp_path) -> None:
    with pytest.raises(ValueError, match="max_messages or seconds must be provided"):
        asyncio.run(
            capture_messages(
                output_path=tmp_path / "raw.jsonl",
                channel="book",
                symbol="BTC/USD",
                connect=FakeConnect(FakeWebSocket([])),
            )
        )


def test_capture_kraken_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "market_micstr_lab.cli.capture_kraken", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Capture raw Kraken WebSocket messages to JSONL." in result.stdout
    assert "--max-messages" in result.stdout
