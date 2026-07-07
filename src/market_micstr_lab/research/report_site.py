import json
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any


REPORT_FILES = {
    "baseline": "baseline_imbalance.json",
    "walk_forward": "walk_forward_imbalance.json",
    "execution": "execution_imbalance.json",
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _format_percent(value: Any) -> str:
    if value is None:
        return "n/a"

    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def _format_number(value: Any) -> str:
    if value is None:
        return "n/a"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return escape(str(value))

    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,.6g}"


def _display_label(text: str) -> str:
    return text.replace("_", " ").replace("-", " ").title()


def _metric(label: str, value: str, detail: str = "") -> str:
    return (
        '<article class="metric-card">'
        f'<p class="metric-label">{escape(label)}</p>'
        f'<p class="metric-value">{value}</p>'
        f'<p class="metric-detail">{escape(detail)}</p>'
        "</article>"
    )


def _report_status(name: str, report: dict[str, Any] | None) -> str:
    state = "Ready" if report is not None else "Missing"
    state_class = "ready" if report is not None else "missing"
    return (
        f'<span class="status-pill {state_class}">'
        f"{escape(_display_label(name))}: {state}</span>"
    )


def _baseline_metrics(report: dict[str, Any] | None) -> str:
    if report is None:
        return _metric("Baseline", "Missing", "Run the imbalance baseline report")

    test = report.get("test", {})
    return "".join(
        [
            _metric("Baseline Accuracy", _format_percent(test.get("accuracy")), "chronological holdout"),
            _metric("Best Threshold", escape(str(report.get("best_threshold", "n/a"))), "trained on early rows"),
            _metric("Usable Rows", _format_number(report.get("usable_rows")), "rows with feature and label"),
            _metric("Test Rows", _format_number(report.get("test_rows")), "out-of-sample rows"),
        ]
    )


def _walk_forward_metrics(report: dict[str, Any] | None) -> str:
    if report is None:
        return _metric("Walk Forward", "Missing", "Run rolling-window validation")

    return "".join(
        [
            _metric("Windows", _format_number(report.get("window_count")), "rolling train/test splits"),
            _metric("Mean Accuracy", _format_percent(report.get("mean_test_accuracy")), "average test window"),
            _metric("Min Accuracy", _format_percent(report.get("min_test_accuracy")), "worst test window"),
            _metric("Max Accuracy", _format_percent(report.get("max_test_accuracy")), "best test window"),
        ]
    )


def _execution_metrics(report: dict[str, Any] | None) -> str:
    if report is None:
        return _metric("Execution", "Missing", "Run the execution simulator")

    summary = report.get("summary", {})
    return "".join(
        [
            _metric("Trades", _format_number(summary.get("trade_count")), "non-zero signals"),
            _metric("Win Rate", _format_percent(summary.get("win_rate")), "after spread and costs"),
            _metric("Net PnL", _format_number(summary.get("total_net_pnl")), "simulated quote-currency units"),
            _metric("Latency Events", _format_number(report.get("latency_events")), "event delay before entry"),
            _metric("Queue Fill", _format_percent(report.get("queue_fill_fraction")), "filled fraction of signal size"),
        ]
    )


def _threshold_rows(report: dict[str, Any] | None) -> str:
    if report is None:
        return '<tr><td colspan="4">No baseline report found.</td></tr>'

    rows = []
    for item in report.get("threshold_search", []):
        rows.append(
            "<tr>"
            f"<td>{escape(str(item.get('threshold', 'n/a')))}</td>"
            f"<td>{_format_number(item.get('evaluated_rows'))}</td>"
            f"<td>{_format_number(item.get('correct'))}</td>"
            f"<td>{_format_percent(item.get('accuracy'))}</td>"
            "</tr>"
        )

    return "".join(rows) if rows else '<tr><td colspan="4">No threshold search rows found.</td></tr>'


def _walk_forward_rows(report: dict[str, Any] | None) -> str:
    if report is None:
        return '<tr><td colspan="5">No walk-forward report found.</td></tr>'

    rows = []
    for item in report.get("windows", [])[:12]:
        test = item.get("test", {})
        rows.append(
            "<tr>"
            f"<td>{_format_number(item.get('window'))}</td>"
            f"<td>{escape(str(item.get('best_threshold', 'n/a')))}</td>"
            f"<td>{_format_number(test.get('evaluated_rows'))}</td>"
            f"<td>{_format_number(test.get('correct'))}</td>"
            f"<td>{_format_percent(test.get('accuracy'))}</td>"
            "</tr>"
        )

    return "".join(rows) if rows else '<tr><td colspan="5">No windows were produced.</td></tr>'


def _chart_cards(figures_dir: Path) -> str:
    if not figures_dir.exists():
        return '<p class="empty-state">No SVG figures found yet.</p>'

    cards = []
    for path in sorted(figures_dir.glob("*.svg")):
        svg = path.read_text(encoding="utf-8")
        if "<svg" not in svg:
            continue
        cards.append(
            '<article class="figure-card">'
            f"<h3>{escape(_display_label(path.stem))}</h3>"
            f'<div class="svg-shell">{svg}</div>'
            "</article>"
        )

    return "".join(cards) if cards else '<p class="empty-state">No SVG figures found yet.</p>'


def _json_summary(title: str, report: dict[str, Any] | None) -> str:
    if report is None:
        body = "Report not found."
    else:
        compact = {
            key: report.get(key)
            for key in [
                "model",
                "feature",
                "label",
                "horizon",
                "best_threshold",
                "threshold",
                "fee_bps",
                "slippage_bps",
                "latency_events",
                "queue_fill_fraction",
            ]
            if key in report
        }
        body = json.dumps(compact, indent=2, sort_keys=True)

    return (
        '<article class="json-card">'
        f"<h3>{escape(title)}</h3>"
        f"<pre>{escape(body)}</pre>"
        "</article>"
    )


def build_report_site(
    reports_dir: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    reports_root = Path(reports_dir)
    output = Path(output_path) if output_path is not None else reports_root / "site" / "index.html"
    reports = {
        name: _load_json(reports_root / filename)
        for name, filename in REPORT_FILES.items()
    }

    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    status = " ".join(_report_status(name, report) for name, report in reports.items())
    baseline = reports["baseline"]
    walk_forward = reports["walk_forward"]
    execution = reports["execution"]

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Market Microstructure Lab Viewer</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #182026;
      --muted: #63717b;
      --line: #d9dfdf;
      --paper: #f7f8f4;
      --panel: #ffffff;
      --teal: #0f766e;
      --navy: #182c3a;
      --gold: #b7791f;
      --red: #b42318;
      --green: #157f3b;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}

    .hero {{
      background: linear-gradient(135deg, #102531 0%, #183f3b 50%, #705f21 100%);
      color: #fff;
      border-bottom: 1px solid rgba(255,255,255,0.16);
    }}

    .hero-inner {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 36px 24px 28px;
    }}

    .eyebrow {{
      margin: 0 0 10px;
      color: #bce6de;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      max-width: 920px;
      font-size: 40px;
      line-height: 1.08;
      letter-spacing: 0;
    }}

    .hero p {{
      max-width: 840px;
      color: #dbe9e4;
      margin: 14px 0 0;
      font-size: 17px;
    }}

    .status-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 22px;
    }}

    .status-pill {{
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      border: 1px solid rgba(255,255,255,0.24);
      border-radius: 999px;
      padding: 4px 12px;
      font-size: 13px;
      font-weight: 700;
      background: rgba(255,255,255,0.12);
    }}

    .status-pill.ready {{
      color: #d8ffe8;
    }}

    .status-pill.missing {{
      color: #ffe1d6;
    }}

    nav {{
      position: sticky;
      top: 0;
      z-index: 5;
      background: rgba(247,248,244,0.94);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(12px);
    }}

    nav .nav-inner {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 10px 24px;
      display: flex;
      gap: 8px;
      overflow-x: auto;
    }}

    nav a {{
      color: var(--navy);
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
      border-radius: 999px;
      padding: 7px 12px;
      white-space: nowrap;
    }}

    nav a:hover {{
      background: #e8efed;
    }}

    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 24px 48px;
    }}

    section {{
      margin-top: 30px;
    }}

    .section-head {{
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 16px;
      margin-bottom: 14px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 10px;
    }}

    h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: 0;
    }}

    .section-note {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      text-align: right;
    }}

    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}

    .metric-card,
    .figure-card,
    .table-card,
    .json-card,
    .assumption-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(18,32,38,0.04);
    }}

    .metric-card {{
      min-height: 122px;
      padding: 16px;
    }}

    .metric-label {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }}

    .metric-value {{
      margin: 8px 0 4px;
      font-size: 28px;
      line-height: 1.1;
      font-weight: 800;
      overflow-wrap: anywhere;
    }}

    .metric-detail {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }}

    .figure-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}

    .figure-card {{
      overflow: hidden;
    }}

    .figure-card h3,
    .json-card h3 {{
      margin: 0;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      font-size: 16px;
    }}

    .svg-shell {{
      padding: 12px;
      background: #fbfcfa;
      overflow-x: auto;
    }}

    .svg-shell svg {{
      width: 100%;
      height: auto;
      display: block;
    }}

    .table-grid,
    .json-grid,
    .assumption-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}

    .table-card {{
      overflow: hidden;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}

    th,
    td {{
      text-align: left;
      border-bottom: 1px solid var(--line);
      padding: 10px 12px;
      vertical-align: top;
    }}

    th {{
      background: #eef4f2;
      color: var(--navy);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
    }}

    tr:last-child td {{
      border-bottom: 0;
    }}

    pre {{
      margin: 0;
      padding: 14px 16px;
      overflow-x: auto;
      color: #25313a;
      background: #fbfcfa;
      font-size: 13px;
    }}

    .assumption-card {{
      padding: 16px;
    }}

    .assumption-card h3 {{
      margin: 0 0 8px;
      font-size: 16px;
    }}

    .assumption-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}

    .empty-state {{
      margin: 0;
      color: var(--muted);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}

    footer {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 0 24px 30px;
      color: var(--muted);
      font-size: 13px;
    }}

    @media (max-width: 920px) {{
      h1 {{
        font-size: 32px;
      }}

      .metric-grid,
      .figure-grid,
      .table-grid,
      .json-grid,
      .assumption-grid {{
        grid-template-columns: 1fr;
      }}

      .section-head {{
        align-items: flex-start;
        flex-direction: column;
      }}

      .section-note {{
        text-align: left;
      }}
    }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-inner">
      <p class="eyebrow">Research and replay dashboard</p>
      <h1>Market Microstructure Lab Viewer</h1>
      <p>Order-book capture, normalization, feature engineering, baseline research, execution simulation, and C++ replay summarized in one local report.</p>
      <div class="status-row">{status}</div>
    </div>
  </header>

  <nav aria-label="Report sections">
    <div class="nav-inner">
      <a href="#overview">Overview</a>
      <a href="#validation">Validation</a>
      <a href="#figures">Figures</a>
      <a href="#assumptions">Assumptions</a>
      <a href="#metadata">Metadata</a>
    </div>
  </nav>

  <main>
    <section id="overview">
      <div class="section-head">
        <h2>Pipeline Snapshot</h2>
        <p class="section-note">Generated {escape(generated_at)}</p>
      </div>
      <div class="metric-grid">
        {_baseline_metrics(baseline)}
        {_walk_forward_metrics(walk_forward)}
        {_execution_metrics(execution)}
      </div>
    </section>

    <section id="validation">
      <div class="section-head">
        <h2>Validation Detail</h2>
        <p class="section-note">Threshold search and rolling-window results</p>
      </div>
      <div class="table-grid">
        <article class="table-card">
          <table>
            <thead>
              <tr><th>Threshold</th><th>Rows</th><th>Correct</th><th>Accuracy</th></tr>
            </thead>
            <tbody>{_threshold_rows(baseline)}</tbody>
          </table>
        </article>
        <article class="table-card">
          <table>
            <thead>
              <tr><th>Window</th><th>Threshold</th><th>Rows</th><th>Correct</th><th>Accuracy</th></tr>
            </thead>
            <tbody>{_walk_forward_rows(walk_forward)}</tbody>
          </table>
        </article>
      </div>
    </section>

    <section id="figures">
      <div class="section-head">
        <h2>Figures</h2>
        <p class="section-note">SVG outputs from the research plotting command</p>
      </div>
      <div class="figure-grid">{_chart_cards(reports_root / "figures")}</div>
    </section>

    <section id="assumptions">
      <div class="section-head">
        <h2>Execution Assumptions</h2>
        <p class="section-note">Modeling choices used by the execution report</p>
      </div>
      <div class="assumption-grid">
        <article class="assumption-card">
          <h3>Market Data</h3>
          <p>Book events are normalized into JSONL with explicit channel, symbol, receive sequence, bids, asks, and event type fields.</p>
        </article>
        <article class="assumption-card">
          <h3>Labeling</h3>
          <p>Future labels are derived chronologically from mid-price movement, so no future rows are used in current-row features.</p>
        </article>
        <article class="assumption-card">
          <h3>Trading Costs</h3>
          <p>Execution includes spread, configurable fees, configurable slippage, latency in events, and partial queue fill assumptions.</p>
        </article>
        <article class="assumption-card">
          <h3>C++ Replay</h3>
          <p>The critical-path order book can replay normalized JSONL and report benchmark latency summaries across repeated runs.</p>
        </article>
      </div>
    </section>

    <section id="metadata">
      <div class="section-head">
        <h2>Report Metadata</h2>
        <p class="section-note">Compact view of report parameters</p>
      </div>
      <div class="json-grid">
        {_json_summary("Baseline", baseline)}
        {_json_summary("Walk Forward", walk_forward)}
        {_json_summary("Execution", execution)}
      </div>
    </section>
  </main>

  <footer>
    Built from local project artifacts in {escape(str(reports_root))}.
  </footer>
</body>
</html>
"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output
