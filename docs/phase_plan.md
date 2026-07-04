# Phase Plan

## Phase 1: Scaffold

Status: started

Deliverables:

- Project folder and repository structure.
- README and design notes.
- Minimal C++ build target and smoke test.
- Minimal Python package and smoke test.

## Phase 2: Data Schema and Capture

Requires explicit approval before implementation.

Deliverables:

- Raw JSONL capture format.
- Normalized event schema.
- Small sample data capture.
- Data integrity notes.

## Phase 3: C++ Order-Book Replay

Requires explicit approval before implementation.

Deliverables:

- Snapshot apply logic.
- Incremental update apply logic.
- Top-of-book and depth queries.
- Deterministic replay CLI.
- Unit tests for core book behavior.

## Phase 4: Research Pipeline

Requires explicit approval before implementation.

Deliverables:

- Feature generation.
- Label generation.
- Baseline models.
- Walk-forward validation.
- Charts.

## Phase 5: Execution Simulator

Requires explicit approval before implementation.

Deliverables:

- Fee model.
- Latency delay model.
- Slippage assumptions.
- Queue-position approximation.
- PnL and risk attribution.

## Phase 6: Portfolio Finish

Requires explicit approval before implementation.

Deliverables:

- Benchmarks.
- Research writeup.
- Final README polish.
- Reproducibility instructions.
