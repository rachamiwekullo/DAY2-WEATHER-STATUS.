import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set random seed for reproducible sample data
np.random.seed(42)

# --- Step 1: Set up time series DataFrame with date index ---
dates = pd.date_range(start="2025-01-01", end="2026-06-30", freq="D")
n = len(dates)

# Generate baseline trend with December spikes and February dips
base_trend = 5000 + np.linspace(0, 1200, n)
seasonality = (
    0.22 * np.sin(2 * np.pi * (dates.dayofyear - 60) / 365.25)
    + 0.25 * np.where(dates.month == 12, 0.6, 0)
    - 0.20 * np.where(dates.month == 2, 0.4, 0)
)
daily_transactions = (
    base_trend * (1 + seasonality) + np.random.normal(0, 250, n)
).astype(int)

df = pd.DataFrame({"transactions": daily_transactions}, index=dates)
print(
    f"Step 1 Complete: DataFrame initialized with {len(df)} daily records from"
    f" {dates[0].date()} to {dates[-1].date()}."
)


# --- Step 2: Calculate month-over-month growth and rolling averages ---
monthly_df = df.resample("ME").sum()
monthly_df["mom_growth_pct"] = monthly_df["transactions"].pct_change() * 100
df["rolling_30d"] = df["transactions"].rolling(window=30).mean()
print("Step 2 Complete: MoM growth and 30-day rolling averages calculated.")


# --- Step 3: Resample data to different frequencies ---
resampled_daily = df["transactions"].resample("D").sum()
resampled_weekly = df["transactions"].resample("W").sum()
resampled_monthly = df["transactions"].resample("ME").sum()
resampled_quarterly = df["transactions"].resample("QE").sum()

print("Step 3 Complete Resampling Summary:")
print(f"  - Daily frequency records: {len(resampled_daily)}")
print(f"  - Weekly frequency periods: {len(resampled_weekly)}")
print(f"  - Monthly frequency periods: {len(resampled_monthly)}")
print(f"  - Quarterly frequency periods: {len(resampled_quarterly)}")


# --- Step 4: Plot time series to spot trend visual ---
fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.bar(
    monthly_df.index,
    monthly_df["transactions"],
    width=20,
    color="#1F4E79",
    alpha=0.8,
    label="Monthly Total Transactions",
)
ax1.set_title(
    "Nairobi Supermarket Chain: Foot Traffic Trends & 30-Day Rolling Average"
)
ax1.set_ylabel("Total Monthly Transactions", color="#1F4E79")
ax1.tick_params(axis="y", labelcolor="#1F4E79")

ax2 = ax1.twinx()
ax2.plot(
    df.index,
    df["rolling_30d"],
    color="#D62728",
    linewidth=2,
    label="30-Day Rolling Average",
)
ax2.set_ylabel("Daily Rolling Average", color="#D62728")
ax2.tick_params(axis="y", labelcolor="#D62728")

ax1.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("supermarket_traffic_trend.png", dpi=150)
print("Step 4 Complete: Chart saved as 'supermarket_traffic_trend.png'")


# --- Step 5: Identify peak, dips, and outliers in the time series ---
peak_month = monthly_df["transactions"].idxmax()
dip_month = monthly_df["transactions"].idxmin()

df["residual"] = df["transactions"] - df["rolling_30d"]
outliers = df[abs(df["residual"]) > 2.5 * df["residual"].std()]

print("\nStep 5 Complete: Key Insights Summary:")
print(
    f"  - Peak Traffic Month: {peak_month.strftime('%B %Y')} ("
    f"{monthly_df.loc[peak_month, 'transactions']:,} transactions)"
)
print(
    f"  - Lowest Traffic Month: {dip_month.strftime('%B %Y')} ("
    f"{monthly_df.loc[dip_month, 'transactions']:,} transactions)"
)
print(
    f"  - Significant Daily Outlier Events Detected: {len(outliers)} anomalous"
    " days"
)