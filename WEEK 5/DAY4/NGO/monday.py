import base64
from datetime import datetime
from html import escape
import logging
from pathlib import Path
import time
from typing import TypedDict

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "nutrition_program-v2.csv"
CHARTS_DIR = BASE_DIR / "charts"
LOG_FILE = BASE_DIR / "report.log"


class ChartPaths(TypedDict):
    completion: Path
    trend: Path
    adherence: Path


class ProgramSummary(TypedDict):
    report_date: str
    display_timestamp: str
    enrolled_total: int
    completed_total: int
    completion_rate: float
    avg_nutrition_score: float
    avg_adherence_pct: float
    top_site: str
    charts: ChartPaths


def _save_bar_chart(
    series: pd.Series,
    title: str,
    xlabel: str,
    ylabel: str,
    out_path: Path,
    color: str = "#1F4E79",
) -> Path:
    """Render and save a bar chart as a PNG file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    series.plot(kind="bar", color=color, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def _save_line_chart(
    series: pd.Series,
    title: str,
    xlabel: str,
    ylabel: str,
    out_path: Path,
    color: str = "#1F4E79",
) -> Path:
    """Render and save a line chart as a PNG file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(series.index.astype(str), series.values, marker="o", linewidth=2, color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def generate_report(run_dt: datetime | None = None) -> ProgramSummary:
    """Load nutrition program data, compute metrics, and save three PNG charts."""
    current_dt = run_dt or datetime.now()
    report_date = current_dt.strftime("%Y-%m-%d")
    display_timestamp = current_dt.strftime("%A %d %B %Y at %H:%M")

    df = pd.read_csv(DATA_FILE)
    required_columns = {
        "period",
        "cohort",
        "site",
        "enrolled",
        "completed",
        "nutrition_score",
        "adherence_pct",
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Nutrition program data is missing required columns: {missing}")
    if df.empty:
        raise ValueError("Nutrition program data contains no records.")
    if df[list(required_columns)].isna().any().any():
        raise ValueError("Nutrition program data contains missing values in required columns.")

    numeric_columns = ["enrolled", "completed", "nutrition_score", "adherence_pct"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="raise")

    enrolled_total = int(df["enrolled"].sum())
    completed_total = int(df["completed"].sum())
    if enrolled_total <= 0:
        raise ValueError("Nutrition program data must have a positive enrolled total.")

    # Chart 1: Program Completion Rate (%) by Site
    site_totals = df.groupby("site")[["enrolled", "completed"]].sum()
    site_completion_rate = (
        site_totals["completed"] / site_totals["enrolled"] * 100
    ).sort_values(ascending=False)
    completion_chart = _save_bar_chart(
        series=site_completion_rate,
        title="Program Completion Rate by Site",
        xlabel="Site",
        ylabel="Completion Rate (%)",
        out_path=CHARTS_DIR / "site_completion_rate.png",
        color="#1F4E79",
    )

    # Chart 2: Average Nutrition Score Over Reporting Period
    df_sorted = df.copy()
    df_sorted["_period_dt"] = pd.to_datetime(
    df_sorted["period"],
    format="mixed",
    dayfirst=True,
)
    df_sorted = df_sorted.sort_values("_period_dt")
    nutrition_trend = df_sorted.groupby("period", sort=False)["nutrition_score"].mean()
    trend_chart = _save_line_chart(
        series=nutrition_trend,
        title="Average Nutrition Score Over Time",
        xlabel="Reporting Period",
        ylabel="Average Nutrition Score",
        out_path=CHARTS_DIR / "nutrition_score_trend.png",
        color="#2E7D32",
    )

    # Chart 3: Average Adherence (%) by Cohort
    cohort_adherence = (
        df.groupby("cohort")["adherence_pct"].mean().sort_values(ascending=False)
    )
    adherence_chart = _save_bar_chart(
        series=cohort_adherence,
        title="Average Adherence Rate by Cohort",
        xlabel="Cohort",
        ylabel="Adherence (%)",
        out_path=CHARTS_DIR / "adherence_by_cohort.png",
        color="#0D6E6E",
    )

    return {
        "report_date": report_date,
        "display_timestamp": display_timestamp,
        "enrolled_total": enrolled_total,
        "completed_total": completed_total,
        "completion_rate": completed_total / enrolled_total * 100,
        "avg_nutrition_score": float(df["nutrition_score"].mean()),
        "avg_adherence_pct": float(df["adherence_pct"].mean()),
        "top_site": str(site_completion_rate.idxmax()),
        "charts": {
            "completion": completion_chart,
            "trend": trend_chart,
            "adherence": adherence_chart,
        },
    }


def _img_data_uri(chart_path: Path) -> str:
    """Encode a PNG file into a Base64 data URI for standalone HTML."""
    encoded = base64.b64encode(chart_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def build_html_report(data: ProgramSummary) -> Path:
    """Write a self-contained HTML report named report_YYYY-MM-DD.html."""
    report_date = data["report_date"]
    output_file = BASE_DIR / f"report_{report_date}.html"

    one_paragraph_summary = (
        f"As of {escape(report_date)}, the nutrition program recorded "
        f"{data['enrolled_total']:,} total enrollments and {data['completed_total']:,} "
        f"completions ({data['completion_rate']:.1f}% overall completion rate), with an average "
        f"nutrition score of {data['avg_nutrition_score']:.1f}, an average adherence rate of "
        f"{data['avg_adherence_pct']:.1f}%, and {escape(data['top_site'])} leading site-level completion."
    )

    completion_uri = _img_data_uri(data["charts"]["completion"])
    trend_uri = _img_data_uri(data["charts"]["trend"])
    adherence_uri = _img_data_uri(data["charts"]["adherence"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nutrition Program Report - {escape(report_date)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172b3a;
      --muted: #607384;
      --accent: #0f766e;
      --line: #dce6ec;
      --paper: #ffffff;
      --canvas: #f2f6f8;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 44px 28px 64px;
      background: var(--canvas);
      color: var(--ink);
      font: 16px/1.65 Inter, "Segoe UI", Arial, sans-serif;
    }}
    h1 {{
      margin: 0 0 10px;
      padding-bottom: 16px;
      border-bottom: 3px solid var(--accent);
      color: #123b52;
      font-size: clamp(1.8rem, 4vw, 2.6rem);
      line-height: 1.2;
      letter-spacing: -0.035em;
    }}
    .meta {{
      display: inline-block;
      margin-bottom: 24px;
      padding: 5px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--paper);
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .summary {{
      margin-bottom: 26px;
      padding: 22px 24px;
      border: 1px solid var(--line);
      border-left: 5px solid var(--accent);
      border-radius: 12px;
      background: var(--paper);
      box-shadow: 0 8px 24px rgba(23, 43, 58, 0.06);
    }}
    .summary p {{
      margin: 0;
      font-size: 1.04rem;
    }}
    .chart-block {{
      margin-bottom: 24px;
      padding: 22px 24px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--paper);
      box-shadow: 0 8px 24px rgba(23, 43, 58, 0.06);
      page-break-inside: avoid;
    }}
    .chart-block h2 {{
      margin: 0 0 16px;
      color: #174e61;
      font-size: 1.2rem;
      line-height: 1.35;
    }}
    .chart-block img {{
      display: block;
      width: 100%;
      max-width: 100%;
      height: auto;
      margin: 0 auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    @media (max-width: 640px) {{
      body {{
        padding: 28px 14px 40px;
      }}
      .summary,
      .chart-block {{
        padding: 18px;
      }}
    }}
    @media print {{
      body {{
        max-width: none;
        padding: 0;
        background: #fff;
      }}
      .summary,
      .chart-block {{
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>
  <h1>Nutrition Program Report - {escape(report_date)}</h1>
  <div class="meta">Generated on {escape(data["display_timestamp"])}</div>

  <div class="summary">
    <p>{one_paragraph_summary}</p>
  </div>

  <div class="chart-block">
    <h2>1. Program Completion Rate by Site</h2>
    <img src="{completion_uri}" alt="Program Completion Rate by Site">
  </div>

  <div class="chart-block">
    <h2>2. Average Nutrition Score Over Time</h2>
    <img src="{trend_uri}" alt="Average Nutrition Score Over Time">
  </div>

  <div class="chart-block">
    <h2>3. Average Adherence Rate by Cohort</h2>
    <img src="{adherence_uri}" alt="Average Adherence Rate by Cohort">
  </div>
</body>
</html>
"""
    output_file.write_text(html, encoding="utf-8")
    print(f"Report saved to {output_file}")
    return output_file


def weekly_job(run_dt: datetime | None = None) -> None:
    """Generate the weekly report and log success or failure."""
    try:
        data = generate_report(run_dt=run_dt)
        build_html_report(data)
        logging.info("Weekly report generated and saved OK for %s", data["report_date"])
    except Exception:
        logging.exception("Weekly report generation failed")


def main() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
    )
    weekly_job()

    import schedule

    schedule.every().monday.at("07:00").do(weekly_job)
    logging.info("Weekly report scheduled for Monday at 07:00 local time")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()