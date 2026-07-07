import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from market_micstr_lab.data.jsonl import read_jsonl
from market_micstr_lab.research.baseline import predict_from_imbalance


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _json_decimal(value: Decimal) -> str:
    return format(value, "f")


def execution_cost(
    mid_price: Any,
    spread: Any,
    fee_bps: Decimal = Decimal("0"),
    slippage_bps: Decimal = Decimal("0"),
) -> Decimal:
    mid = _to_decimal(mid_price)
    spread_value = _to_decimal(spread)

    if mid is None:
        raise ValueError("mid_price is required")
    if spread_value is None:
        raise ValueError("spread is required")
    if fee_bps < 0:
        raise ValueError("fee_bps must be non-negative")
    if slippage_bps < 0:
        raise ValueError("slippage_bps must be non-negative")

    round_trip_fee = mid * (fee_bps / Decimal("10000")) * Decimal("2")
    round_trip_slippage = mid * (slippage_bps / Decimal("10000")) * Decimal("2")

    return spread_value + round_trip_fee + round_trip_slippage


def simulate_row_execution(
    row: dict,
    depth: int = 1,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
    fee_bps: Decimal = Decimal("0"),
    slippage_bps: Decimal = Decimal("0"),
) -> dict | None:
    imbalance_key = f"imbalance_{depth}"
    delta_key = f"mid_price_delta_{horizon}"

    if row.get(imbalance_key) is None or row.get(delta_key) is None:
        return None

    signal = predict_from_imbalance(row[imbalance_key], threshold=threshold)
    if signal == 0:
        gross_pnl = Decimal("0")
        cost = Decimal("0")
        net_pnl = Decimal("0")
    else:
        delta = _to_decimal(row[delta_key])
        if delta is None:
            return None

        gross_pnl = Decimal(signal) * delta
        cost = execution_cost(
            row.get("mid_price"),
            row.get("spread"),
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
        )
        net_pnl = gross_pnl - cost

    return {
        "recv_seq": row.get("recv_seq"),
        "signal_recv_seq": row.get("recv_seq"),
        "entry_recv_seq": row.get("recv_seq"),
        "exit_recv_seq": row.get("recv_seq"),
        "signal": signal,
        "latency_events": 0,
        "queue_fill_fraction": "1",
        "gross_pnl": _json_decimal(gross_pnl),
        "cost": _json_decimal(cost),
        "net_pnl": _json_decimal(net_pnl),
    }


def simulate_delayed_row_execution(
    rows: list[dict],
    signal_index: int,
    depth: int = 1,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
    fee_bps: Decimal = Decimal("0"),
    slippage_bps: Decimal = Decimal("0"),
    latency_events: int = 0,
    queue_fill_fraction: Decimal = Decimal("1"),
) -> dict | None:
    if latency_events < 0:
        raise ValueError("latency_events must be non-negative")
    if not Decimal("0") <= queue_fill_fraction <= Decimal("1"):
        raise ValueError("queue_fill_fraction must be between 0 and 1")

    imbalance_key = f"imbalance_{depth}"
    signal_row = rows[signal_index]
    if signal_row.get(imbalance_key) is None:
        return None

    entry_index = signal_index + latency_events
    exit_index = entry_index + horizon
    if exit_index >= len(rows):
        return None

    entry_row = rows[entry_index]
    exit_row = rows[exit_index]
    signal = predict_from_imbalance(signal_row[imbalance_key], threshold=threshold)

    if signal == 0 or queue_fill_fraction == 0:
        gross_pnl = Decimal("0")
        cost = Decimal("0")
        net_pnl = Decimal("0")
    else:
        entry_mid = _to_decimal(entry_row.get("mid_price"))
        exit_mid = _to_decimal(exit_row.get("mid_price"))
        if entry_mid is None or exit_mid is None:
            return None

        gross_pnl = Decimal(signal) * (exit_mid - entry_mid) * queue_fill_fraction
        cost = execution_cost(
            entry_row.get("mid_price"),
            entry_row.get("spread"),
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
        ) * queue_fill_fraction
        net_pnl = gross_pnl - cost

    return {
        "recv_seq": signal_row.get("recv_seq"),
        "signal_recv_seq": signal_row.get("recv_seq"),
        "entry_recv_seq": entry_row.get("recv_seq"),
        "exit_recv_seq": exit_row.get("recv_seq"),
        "signal": signal,
        "latency_events": latency_events,
        "queue_fill_fraction": _json_decimal(queue_fill_fraction),
        "gross_pnl": _json_decimal(gross_pnl),
        "cost": _json_decimal(cost),
        "net_pnl": _json_decimal(net_pnl),
    }


def simulate_execution_rows(
    rows: list[dict],
    depth: int = 1,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
    fee_bps: Decimal = Decimal("0"),
    slippage_bps: Decimal = Decimal("0"),
    latency_events: int = 0,
    queue_fill_fraction: Decimal = Decimal("1"),
) -> list[dict]:
    results = []

    if latency_events < 0:
        raise ValueError("latency_events must be non-negative")
    if not Decimal("0") <= queue_fill_fraction <= Decimal("1"):
        raise ValueError("queue_fill_fraction must be between 0 and 1")

    for index, row in enumerate(rows):
        if latency_events == 0 and queue_fill_fraction == 1:
            result = simulate_row_execution(
                row,
                depth=depth,
                horizon=horizon,
                threshold=threshold,
                fee_bps=fee_bps,
                slippage_bps=slippage_bps,
            )
        else:
            result = simulate_delayed_row_execution(
                rows,
                signal_index=index,
                depth=depth,
                horizon=horizon,
                threshold=threshold,
                fee_bps=fee_bps,
                slippage_bps=slippage_bps,
                latency_events=latency_events,
                queue_fill_fraction=queue_fill_fraction,
            )

        if result is not None:
            results.append(result)

    return results


def summarize_execution(results: list[dict]) -> dict:
    total_gross = sum((_to_decimal(row["gross_pnl"]) for row in results), Decimal("0"))
    total_cost = sum((_to_decimal(row["cost"]) for row in results), Decimal("0"))
    total_net = sum((_to_decimal(row["net_pnl"]) for row in results), Decimal("0"))
    trades = [row for row in results if row["signal"] != 0]
    winning_trades = [
        row
        for row in trades
        if _to_decimal(row["net_pnl"]) is not None and _to_decimal(row["net_pnl"]) > 0
    ]

    trade_count = len(trades)
    win_rate = len(winning_trades) / trade_count if trade_count else None
    average_net_pnl = total_net / Decimal(str(trade_count)) if trade_count else None

    return {
        "evaluated_rows": len(results),
        "trade_count": trade_count,
        "win_rate": win_rate,
        "total_gross_pnl": _json_decimal(total_gross),
        "total_cost": _json_decimal(total_cost),
        "total_net_pnl": _json_decimal(total_net),
        "average_net_pnl_per_trade": _json_decimal(average_net_pnl) if average_net_pnl is not None else None,
    }


def run_execution_simulation(
    rows: list[dict],
    depth: int = 1,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
    fee_bps: Decimal = Decimal("0"),
    slippage_bps: Decimal = Decimal("0"),
    latency_events: int = 0,
    queue_fill_fraction: Decimal = Decimal("1"),
) -> dict:
    results = simulate_execution_rows(
        rows,
        depth=depth,
        horizon=horizon,
        threshold=threshold,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        latency_events=latency_events,
        queue_fill_fraction=queue_fill_fraction,
    )

    return {
        "model": "imbalance_threshold_execution",
        "feature": f"imbalance_{depth}",
        "horizon": horizon,
        "threshold": str(threshold),
        "fee_bps": str(fee_bps),
        "slippage_bps": str(slippage_bps),
        "latency_events": latency_events,
        "queue_fill_fraction": str(queue_fill_fraction),
        "summary": summarize_execution(results),
        "rows": results,
    }


def write_execution_report_json(
    input_path: str | Path,
    output_path: str | Path,
    depth: int = 1,
    horizon: int = 1,
    threshold: Decimal = Decimal("0"),
    fee_bps: Decimal = Decimal("0"),
    slippage_bps: Decimal = Decimal("0"),
    latency_events: int = 0,
    queue_fill_fraction: Decimal = Decimal("1"),
) -> dict:
    report = run_execution_simulation(
        list(read_jsonl(input_path)),
        depth=depth,
        horizon=horizon,
        threshold=threshold,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        latency_events=latency_events,
        queue_fill_fraction=queue_fill_fraction,
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, sort_keys=True)
        file.write("\n")

    return report
