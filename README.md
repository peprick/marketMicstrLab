# Market Microstructure Lab

Market Microstructure Lab is a quant research and engineering project focused on
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
- Simple imbalance-threshold baseline with chronological train/test evaluation.
- Walk-forward validation for baseline stability checks.
- Dependency-free SVG research charts.
- Cost-aware execution simulation with spread, fees, and slippage.
- C++ order-book core with replay benchmark tooling.

No live trading, broker integration, or production HFT claim is included.

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
8. Build baseline predictive models and robust validation. Done for imbalance threshold baseline and walk-forward validation.
9. Port critical replay/simulation logic to C++. Done for the order-book update path.
10. Add execution simulator with fees, slippage, latency, and queue assumptions. Done for spread, fee, and slippage assumptions.
11. Produce charts, benchmarks, tests, and a 6-10 page research writeup. Done as local report artifacts.

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

Run the first baseline research report:

```bash
python -m market_micstr_lab.cli.run_baseline \
  --input data/processed/labeled_features.jsonl \
  --output reports/baseline_imbalance.json \
  --depth 1 \
  --horizon 10 \
  --train-fraction 0.7 \
  --thresholds 0,0.05,0.10,0.20,0.30,0.50
```

Run walk-forward validation:

```bash
python -m market_micstr_lab.cli.run_walk_forward \
  --input data/processed/labeled_features.jsonl \
  --output reports/walk_forward_imbalance.json \
  --depth 1 \
  --horizon 10 \
  --train-size 40 \
  --test-size 15 \
  --step-size 15
```

Run cost-aware execution simulation:

```bash
python -m market_micstr_lab.cli.run_execution \
  --input data/processed/labeled_features.jsonl \
  --output reports/execution_imbalance.json \
  --depth 1 \
  --horizon 10 \
  --threshold 0.20 \
  --fee-bps 2 \
  --slippage-bps 1
```

Write research charts:

```bash
python -m market_micstr_lab.cli.plot_research \
  --dataset data/processed/labeled_features.jsonl \
  --baseline reports/baseline_imbalance.json \
  --output-dir reports/figures \
  --imbalance-depth 1
```

Run the C++ replay benchmark:

```bash
./build/mml_replay_benchmark --events 100000 --depth 10
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
