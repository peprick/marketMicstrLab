# C++ Replay Benchmark

## Setup

- Tool: `mml_replay_benchmark`
- Data mode: deterministic synthetic top-of-book updates
- Configurable book depth
- Configurable event count
- Configurable repeated runs

## Command

```bash
./build/mml_replay_benchmark --events 100000 --depth 10 --runs 5
```

## Output Fields

- `events`: synthetic updates per run.
- `depth`: book levels initialized on each side.
- `runs`: repeated benchmark runs.
- `elapsed_ns_total`: total measured nanoseconds across runs.
- `mean_events_per_second`: aggregate throughput.
- `mean_ns_per_event`: average update latency.
- `p50_ns_per_event`: median per-run update latency.
- `p95_ns_per_event`: p95 per-run update latency.
- `p99_ns_per_event`: p99 per-run update latency.
- `bid_levels` and `ask_levels`: final book depth counts.

## Interpretation

The benchmark exercises the C++ `OrderBook` update path without JSON parsing or file I/O. It is intended as a focused critical-path benchmark, not an end-to-end market-data pipeline benchmark. Timing values depend on machine, compiler, build type, and current system load, so generated numbers should be recorded with local environment details when used in reports.

The separate normalized JSONL replay path validates the file-ingestion route:

```bash
./build/mml_replay_jsonl --input data/processed/book_events.jsonl --scale 100000000
```

That command expects normalized book events produced by the Python normalization pipeline.

The JSONL replay output reports event counts, snapshot/update counts, final book validity, and final top-of-book levels in fixed-point integer units.

Future benchmark work should add larger variable-depth books, snapshot-heavy workloads, and measurements on longer real captures.
