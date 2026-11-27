import sqlite3
import pandas as pd

DB_PATH = "distributor_cfo_trends.db"


def setup_database(db_path: str = DB_PATH) -> None:
    """Create and seed customers and orders tables for CFO trend analysis."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("DROP TABLE IF EXISTS orders;")
    cur.execute("DROP TABLE IF EXISTS customers;")

    cur.execute(
        """
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            county TEXT NOT NULL,
            account_tier TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        );
        """
    )

    customers_data = [
        (1, "Kamau Stores", "Nairobi", "Platinum"),
        (2, "Westlands Provision", "Nairobi", "Gold"),
        (3, "Eastleigh Superstore", "Nairobi", "Gold"),
        (4, "Hassan Traders", "Mombasa", "Platinum"),
        (5, "Pwani Mart", "Mombasa", "Gold"),
        (6, "Kilindini Distributors", "Mombasa", "Gold"),
        (7, "Otieno Wholesale", "Kisumu", "Gold"),
        (8, "Kondele Mini Mart", "Kisumu", "Silver"),
        (9, "Eldoret Central Stores", "Uasin Gishu", "Gold"),
        (10, "Uasin Gishu Depot", "Uasin Gishu", "Silver"),
        (11, "Thika Road Mart", "Kiambu", "Gold"),
        (12, "Naivasha Supply Co", "Nakuru", "Silver"),
    ]

    orders_data = [
        # Kamau Stores (Nairobi): Aug=76,000 -> Sep=114,000 -> Oct=152,000 (2 consecutive MoM increases)
        (301, 1, "Cooking Oil 20L", 20, 3800.0, "2026-08-12", "Completed"),
        (302, 1, "Cooking Oil 20L", 30, 3800.0, "2026-09-14", "Completed"),
        (303, 1, "Cooking Oil 20L", 40, 3800.0, "2026-10-16", "Completed"),
        # Westlands Provision (Nairobi): Aug=128,000 -> Sep=96,000 -> Oct=144,000 (only 1 increase)
        (304, 2, "Rice 25kg", 40, 3200.0, "2026-08-15", "Completed"),
        (305, 2, "Rice 25kg", 30, 3200.0, "2026-09-18", "Pending"),
        (306, 2, "Rice 25kg", 45, 3200.0, "2026-10-20", "Completed"),
        # Eastleigh Superstore (Nairobi): Sep=84,000 -> Oct=63,000 (Cancelled)
        (307, 3, "Tea Leaves 500g (Carton)", 20, 4200.0, "2026-09-10", "Completed"),
        (308, 3, "Tea Leaves 500g (Carton)", 15, 4200.0, "2026-10-12", "Cancelled"),
        # Hassan Traders (Mombasa): Aug=64,000 -> Sep=96,000 -> Oct=128,000 (2 consecutive MoM increases)
        (309, 4, "Rice 25kg", 20, 3200.0, "2026-08-08", "Completed"),
        (310, 4, "Rice 25kg", 30, 3200.0, "2026-09-11", "Completed"),
        (311, 4, "Rice 25kg", 40, 3200.0, "2026-10-15", "Completed"),
        # Pwani Mart (Mombasa): Sep=92,500 -> Oct=55,500
        (312, 5, "Maize Flour 2kg (Bale)", 50, 1850.0, "2026-09-19", "Completed"),
        (313, 5, "Maize Flour 2kg (Bale)", 30, 1850.0, "2026-10-22", "Pending"),
        # Kilindini Distributors (Mombasa): Oct=124,200 (Cancelled)
        (314, 6, "Sugar 50kg", 18, 6900.0, "2026-10-25", "Cancelled"),
        # Otieno Wholesale (Kisumu): Aug=69,000 -> Sep=103,500 -> Oct=138,000 (2 consecutive MoM increases)
        (315, 7, "Sugar 50kg", 10, 6900.0, "2026-08-18", "Completed"),
        (316, 7, "Sugar 50kg", 15, 6900.0, "2026-09-21", "Completed"),
        (317, 7, "Sugar 50kg", 20, 6900.0, "2026-10-24", "Completed"),
        # Kondele Mini Mart (Kisumu): Sep=50,750 -> Oct=40,700
        (318, 8, "Bar Soap (Carton)", 35, 1450.0, "2026-09-23", "Completed"),
        (319, 8, "Maize Flour 2kg (Bale)", 22, 1850.0, "2026-10-26", "Pending"),
        # Eldoret Central Stores (Uasin Gishu): Aug=92,500 -> Sep=129,500
        (320, 9, "Maize Flour 2kg (Bale)", 50, 1850.0, "2026-08-22", "Completed"),
        (321, 9, "Maize Flour 2kg (Bale)", 70, 1850.0, "2026-09-25", "Completed"),
        # Uasin Gishu Depot (Uasin Gishu): Oct=95,000
        (322, 10, "Cooking Oil 20L", 25, 3800.0, "2026-10-28", "Pending"),
        # Thika Road Mart (Kiambu): Sep=152,000 -> Oct=58,500
        (323, 11, "Cooking Oil 20L", 40, 3800.0, "2026-09-27", "Completed"),
        (324, 11, "Wheat Flour 2kg (Bale)", 30, 1950.0, "2026-10-29", "Completed"),
        # Naivasha Supply Co (Nakuru): Oct=103,500
        (325, 12, "Sugar 50kg", 15, 6900.0, "2026-10-30", "Completed"),
    ]

    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?);", customers_data)
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?);", orders_data)
    conn.commit()
    conn.close()


def run_cfo_trend_queries(db_path: str = DB_PATH) -> None:
    """Run the three CFO board trend queries via pandas and print results."""
    conn = sqlite3.connect(db_path)

    # Business interpretation: Order fulfillment reliability varies across counties, with Mombasa showing the highest cancellation rate (16.7%) and Uasin Gishu holding the highest share of pending orders (33.3%) that require fulfillment follow-up.
    query_1_status_mix = """
    SELECT
        c.county,
        COUNT(o.order_id) AS total_orders,
        ROUND(100.0 * SUM(CASE WHEN o.status = 'Completed' THEN 1 ELSE 0 END) / COUNT(o.order_id), 1) AS completed_pct,
        ROUND(100.0 * SUM(CASE WHEN o.status = 'Pending' THEN 1 ELSE 0 END) / COUNT(o.order_id), 1) AS pending_pct,
        ROUND(100.0 * SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(o.order_id), 1) AS cancelled_pct
    FROM customers c
    INNER JOIN orders o
        ON c.customer_id = o.customer_id
    GROUP BY c.county
    ORDER BY completed_pct DESC, c.county ASC;
    """

    # Business interpretation: Sustained multi-month expansion is concentrated among three expanding accounts—Kamau Stores, Otieno Wholesale, and Hassan Traders—which are prime candidates for priority credit terms and retention focus.
    query_2_consecutive_growth = """
    WITH monthly_customer_orders AS (
        SELECT
            c.customer_id,
            c.customer_name,
            c.county,
            c.account_tier,
            strftime('%Y-%m', o.order_date) AS order_month,
            SUM(o.quantity * o.unit_price) AS monthly_order_value_kes
        FROM customers c
        INNER JOIN orders o
            ON c.customer_id = o.customer_id
        WHERE o.status != 'Cancelled'
        GROUP BY c.customer_id, c.customer_name, c.county, c.account_tier, strftime('%Y-%m', o.order_date)
    ),
    with_lags AS (
        SELECT
            customer_id,
            customer_name,
            county,
            account_tier,
            order_month,
            monthly_order_value_kes,
            LAG(monthly_order_value_kes, 1) OVER (PARTITION BY customer_id ORDER BY order_month) AS prev_1_value,
            LAG(monthly_order_value_kes, 2) OVER (PARTITION BY customer_id ORDER BY order_month) AS prev_2_value
        FROM monthly_customer_orders
    ),
    consecutive_streaks AS (
        SELECT
            customer_id,
            customer_name,
            county,
            account_tier,
            order_month AS latest_streak_month,
            prev_2_value AS month_1_value_kes,
            prev_1_value AS month_2_value_kes,
            monthly_order_value_kes AS month_3_value_kes,
            CASE
                WHEN prev_1_value IS NOT NULL
                 AND prev_2_value IS NOT NULL
                 AND monthly_order_value_kes > prev_1_value
                 AND prev_1_value > prev_2_value
                THEN 1 ELSE 0
            END AS two_step_increase
        FROM with_lags
    )
    SELECT
        customer_id,
        customer_name,
        county,
        account_tier,
        latest_streak_month,
        ROUND(month_1_value_kes, 2) AS month_1_value_kes,
        ROUND(month_2_value_kes, 2) AS month_2_value_kes,
        ROUND(month_3_value_kes, 2) AS month_3_value_kes
    FROM consecutive_streaks
    WHERE two_step_increase = 1
    ORDER BY month_3_value_kes DESC;
    """

    # Business interpretation: Cumulative non-cancelled revenue climbs steadily to KES 2,262,950 across August–October 2026, giving leadership clear visibility into cash-flow velocity and late-month billing pacing.
    query_3_running_total = """
    WITH daily_revenue AS (
        SELECT
            o.order_date,
            COUNT(o.order_id) AS orders_that_day,
            SUM(o.quantity * o.unit_price) AS daily_revenue_kes
        FROM orders o
        WHERE o.status != 'Cancelled'
        GROUP BY o.order_date
    )
    SELECT
        order_date,
        orders_that_day,
        ROUND(daily_revenue_kes, 2) AS daily_revenue_kes,
        ROUND(
            SUM(daily_revenue_kes) OVER (
                ORDER BY order_date ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ),
            2
        ) AS running_total_revenue_kes
    FROM daily_revenue
    ORDER BY order_date ASC;
    """

    sections = [
        ("1. County Order Status Mix (%)", query_1_status_mix),
        ("2. Customers with >= 2 Consecutive MoM Order Value Increases (LAG)", query_2_consecutive_growth),
        ("3. Running Total of Revenue by Date Across All Counties", query_3_running_total),
    ]

    for title, sql in sections:
        print(f"\n=== {title} ===")
        df = pd.read_sql_query(sql, conn)
        print(df.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    setup_database()
    run_cfo_trend_queries()