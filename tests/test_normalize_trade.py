from market_micstr_lab.data.normalize import normalize_message


def test_normalize_trade_update() -> None:
    raw = {
        "source": "kraken_ws_v2",
        "capture_ts_ns": 1780000000000000001,
        "recv_seq": 2,
        "payload": {
            "channel": "trade",
            "type": "update",
            "data": [
                {
                    "symbol": "BTC/USD",
                    "side": "buy",
                    "price": "45284.1",
                    "qty": "0.025",
                    "ord_type": "market",
                    "trade_id": 123456789,
                    "timestamp": "2026-07-03T10:00:01.000000Z",
                }
            ],
        },
    }

    events = normalize_message(raw, 1)

    assert len(events) == 1
    event = events[0]
    assert event["channel"] == "trade"
    assert event["event_type"] == "trade"
    assert event["message_type"] == "update"
    assert event["side"] == "buy"
    assert event["price"] == "45284.1"
    assert event["qty"] == "0.025"
