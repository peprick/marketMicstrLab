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

Status: complete

Deliverables:

- Snapshot apply logic. Done.
- Incremental update apply logic. Done.
- Top-of-book and depth queries. Done.
- Normalized JSONL replay. Done.
- Deterministic replay benchmark. Done.
- Repeated-run benchmark latency percentiles. Done.
- Unit tests for core book behavior. Done.

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

Status: complete

Deliverables:

- Fee model. Done.
- Latency delay model. Done.
- Slippage assumptions. Done.
- Queue-position approximation. Done as configurable fill fraction.
- PnL and risk attribution. Done.

## Phase 6: Portfolio Finish

Status: complete

Deliverables:

- Benchmarks. Done for C++ synthetic replay.
- Research writeup. Done as Markdown.
- Static local report UI. Done.
- Final README polish. Done.
- Reproducibility instructions. Done for local workflow.

## Optional Extensions

- Larger live captures across multiple market regimes.
- Stronger predictive baselines such as logistic regression or gradient boosting.
- Python-to-C++ binding layer for in-process replay.
- More realistic queue modeling from order-book update sizes and trade prints.
- A published read-only version of the static report UI.
