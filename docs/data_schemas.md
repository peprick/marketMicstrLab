# Data Schemas

This document defines the first internal data contracts for Market Microstructure Lab.

The project keeps two kinds of files separate:

- Raw JSONL: exchange messages wrapped with local capture metadata.
- Processed JSONL: normalized events used by replay, research, and future C++ ingestion.

JSONL means one JSON object per line. This format is easy to append, inspect, test, and replay in order.

## Directory Policy

Use these locations for data:

```text
data/raw/
  sample_book.jsonl

data/processed/
  sample_book_events.jsonl

tests/fixtures/
  raw_book.jsonl
```

Use `data/` for local/manual samples and future captures. Use `tests/fixtures/` for tiny deterministic examples committed with tests.

Do not store market-data files inside `src/market_micstr_lab/`; that folder is for package code.

## Raw Envelope

Every exchange payload should be wrapped before it is written to raw JSONL.

```json
{
  "schema_version": 1,
  "source": "kraken_ws_v2",
  "depth": 10,
  "capture_ts_ns": 1780000000000000000,
  "recv_seq": 1,
  "payload": {
    "channel": "book",
    "type": "snapshot",
    "data": []
  }
}
```

Fields:

- `schema_version`: internal schema version.
- `source`: data source identifier.
- `depth`: subscribed book depth when relevant.
- `capture_ts_ns`: local receive/capture timestamp in nanoseconds.
- `recv_seq`: local monotonically increasing receive counter.
- `payload`: original exchange message payload.

## Normalized Book Event

Book messages become normalized book events.

```json
{
  "schema_version": 1,
  "source": "kraken_ws_v2",
  "channel": "book",
  "event_type": "snapshot",
  "symbol": "BTC/USD",
  "depth": 10,
  "exchange_ts": "2026-07-03T10:00:00.000000Z",
  "capture_ts_ns": 1780000000000000000,
  "recv_seq": 1,
  "checksum": 3310070434,
  "bids": [["45283.5", "0.10000000"]],
  "asks": [["45285.2", "0.00100000"]]
}
```

Rules:

- `event_type` is `snapshot` or `update`.
- `bids` and `asks` are lists of `[price, qty]`.
- Prices and quantities stay as strings at the JSON boundary.
- A quantity of `"0"` or `"0.00000000"` should later be interpreted as removing that price level from the book.

## Normalized Trade Event

Trade messages become normalized trade events.

```json
{
  "schema_version": 1,
  "source": "kraken_ws_v2",
  "channel": "trade",
  "event_type": "trade",
  "symbol": "BTC/USD",
  "exchange_ts": "2026-07-03T10:00:01.000000Z",
  "capture_ts_ns": 1780000000000000001,
  "recv_seq": 2,
  "side": "buy",
  "price": "45284.1",
  "qty": "0.025",
  "ord_type": "market",
  "trade_id": 123456789,
  "message_type": "update"
}
```

Rules:

- `event_type` is always `trade`.
- `message_type` preserves whether the exchange message was a `snapshot` or `update`.
- Prices and quantities stay as strings at the JSON boundary.

## Current Channel Flag Convention

The current normalizer uses this temporary mapping:

```text
book  -> 0
trade -> 1
```

This is intentionally documented because the current pipeline and CLI use it. A future cleanup can replace the numeric flag with explicit functions or an enum.

## Validation Expectations

At this phase, tests should prove:

- Raw JSONL can be written and read back.
- Book messages normalize into book events.
- Trade messages normalize into trade events.
- The pipeline converts raw JSONL into processed JSONL.
- The CLI can run the pipeline from the command line.

Later phases will add order-book reconstruction checks, checksum validation, and replay invariants.
