import json
from html import escape
from pathlib import Path
from typing import Any

from market_micstr_lab.data.jsonl import read_jsonl


def load_labeled_rows(path: str | Path) -> list[dict]:
    return list(read_jsonl(path))


def series_from_rows(rows: list[dict], key: str) -> list[float]:
    values = []

    for row in rows:
        value = row.get(key)
        if value is None:
            continue
        values.append(float(value))

    return values


def _scale(value: float, source_min: float, source_max: float, target_min: float, target_max: float) -> float:
    if source_max == source_min:
        return (target_min + target_max) / 2

    ratio = (value - source_min) / (source_max - source_min)
    return target_min + ratio * (target_max - target_min)


def write_line_svg(values: list[float], output_path: str | Path, title: str, y_label: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    width = 900
    height = 420
    left = 70
    right = 30
    top = 50
    bottom = 55
    plot_width = width - left - right
    plot_height = height - top - bottom

    if values:
        y_min = min(values)
        y_max = max(values)
        if y_min == y_max:
            y_min -= 1
            y_max += 1

        points = []
        for index, value in enumerate(values):
            x = left if len(values) == 1 else left + (index / (len(values) - 1)) * plot_width
            y = _scale(value, y_min, y_max, top + plot_height, top)
            points.append(f"{x:.2f},{y:.2f}")

        polyline = (
            f'<polyline points="{" ".join(points)}" fill="none" '
            f'stroke="#2563eb" stroke-width="2.5" />'
        )
    else:
        y_min = 0
        y_max = 0
        polyline = ""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff" />
  <text x="{width / 2}" y="28" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">{escape(title)}</text>
  <text x="18" y="{height / 2}" text-anchor="middle" font-family="Arial" font-size="13" transform="rotate(-90 18 {height / 2})">{escape(y_label)}</text>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#111827" stroke-width="1.5" />
  <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#111827" stroke-width="1.5" />
  <text x="{left}" y="{top + plot_height + 32}" text-anchor="middle" font-family="Arial" font-size="12">0</text>
  <text x="{left + plot_width}" y="{top + plot_height + 32}" text-anchor="middle" font-family="Arial" font-size="12">{max(len(values) - 1, 0)}</text>
  <text x="{left - 8}" y="{top + 4}" text-anchor="end" font-family="Arial" font-size="12">{y_max:.6g}</text>
  <text x="{left - 8}" y="{top + plot_height}" text-anchor="end" font-family="Arial" font-size="12">{y_min:.6g}</text>
  {polyline}
</svg>
"""

    path.write_text(svg, encoding="utf-8")


def write_bar_svg(labels: list[str], values: list[float], output_path: str | Path, title: str, y_label: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    width = 720
    height = 420
    left = 70
    right = 30
    top = 50
    bottom = 65
    plot_width = width - left - right
    plot_height = height - top - bottom

    max_value = max(values) if values else 1
    if max_value <= 0:
        max_value = 1

    bars = []
    if values:
        slot_width = plot_width / len(values)
        bar_width = slot_width * 0.55

        for index, (label, value) in enumerate(zip(labels, values)):
            bar_height = (value / max_value) * plot_height
            x = left + index * slot_width + (slot_width - bar_width) / 2
            y = top + plot_height - bar_height

            bars.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" fill="#16a34a" />'
            )
            bars.append(
                f'<text x="{x + bar_width / 2:.2f}" y="{top + plot_height + 24}" text-anchor="middle" font-family="Arial" font-size="12">{escape(label)}</text>'
            )
            bars.append(
                f'<text x="{x + bar_width / 2:.2f}" y="{y - 6:.2f}" text-anchor="middle" font-family="Arial" font-size="12">{value:.4g}</text>'
            )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff" />
  <text x="{width / 2}" y="28" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">{escape(title)}</text>
  <text x="18" y="{height / 2}" text-anchor="middle" font-family="Arial" font-size="13" transform="rotate(-90 18 {height / 2})">{escape(y_label)}</text>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#111827" stroke-width="1.5" />
  <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#111827" stroke-width="1.5" />
  <text x="{left - 8}" y="{top + 4}" text-anchor="end" font-family="Arial" font-size="12">{max_value:.4g}</text>
  <text x="{left - 8}" y="{top + plot_height}" text-anchor="end" font-family="Arial" font-size="12">0</text>
  {"".join(bars)}
</svg>
"""

    path.write_text(svg, encoding="utf-8")


def _accuracy(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def write_research_charts(
    dataset_path: str | Path,
    baseline_path: str | Path,
    output_dir: str | Path,
    imbalance_depth: int = 1,
) -> dict[str, str]:
    rows = load_labeled_rows(dataset_path)
    output = Path(output_dir)

    with Path(baseline_path).open("r", encoding="utf-8") as file:
        baseline = json.load(file)

    paths = {
        "mid_price": output / "mid_price.svg",
        "spread": output / "spread.svg",
        "imbalance": output / f"imbalance_{imbalance_depth}.svg",
        "baseline_accuracy": output / "baseline_accuracy.svg",
    }

    write_line_svg(
        series_from_rows(rows, "mid_price"),
        paths["mid_price"],
        title="Mid Price",
        y_label="price",
    )
    write_line_svg(
        series_from_rows(rows, "spread"),
        paths["spread"],
        title="Spread",
        y_label="price",
    )
    write_line_svg(
        series_from_rows(rows, f"imbalance_{imbalance_depth}"),
        paths["imbalance"],
        title=f"Order Book Imbalance Depth {imbalance_depth}",
        y_label="imbalance",
    )
    write_bar_svg(
        ["train", "test"],
        [
            _accuracy(baseline.get("train", {}).get("accuracy")),
            _accuracy(baseline.get("test", {}).get("accuracy")),
        ],
        paths["baseline_accuracy"],
        title="Baseline Accuracy",
        y_label="accuracy",
    )

    return {key: str(value) for key, value in paths.items()}
