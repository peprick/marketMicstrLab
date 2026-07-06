# Phase Plan

## Phase 1: Scaffold

Status: complete

Deliverables:

- Project folder and repository structure.
- README and design notes.
- Minimal C++ build target and smoke test.
- Minimal Python package and smoke test.

## Phase 2: Data Schema and Capture

Status: partially complete

Deliverables:

- Raw JSONL capture format. Done.
- Normalized event schema. Done.
- Offline normalization pipeline and CLI. Done.
- Bounded Kraken WebSocket capture CLI. Done.
- End-to-end capture-to-dataset CLI. Done.
- Small committed sample data capture. Not started.
- Kraken checksum validation. Done.
- Data integrity notes. Started in schema docs.

## Phase 3: C++ Order-Book Replay

Status: not started

Deliverables:

- Snapshot apply logic.
- Incremental update apply logic.
- Top-of-book and depth queries.
- Deterministic replay CLI.
- Unit tests for core book behavior.

Note: a Python reference order book now exists and should guide the future C++ version.

## Phase 4: Research Pipeline

Status: partially complete

Deliverables:

- Feature generation. Done for book-derived features.
- Label generation. Done for future mid-price direction.
- Dataset builder CLI. Done.
- Baseline models. Started with simple imbalance threshold rule.
- Walk-forward validation. Not started.
- Charts. Not started.

## Phase 5: Execution Simulator

Status: not started

Deliverables:

- Fee model.
- Latency delay model.
- Slippage assumptions.
- Queue-position approximation.
- PnL and risk attribution.

## Phase 6: Portfolio Finish

Status: not started

Deliverables:

- Benchmarks.
- Research writeup.
- Final README polish.
- Reproducibility instructions.
