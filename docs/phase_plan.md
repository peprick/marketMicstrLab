# Phase Plan

## Phase 1: Scaffold

Status: complete

Deliverables:

- Project folder and repository structure.
- README and design notes.
- Minimal C++ build target and smoke test.
- Minimal Python package and smoke test.

## Phase 2: Data Schema and Capture

Status: complete

Deliverables:

- Raw JSONL capture format. Done.
- Normalized event schema. Done.
- Offline normalization pipeline and CLI. Done.
- Bounded Kraken WebSocket capture CLI. Done.
- End-to-end capture-to-dataset CLI. Done.
- Small local sample data capture. Done.
- Kraken checksum validation. Done.
- Data integrity notes. Done in schema docs.

## Phase 3: C++ Order-Book Replay

Status: partially complete

Deliverables:

- Snapshot apply logic. Done.
- Incremental update apply logic. Done.
- Top-of-book and depth queries. Done.
- Deterministic replay benchmark. Done.
- Unit tests for core book behavior. Done.

Remaining: full C++ JSONL replay over normalized exchange files.

## Phase 4: Research Pipeline

Status: complete

Deliverables:

- Feature generation. Done for book-derived features.
- Label generation. Done for future mid-price direction.
- Dataset builder CLI. Done.
- Baseline models. Done for simple imbalance threshold rule.
- Walk-forward validation. Done.
- Charts. Done.

## Phase 5: Execution Simulator

Status: partially complete

Deliverables:

- Fee model. Done.
- Latency delay model. Not started.
- Slippage assumptions. Done.
- Queue-position approximation. Not started.
- PnL and risk attribution. Done.

## Phase 6: Portfolio Finish

Status: partially complete

Deliverables:

- Benchmarks. Done for C++ synthetic replay.
- Research writeup. Done as Markdown.
- Final README polish. Done.
- Reproducibility instructions. Done for local workflow.
