# Market Microstructure Lab

Market Microstructure Lab is a flagship quant research and engineering project focused on
order-book dynamics, short-horizon price movement, and realistic execution assumptions.

The project is intentionally split into two halves:

- Python research layer: data capture, cleaning, feature engineering, labeling, modeling, and charts.
- C++ critical path: order-book replay, deterministic simulation, execution assumptions, tests, and benchmarks.

## Current Status

Phase 1 scaffold is in place. No data collector, order-book engine, trading logic, or predictive model has been implemented yet.

## Core Research Question

Can short-horizon order-book imbalance, spread, depth, and event-intensity features predict mid-price movement after accounting for realistic fees, latency, and execution assumptions?

## Planned Data Source

Initial data source: Kraken public L2 order-book WebSocket for BTC/USD.

Why this source:

- Public market data access.
- Snapshot and incremental update messages.
- Configurable book depth.
- Checksum support for book-integrity validation.

## Planned Milestones

1. Define event schema and research assumptions.
2. Capture and normalize order-book snapshots and updates.
3. Build deterministic C++ order-book replay.
4. Add feature extraction and labeling in Python.
5. Build baseline predictive models and robust validation.
6. Add execution simulator with fees, slippage, latency, and queue assumptions.
7. Produce charts, benchmarks, tests, and a 6-10 page research writeup.

## Repository Layout

```text
marketMicstrLab/
  cpp/                  C++ replay and simulation components
  data/                 Local raw and processed data, ignored by git
  docs/                 Project specs and architecture notes
  notebooks/            Research notebooks
  reports/              Research writeup and generated figures
  src/                  Python package
  tests/                Python tests
  benchmarks/           Benchmark notes and generated results
```

## Development Rule

Implementation is gated phase by phase. New coding phases should start only after explicit approval.
