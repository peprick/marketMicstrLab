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
    -> C++ deterministic replay
    -> book snapshots and replay metrics
    -> Python feature and label generation
    -> model validation and execution simulation
    -> reports, charts, and benchmark tables
```

## C++ Responsibilities

- Maintain bid and ask books from snapshots and incremental updates.
- Preserve deterministic replay behavior.
- Track replay throughput and latency-sensitive operations.
- Expose outputs that Python can consume through files or a later binding layer.

## Python Responsibilities

- Capture and normalize data.
- Generate features and labels.
- Train baseline models.
- Run walk-forward validation.
- Produce charts and tables for the writeup.

## Validation Principles

- Separate train, validation, and test periods by time.
- Avoid leakage from future book states.
- Report simple baselines before complex models.
- Include costs, latency, and conservative execution assumptions.
