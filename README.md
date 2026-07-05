# Market Microstructure Lab

Market Microstructure Lab is a flagship quant research and engineering project focused on
order-book dynamics, short-horizon price movement, and realistic execution assumptions.

The project is intentionally split into two halves:

- Python research layer: data capture, cleaning, feature engineering, labeling, modeling, and charts.
- C++ critical path: order-book replay, deterministic simulation, execution assumptions, tests, and benchmarks.

## Current Status

The Python research skeleton is in place and tested:

- Raw/processed JSONL utilities.
- Kraken-style book/trade message normalization.
- Offline normalization CLI.
- Python reference order-book replay with validation.
- Book feature extraction: spread, mid-price, microprice, depth, and imbalance.
- Future mid-price labeling.
- Dataset builder CLI for labeled feature rows.
- Kraken WebSocket raw capture CLI with bounded capture by message count or time.
- End-to-end capture-to-dataset CLI for reproducible pipeline runs.
- Kraken book checksum validation during replay/dataset construction.

No predictive model, execution simulator, or C++ order-book implementation has been implemented yet.

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

1. Define event schema and research assumptions. Done.
2. Normalize order-book snapshots and updates. Done for offline JSONL.
3. Build Python reference order-book replay. Done.
4. Add feature extraction and labeling in Python. Done.
5. Add command-line dataset builder. Done.
6. Capture bounded raw Kraken book/trade data. Done at the CLI layer.
7. Add raw-to-processed-to-dataset command workflow. Done.
8. Build baseline predictive models and robust validation.
9. Port critical replay/simulation logic to C++.
10. Add execution simulator with fees, slippage, latency, and queue assumptions.
11. Produce charts, benchmarks, tests, and a 6-10 page research writeup.

## Quickstart

Create and activate a Python 3.11 virtual environment, then install the package in editable mode:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e . pytest
```

Run the Python test suite:

```bash
pytest tests
```

Build and test the C++ scaffold:

```bash
cmake -S . -B build -G Ninja
cmake --build build
ctest --test-dir build --output-on-failure
```

## Command-Line Tools

Normalize raw exchange JSONL into internal event JSONL:

```bash
python -m market_micstr_lab.cli.normalize \
  --input data/raw/sample_book.jsonl \
  --output data/processed/book_events.jsonl \
  --channel book
```

Capture bounded raw Kraken messages:

```bash
python -m market_micstr_lab.cli.capture_kraken \
  --output data/raw/kraken_btcusd_book.jsonl \
  --channel book \
  --symbol BTC/USD \
  --depth 10 \
  --max-messages 100
```

Build labeled feature rows from processed book events:

```bash
python -m market_micstr_lab.cli.build_dataset \
  --input data/processed/book_events.jsonl \
  --output data/processed/labeled_features.jsonl \
  --depth 1 \
  --horizon 10 \
  --validate
```

Run the full live-data pipeline in one command:

```bash
python -m market_micstr_lab.cli.capture_dataset \
  --raw-output data/raw/kraken_btcusd_book.jsonl \
  --events-output data/processed/book_events.jsonl \
  --dataset-output data/processed/labeled_features.jsonl \
  --symbol BTC/USD \
  --depth 10 \
  --feature-depth 1 \
  --max-messages 100 \
  --horizon 10 \
  --validate-checksum \
  --validate
```

Note: `data/raw/` and `data/processed/` are local working directories and are ignored by git.

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
