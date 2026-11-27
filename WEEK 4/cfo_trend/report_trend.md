# Distributor CFO Trend Analysis

A SQLite and Python (`pandas`) reporting script that answers board-level questions about regional order completion, month-on-month customer growth, and cumulative daily revenue. It brings three complementary views of distributor performance together for CFO and leadership reviews.

## Features

- **SQLite Distributor Data:** Creates related `customers` and `orders` tables with county, account tier, order value, date, and status information.
- **Sample Data:** Seeds 12 customers and 25 orders across six counties.
- **County Order Status Mix:** Compares completed, pending, and cancelled order percentages by county.
- **Customer Growth Analysis:** Uses monthly order totals and `LAG()` to find customers whose order value increased for two successive month-over-month comparisons.
- **Daily Revenue Trend:** Calculates daily revenue and a cumulative running total, excluding cancelled orders.
- **Pandas Results:** Runs and prints each SQL result with `pandas.read_sql_query`.

## Project Structure

- `trend_analysis.py`       # Creates and seeds the SQLite tables, runs the three trend queries, and prints results
- `distributor_cfo_trends.db` # SQLite database used by the script
- `report_trend.md`         # Board report findings and setup guide

## What Each Query Answers & Why the CFO Cares

### 1. County Order Status Mix

Shows each county's total order count and the percentages completed, pending, and cancelled. It highlights fulfillment follow-up needs and differences in cancellation rates between regions.

### 2. Customers with Consecutive Month-on-Month Growth (`LAG()`)

Compares each customer's order value for the latest month with the two preceding months, excluding cancelled orders. It identifies accounts with two successive increases as possible candidates for retention focus and a closer review of credit terms.

### 3. Cumulative Daily Revenue

Groups non-cancelled orders by date and calculates the running revenue total across the reporting period. Pending orders are included, so the total represents non-cancelled order value rather than confirmed cash receipts.

## Board Report Key Findings

- **County Order Status Mix:** Mombasa has the highest cancellation rate at **16.7%**. Uasin Gishu has the highest pending share at **33.3%**, highlighting orders for fulfillment follow-up.
- **Consecutive Month-on-Month Customer Growth:** **Kamau Stores**, **Otieno Wholesale**, and **Hassan Traders** each show two successive monthly order-value increases from August through October 2026. These accounts merit retention focus and review for suitable credit terms.
- **Running Total of Revenue by Date:** Cumulative non-cancelled order value reaches **KES 2,262,950** across August–October 2026, providing a view of revenue pacing over time.

## Recommendation

Prioritize follow-up on pending orders in Uasin Gishu and review cancellation causes in Mombasa. Use the customer growth results to guide account-retention discussions, while treating the running total as order value—not cash collected—because pending orders are included.

## Findings Summary

The sample data spans 12 customers, 25 orders, and six counties. Together, the reports show regional order outcomes, flag three customers with consecutive monthly growth, and track cumulative non-cancelled revenue across the sample period. Cancelled orders are excluded from the growth and revenue queries; the status-mix query includes all orders.

## Installation & Setup

### Prerequisites

- Python 3.7+ installed on your system.
- SQLite is included with Python; no separate database installation is required.
- Pandas.

### Steps

Open a terminal in the project directory and install Pandas:

```powershell
python -m pip install pandas
```

## Usage

Run the analysis script from the CFO trend directory:

```powershell
python trend_analysis.py
```

The script calls `setup_database()` before running the reports. **This drops and recreates the `customers` and `orders` tables in `distributor_cfo_trends.db` and replaces their contents with the bundled sample data.** Back up any database data you need before running it. To query an existing database, call `run_cfo_trend_queries(db_path)` from Python without calling `setup_database()`.

## Sample Output

```text
=== 1. County Order Status Mix (%) ===
     county  total_orders  completed_pct  pending_pct  cancelled_pct
     Kiambu             2          100.0          0.0            0.0
     Nakuru             1          100.0          0.0            0.0
     Kisumu             5           80.0         20.0            0.0
    Nairobi             8           75.0         12.5           12.5
    Mombasa             6           66.7         16.7           16.7
Uasin Gishu             3           66.7         33.3            0.0

=== 2. Customers with >= 2 Consecutive MoM Order Value Increases (LAG) ===
 customer_id  customer_name       county account_tier latest_streak_month  month_1_value_kes  month_2_value_kes  month_3_value_kes
           1   Kamau Stores      Nairobi     Platinum            2026-10            76000.0           114000.0           152000.0
           7 Otieno Wholesale      Kisumu         Gold            2026-10            69000.0           103500.0           138000.0
           4 Hassan Traders     Mombasa     Platinum            2026-10            64000.0            96000.0           128000.0

=== 3. Running Total of Revenue by Date Across All Counties ===
 order_date  orders_that_day  daily_revenue_kes  running_total_revenue_kes
        ...              ...                ...                        ...
 2026-10-30                1           103500.0                  2262950.0
```