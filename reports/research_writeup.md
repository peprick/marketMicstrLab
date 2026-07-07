# Market Microstructure Lab Research Note

## 1. Objective

Market Microstructure Lab studies whether short-horizon order-book features can explain or predict future mid-price movement after accounting for market frictions.

The project separates research tooling from latency-sensitive replay logic:

- Python handles capture, normalization, reference replay, feature generation, labeling, validation, charts, execution reports, and static report generation.
- C++ handles deterministic order-book updates, normalized JSONL replay, and replay benchmarks.

The first supported public data source is Kraken WebSocket v2 order-book data. The code is structured so additional venues or instruments can be added behind the same normalized event schema.

## 2. Data Contract

Raw exchange messages are stored as JSONL envelopes with local receive metadata. Processed files use normalized JSONL book events with explicit schema version, source, channel, event type, symbol, receive sequence, book depth, bids, asks, and optional exchange checksum.

Local market-data captures are intentionally excluded from git. Reproducible examples should be regenerated from the command-line tools or stored as tiny deterministic fixtures under `tests/fixtures/`.

## 3. Feature and Label Design

The Python reference replay applies normalized book events in receive order and emits one feature row after each valid book update.

Implemented book features include:

- Best bid and ask.
- Spread.
- Mid-price.
- Microprice.
- Bid and ask depth.
- Order-book imbalance at configurable depth.
- One-event mid-price change and return.
- One-event spread change.
- Rolling 10-event mid-price volatility.
- One-event order-flow imbalance approximation.
- Book-validity flag.

Labels are future mid-price direction labels at a configurable event horizon:

- `1` means future mid-price increased beyond the label threshold.
- `-1` means future mid-price decreased beyond the label threshold.
- `0` means the move stayed within the threshold.
- `null` means the future row is unavailable.

Features are computed only from current and past book states. Future rows are used only for labels.

## 4. Validation

Validation preserves chronological order. Random row shuffling is avoided because it can leak regime information across time.

Implemented validation modes:

- Single chronological train/test split for the imbalance-threshold baseline.
- Walk-forward validation over rolling chronological windows.
- Kraken checksum validation when exchange checksums are present.
- Execution simulation after signal generation.

The first baseline is deliberately simple:

```text
if imbalance > threshold: predict up
if imbalance < -threshold: predict down
otherwise: predict flat
```

Thresholds are selected on training rows and evaluated on future rows.

## 5. Execution Assumptions

Execution simulation applies configurable assumptions after signals are generated:

- Spread cost.
- Fee in basis points.
- Slippage in basis points.
- Event latency before entry.
- Partial queue-fill fraction.

The simulator is a research approximation, not a matching-engine reconstruction. Its purpose is to prevent raw predictive metrics from being confused with executable performance.

## 6. C++ Replay and Benchmarks

The C++ core supports:

- Snapshot application.
- Incremental bid/ask updates.
- Top-of-book queries.
- Depth queries.
- Spread and mid-price calculations.
- Basic book validation.
- Normalized JSONL replay over the internal event schema.
- Repeated-run benchmark summaries with mean, p50, p95, and p99 nanoseconds per event.

The synthetic benchmark isolates the order-book update path. The normalized JSONL replay executable validates the file-ingestion path. Neither benchmark includes exchange networking or Python overhead.

## 7. Reporting

Research commands write JSON reports under `reports/` and SVG figures under `reports/figures/`. These generated outputs are ignored by git.

The static report UI can be rebuilt from generated artifacts:

```bash
python -m market_micstr_lab.cli.build_report_site \
  --reports-dir reports \
  --output reports/site/index.html
```

The UI summarizes baseline validation, walk-forward validation, execution assumptions, charts, and compact report metadata.

## 8. Limitations

Current limitations are explicit:

- Public WebSocket data is convenient but not equivalent to paid historical market-data feeds.
- The first predictive model is a simple imbalance-threshold rule.
- Queue position is represented by a configurable fill fraction, not full queue reconstruction.
- Execution is simulated from book states and does not place live orders.
- The project does not include broker integration or live trading.

## 9. Extension Paths

Useful future directions:

- Larger captures across different volatility regimes.
- Multi-instrument and multi-venue comparisons.
- Stronger predictive baselines.
- Trade-print-aware queue modeling.
- Python-to-C++ bindings for in-process replay experiments.
- Reproducible benchmark reports with compiler, machine, and build metadata.
