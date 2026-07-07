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
    -> market_micstr_lab.cli.run_baseline
    -> market_micstr_lab.cli.run_walk_forward
    -> market_micstr_lab.cli.run_execution
    -> market_micstr_lab.cli.plot_research
    -> market_micstr_lab.cli.build_report_site
```

The same implemented path is also available as one orchestrated command through
`market_micstr_lab.cli.capture_dataset`.

## C++ Responsibilities

- Maintain bid and ask books from snapshots and incremental updates.
- Preserve deterministic replay behavior.
- Replay normalized JSONL book events through the same core book logic.
- Track replay throughput and latency-sensitive operations.
- Report latency percentiles across repeated synthetic benchmark runs.
- Expose outputs that Python can consume through files or a later binding layer.

The current C++ implementation covers the order-book update path, normalized JSONL replay, and a synthetic replay benchmark. It intentionally uses a narrow parser for the internal normalized JSONL contract rather than a general JSON engine.

## Python Responsibilities

- Normalize raw data into internal events.
- Capture bounded raw Kraken WebSocket data.
- Maintain a reference order book for replay correctness.
- Validate book state.
- Validate Kraken book checksums when exchange checksums are present.
- Generate feature rows after book events.
- Add future mid-price labels.
- Build labeled JSONL datasets from the command line.
- Run capture-to-dataset orchestration from the command line.
- Run simple baseline research reports from labeled feature rows.
- Run walk-forward validation.
- Run cost-aware execution simulation.
- Model event latency and partial queue fill in execution simulation.
- Produce dependency-free SVG research charts.
- Build a static local report UI from generated JSON reports and figures.
- Later: capture larger live samples, add richer predictive models, and compare against stronger baselines.

## Validation Principles

- Separate train, validation, and test periods by time.
- Avoid leakage from future book states.
- Report simple baselines before complex models.
- Include costs, latency, and conservative execution assumptions.
- Keep generated reports and UI traceable to local commands.
