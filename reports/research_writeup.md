# Market Microstructure Lab Research Writeup

## 1. Objective

This project studies whether short-horizon order-book imbalance, spread, depth, and related microstructure features can predict future mid-price movement after accounting for realistic market frictions.

The implementation is intentionally split into:

- Python research tooling for capture, normalization, features, labels, validation, charts, and reports.
- C++ critical-path tooling for deterministic order-book updates and replay benchmarks.

The first instrument is BTC/USD from Kraken's public WebSocket v2 feed.

## 2. Data

The current local sample contains:

- 100 raw Kraken WebSocket messages.
- 96 normalized book events.
- 96 labeled feature rows.

The sample is deliberately small and should be treated as an integration smoke sample, not a statistically meaningful research dataset.

Raw captures are stored as local JSONL envelopes with local receive timestamps and the original exchange payload. The normalized schema extracts book snapshots and updates into a consistent internal format.

## 3. Feature and Label Design

The Python reference replay applies every normalized book event and emits one feature row per event.

Implemented features include:

- Best bid and ask.
- Spread.
- Mid-price.
- Microprice.
- Bid and ask depth.
- Order-book imbalance at configurable depth.
- Book validity flag.

Labels are future mid-price direction labels at a configurable event horizon:

- `1` for future mid-price increase.
- `-1` for future mid-price decrease.
- `0` for no move beyond the configured threshold.

## 4. Validation

The project avoids random row shuffling. All validation paths preserve chronological order.

Implemented validation modes:

- Single chronological train/test split for the first imbalance baseline.
- Walk-forward validation over rolling chronological windows.
- Kraken book checksum validation when exchange checksums are present.
- Cost-aware execution simulation after signal generation.

## 5. Baseline Model

The first baseline is intentionally simple:

```text
if imbalance > threshold: predict up
if imbalance < -threshold: predict down
otherwise: predict flat
```

Thresholds are selected on the training segment and evaluated on future rows.

On the current tiny local sample:

- Best threshold: `0`
- Test rows: 26
- Test accuracy: 0.0

This result is not evidence against the idea; the sample is too small and mostly flat over the chosen horizon. It is useful because the pipeline correctly reports a negative result instead of hiding it.

## 6. Walk-Forward Result

The walk-forward report uses:

- Train size: 40 rows.
- Test size: 15 rows.
- Step size: 15 rows.
- Window count: 3.

On the current local sample:

- Mean test accuracy: 0.0
- Minimum test accuracy: 0.0
- Maximum test accuracy: 0.0

The result reinforces that this tiny smoke dataset should not be used to claim predictive edge.

## 7. Execution Simulation

The execution simulation applies spread, fees, and slippage to the imbalance signal.

Current local run:

- Horizon: 10 events.
- Threshold: 0.20.
- Fees: 2 bps.
- Slippage: 1 bps.
- Trades: 86.
- Gross PnL: 0.00.
- Total cost: 3240.062900.
- Net PnL: -3240.062900.
- Win rate: 0.0.

This is the most important sanity check in the project so far: a signal that looks active can still be worthless once realistic friction is applied.

## 8. C++ Replay Benchmark

The C++ order book supports:

- Snapshot application.
- Incremental bid/ask updates.
- Top-of-book queries.
- Depth queries.
- Spread and mid-price.
- Basic book validation.

Local synthetic replay benchmark:

- Events: 100,000.
- Depth: 10 levels per side.
- Throughput: about 34 million updates per second.
- Average update time: about 29 ns per event.

This benchmark isolates the order-book update path. It does not include JSON parsing, file I/O, Python overhead, or exchange networking.

## 9. Limitations

Current limitations are substantial and intentionally documented:

- The current data sample is tiny.
- The baseline uses only imbalance and ignores many useful microstructure features.
- The execution simulator uses a simplified spread/fee/slippage model.
- Queue position is not yet modeled.
- No production trading, broker integration, or live execution is attempted.
- C++ benchmark uses synthetic updates, not full exchange JSONL replay.

## 10. Next Improvements

High-value next steps:

- Capture larger samples across multiple market regimes.
- Add event-intensity and short-term volatility features.
- Add queue-position approximation.
- Add latency-delay simulation.
- Add richer walk-forward reports and stability plots.
- Extend C++ tooling toward end-to-end JSONL replay.

## 11. Conclusion

The project now has the core shape of a credible quant engineering portfolio piece:

- Real exchange data capture.
- Normalization and schema boundaries.
- Python reference replay.
- Feature and label generation.
- Baseline prediction.
- Walk-forward validation.
- Cost-aware execution simulation.
- C++ order-book core and benchmark.
- Honest reporting of negative results.

The current result should be interpreted as a working research harness, not a profitable strategy. That honesty is the point.
