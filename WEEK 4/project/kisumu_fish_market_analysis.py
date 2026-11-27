import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "kisumu_fish_market.db"
CHART_PATH = "kisumu_fish_market_report.png"
REPORT_PATH = "kisumu_fish_market_sponsor_report.md"


def setup_database(db_path: str = DB_PATH) -> None:
    """Create SQLite database and insert 54 fish market sales rows across three months."""
    rng = np.random.default_rng(42)

    vendors = [
        "Onyango Fish Point",
        "Akinyi Lake Catch",
        "Dunga Pier Traders",
        "Otieno Tilapia Hub",
        "Auma Nile Perch Co",
        "Jubilee Beach Market",
        "Kondele Fresh Fish",
        "Nyalenda Fish Stall",
    ]
    fish_types = ["Tilapia", "Nile Perch", "Omena (Dagaa)"]

    dates_aug = pd.date_range("2026-08-01", "2026-08-31", periods=16).strftime("%Y-%m-%d").tolist()
    dates_sep = pd.date_range("2026-09-01", "2026-09-30", periods=18).strftime("%Y-%m-%d").tolist()
    dates_oct = pd.date_range("2026-10-01", "2026-10-31", periods=20).strftime("%Y-%m-%d").tolist()
    all_dates = dates_aug + dates_sep + dates_oct

    rows = []
    for idx, dt in enumerate(all_dates, start=1):
        month_str = dt[:7]
        if idx % 7 == 0:
            vendor = "Onyango Fish Point"
        elif idx % 5 == 0:
            vendor = "Akinyi Lake Catch"
        elif idx % 4 == 0:
            vendor = "Dunga Pier Traders"
        else:
            vendor = vendors[idx % len(vendors)]

        fish = fish_types[idx % len(fish_types)]
        buyer = "wholesale" if idx % 3 != 0 else "retail"
        month_boost = 1.0 if month_str == "2026-08" else (1.18 if month_str == "2026-09" else 1.36)

        if buyer == "wholesale":
            kg = round(float(rng.integers(35, 85)) * month_boost, 1)
            if fish == "Tilapia":
                price_per_kg = float(rng.integers(380, 440))
            elif fish == "Nile Perch":
                price_per_kg = float(rng.integers(340, 400))
            else:
                price_per_kg = float(rng.integers(150, 190))
        else:
            kg = round(float(rng.integers(8, 24)) * month_boost, 1)
            if fish == "Tilapia":
                price_per_kg = float(rng.integers(520, 600))
            elif fish == "Nile Perch":
                price_per_kg = float(rng.integers(470, 550))
            else:
                price_per_kg = float(rng.integers(230, 290))

        rows.append((idx, vendor, fish, kg, price_per_kg, dt, buyer))

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS fish_sales;")
    cur.execute(
        """
        CREATE TABLE fish_sales (
            sale_id INTEGER PRIMARY KEY,
            vendor_name TEXT NOT NULL,
            fish_type TEXT NOT NULL,
            kg_sold REAL NOT NULL,
            price_per_kg REAL NOT NULL,
            sale_date TEXT NOT NULL,
            buyer_type TEXT NOT NULL CHECK (buyer_type IN ('retail', 'wholesale'))
        );
        """
    )
    cur.executemany(
        """
        INSERT INTO fish_sales (
            sale_id, vendor_name, fish_type, kg_sold, price_per_kg, sale_date, buyer_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        rows,
    )
    conn.commit()
    conn.close()


def analyze_and_visualize(db_path: str = DB_PATH, chart_path: str = CHART_PATH) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Pull SQL results into pandas DataFrames and generate a three-panel summary chart."""
    conn = sqlite3.connect(db_path)

    q1_top_vendors = """
    SELECT
        vendor_name,
        COUNT(*) AS transactions,
        ROUND(SUM(kg_sold), 1) AS total_kg,
        ROUND(SUM(kg_sold * price_per_kg), 2) AS total_revenue_kes
    FROM fish_sales
    GROUP BY vendor_name
    ORDER BY total_revenue_kes DESC
    LIMIT 3;
    """

    q2_buyer_profitability = """
    SELECT
        buyer_type,
        COUNT(*) AS transactions,
        ROUND(SUM(kg_sold), 1) AS total_kg,
        ROUND(AVG(price_per_kg), 2) AS avg_price_per_kg_kes,
        ROUND(SUM(kg_sold * price_per_kg) / SUM(kg_sold), 2) AS weighted_revenue_per_kg_kes,
        ROUND(SUM(kg_sold * price_per_kg), 2) AS total_revenue_kes
    FROM fish_sales
    GROUP BY buyer_type
    ORDER BY avg_price_per_kg_kes DESC;
    """

    q3_monthly_trend = """
    SELECT
        strftime('%Y-%m', sale_date) AS month,
        COUNT(*) AS transactions,
        ROUND(SUM(kg_sold), 1) AS total_kg,
        ROUND(SUM(kg_sold * price_per_kg), 2) AS total_revenue_kes
    FROM fish_sales
    GROUP BY strftime('%Y-%m', sale_date)
    ORDER BY month ASC;
    """

    df_vendors = pd.read_sql_query(q1_top_vendors, conn)
    df_buyers = pd.read_sql_query(q2_buyer_profitability, conn)
    df_monthly = pd.read_sql_query(q3_monthly_trend, conn)
    conn.close()

    print("\n=== 1. Top 3 Vendors by Revenue ===")
    print(df_vendors.to_string(index=False))

    print("\n=== 2. Retail vs. Wholesale Price & Revenue per Kg ===")
    print(df_buyers.to_string(index=False))

    print("\n=== 3. Monthly Revenue Trend ===")
    print(df_monthly.to_string(index=False))

    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.8))
    fig.patch.set_facecolor("white")

    axes[0].barh(df_vendors["vendor_name"][::-1], (df_vendors["total_revenue_kes"] / 1000)[::-1], color="#1b6ca8")
    axes[0].set_title("Top 3 Vendors by Revenue")
    axes[0].set_xlabel("Revenue (KES Thousands)")
    axes[0].set_xlim(0, 265)
    axes[0].grid(axis="x", linestyle=":", alpha=0.6)
    for i, val in enumerate((df_vendors["total_revenue_kes"] / 1000)[::-1]):
        axes[0].text(val + 4, i, f"{val:.1f}k", va="center", fontsize=9)

    bars_b = axes[1].bar(
        df_buyers["buyer_type"].str.title(),
        df_buyers["avg_price_per_kg_kes"],
        color=["#2a9d8f", "#e9c46a"],
        width=0.48,
    )
    axes[1].set_title("Average Price per Kg")
    axes[1].set_ylabel("KES / kg")
    axes[1].set_ylim(0, 650)
    axes[1].grid(axis="y", linestyle=":", alpha=0.6)
    for bar in bars_b:
        h = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width() / 2, h + 14, f"KES {h:.0f}", ha="center", va="bottom", fontsize=9)

    bars_m = axes[2].bar(df_monthly["month"], df_monthly["total_revenue_kes"] / 1000, color="#264653", width=0.48)
    axes[2].plot(df_monthly["month"], df_monthly["total_revenue_kes"] / 1000, color="#e76f51", marker="o", linewidth=2)
    axes[2].set_title("Monthly Revenue Trend")
    axes[2].set_ylabel("Revenue (KES Thousands)")
    axes[2].set_ylim(0, 450)
    axes[2].grid(axis="y", linestyle=":", alpha=0.6)
    for bar in bars_m:
        h = bar.get_height()
        axes[2].text(bar.get_x() + bar.get_width() / 2, h + 16, f"{h:.0f}k", ha="center", va="bottom", fontsize=9)

    plt.suptitle("Kisumu Fish Market — Three-Month Sponsor Summary (Aug–Oct 2026)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(chart_path, dpi=200)
    plt.close()

    return df_vendors, df_buyers, df_monthly


def write_sponsor_report(report_path: str = REPORT_PATH) -> None:
    """Save a ~200-word sponsor report covering the three findings and one recommendation."""
    report_markdown = """# Kisumu Fish Market Three-Month Digital Sales Report

Prepared for: Kisumu County Government Sponsor Review  
Period Covered: August–October 2026 (54 Recorded Transactions)

## Executive Findings

Digital sales records from the Kisumu fish market association's first three months show strong early traction and clear commercial priorities for county sponsorship. First, three vendors lead revenue generation: Dunga Pier Traders (KES 222,211.20 across 740.7 kg), Akinyi Lake Catch (KES 218,876.50 across 727.9 kg), and Otieno Tilapia Hub (KES 111,558.80 across 298.6 kg), anchored by steady sales across Tilapia, Nile Perch, and Omena. Second, retail transactions earn substantially more per kilogram on average than wholesale sales—averaging KES 563.00 per kg for retail buyers versus KES 270.58 per kg for wholesale buyers—while wholesale buyers generate higher total turnover (KES 720,831.80 versus KES 197,549.10) through larger batch sizes. Third, total market revenue is trending upward across all three months, rising from KES 224,927.00 in August to KES 314,919.30 in September and KES 378,534.60 in October as monthly volumes grew from 725.0 kg to 1,271.7 kg.

## Recommendation

Direct county sponsor funds toward cold-storage facilities, digital weighing scales, and clean stall upgrades at key landing and market bays so vendors preserve catch quality, sustain monthly volume growth, and capture stronger retail and wholesale margins.
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_markdown.strip() + "\n")


if __name__ == "__main__":
    setup_database()
    analyze_and_visualize()
    write_sponsor_report()