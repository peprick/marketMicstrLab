# C++ Replay Benchmark

## Setup

- Tool: `mml_replay_benchmark`
- Data mode: deterministic synthetic top-of-book updates
- Book depth: 10 levels per side
- Event count: 100,000 updates
- Machine: local development machine

## Command

```bash
./build/mml_replay_benchmark --events 100000 --depth 10
```

## Result

```json
{
  "events": 100000,
  "depth": 10,
  "elapsed_ns": 2940166,
  "events_per_second": 34011700,
  "ns_per_event": 29.4017,
  "bid_levels": 10,
  "ask_levels": 10
}
```

## Interpretation

The benchmark exercises the C++ `OrderBook` update path without JSON parsing or file I/O. It is intended as a focused critical-path benchmark, not an end-to-end market-data pipeline benchmark.

The measured local throughput is roughly 34 million synthetic updates per second, or about 29 ns per update, for a stable 10-by-10 book.

Future benchmark work should add:

- JSONL parsing overhead.
- Larger and variable depth books.
- Snapshot-heavy workloads.
- Latency distribution percentiles across repeated runs.
