# Architecture

## Layers

1. Data capture and normalization
2. C++ order-book replay core
3. Feature extraction and labeling
4. Predictive research and validation
5. Execution simulation
6. Reporting and benchmarks

## Data Flow

```text
Exchange WebSocket
    -> raw JSONL capture
    -> normalized event files
    -> Python reference replay
    -> feature rows
    -> labeled feature rows
    -> model validation and execution simulation
    -> reports, charts, and benchmark tables
```

Current implemented path:

```text
market_micstr_lab.cli.capture_kraken
    -> raw JSONL
    -> market_micstr_lab.cli.normalize
    -> processed book events JSONL
    -> market_micstr_lab.cli.build_dataset
    -> labeled feature rows JSONL
```

The same implemented path is also available as one orchestrated command through
`market_micstr_lab.cli.capture_dataset`.

## C++ Responsibilities

- Maintain bid and ask books from snapshots and incremental updates.
- Preserve deterministic replay behavior.
- Track replay throughput and latency-sensitive operations.
- Expose outputs that Python can consume through files or a later binding layer.

The C++ implementation has not started yet beyond the build scaffold.

## Python Responsibilities

- Normalize raw data into internal events.
- Capture bounded raw Kraken WebSocket data.
- Maintain a reference order book for replay correctness.
- Validate book state.
- Generate feature rows after book events.
- Add future mid-price labels.
- Build labeled JSONL datasets from the command line.
- Run capture-to-dataset orchestration from the command line.
- Later: capture live data, train baseline models, run walk-forward validation, and produce charts.

## Validation Principles

- Separate train, validation, and test periods by time.
- Avoid leakage from future book states.
- Report simple baselines before complex models.
- Include costs, latency, and conservative execution assumptions.
