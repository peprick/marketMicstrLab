# Project Spec

## Project Name

Market Microstructure Lab

## Folder Name

`marketMicstrLab`

## Objective

Build a serious portfolio project that demonstrates quantitative research judgment and systems engineering ability through order-book data, predictive microstructure features, realistic execution assumptions, tests, and benchmarks.

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
- Deterministic C++ order-book replay.
- Unit tests for book updates and edge cases.
- Benchmark report for replay throughput and latency distribution.
- Python research notebook or script producing clean charts.
- Honest validation with baselines, costs, and negative results included.
- A 6-10 page research writeup that explains assumptions and limitations.
