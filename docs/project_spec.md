# Project Spec

## Project Name

Market Microstructure Lab

## Folder Name

`marketMicstrLab`

## Objective

Build a reproducible market-microstructure research system that combines order-book data, predictive microstructure features, realistic execution assumptions, tests, and benchmarks.

## Research Question

Can short-horizon order-book imbalance, spread, depth, and event-intensity features predict mid-price movement after accounting for realistic fees, latency, and execution assumptions?

## First Instrument

BTC/USD on Kraken.

## First Data Mode

L2 order-book snapshots and incremental updates from a public WebSocket feed.

## Initial Non-Goals

- No live trading.
- No broker integration.
- No claimed production HFT system.
- No high-Sharpe claims without robust validation.
- No paid data dependency in V1.

## Success Criteria

- Reproducible data sample and normalized event schema.
- Python reference order-book replay with validation.
- Deterministic C++ order-book replay.
- Unit tests for book updates, edge cases, feature generation, labels, and CLI entry points.
- Benchmark report for replay throughput and latency distribution.
- Python research notebook or script producing clean charts.
- Honest validation with baselines, costs, and limitations included.
- Static local UI that summarizes reports, charts, and assumptions.
- A 6-10 page research writeup that explains assumptions and limitations.

## Implemented So Far

- Project scaffold with Python package and C++ build skeleton.
- Raw JSONL and processed JSONL helpers.
- Kraken-style book/trade normalization.
- Offline normalization CLI.
- Python order-book replay and validation.
- Book-derived feature generation.
- Future mid-price direction labels.
- Dataset builder CLI.
- Bounded Kraken WebSocket raw capture CLI.
- End-to-end capture-to-dataset CLI.
- Kraken book checksum validation.
- Simple imbalance-threshold baseline report.
- Walk-forward validation report.
- SVG chart generation.
- Cost-aware execution simulation with latency and queue-fill assumptions.
- C++ order-book core, normalized JSONL replay, and synthetic replay benchmark percentiles.
- Static local report UI.
- Research writeup and benchmark notes.

## Optional Next Steps

- Capture larger market-data samples.
- Add stronger predictive models.
- Add more realistic queue modeling from trades and book update flow.
- Add a published read-only report UI for reproducible research runs.
