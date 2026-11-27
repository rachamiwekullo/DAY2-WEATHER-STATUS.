import sqlite3
import pandas as pd

DB_PATH = "distributor_customers_orders.db"
REPORT_COLUMNS = ["product", "total_orders", "total_quantity", "total_revenue_kes"]


def init_sample_database(db_path: str = DB_PATH) -> None:
    """Create and seed customers and orders tables if running standalone."""
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
        (4, "South B Wholesalers", "Nairobi", "Silver"),
        (5, "Hassan Traders", "Mombasa", "Platinum"),
        (6, "Pwani Mart", "Mombasa", "Gold"),
        (7, "Kilindini Distributors", "Mombasa", "Gold"),
        (8, "Otieno Wholesale", "Kisumu", "Gold"),
        (9, "Kondele Mini Mart", "Kisumu", "Silver"),
        (10, "Eldoret Central Stores", "Uasin Gishu", "Gold"),
        (11, "Uasin Gishu Depot", "Uasin Gishu", "Silver"),
        (12, "Thika Road Mart", "Kiambu", "Gold"),
    ]

    orders_data = [
        (201, 1, "Cooking Oil 20L", 40, 3800.0, "2026-10-03", "Delivered"),
        (202, 1, "Rice 25kg", 30, 3200.0, "2026-10-14", "Delivered"),
        (203, 1, "Maize Flour 2kg (Bale)", 50, 1850.0, "2026-10-27", "Delivered"),
        (204, 1, "Cooking Oil 20L", 35, 3800.0, "2026-11-05", "Delivered"),
        (205, 1, "Sugar 50kg", 20, 6900.0, "2026-11-16", "Delivered"),
        (206, 2, "Rice 25kg", 55, 3200.0, "2026-10-06", "Delivered"),
        (207, 2, "Bar Soap (Carton)", 45, 1450.0, "2026-10-19", "Delivered"),
        (208, 2, "Tea Leaves 500g (Carton)", 25, 4200.0, "2026-11-04", "Delivered"),
        (209, 2, "Rice 25kg", 30, 3200.0, "2026-11-18", "Delivered"),
        (210, 3, "Tea Leaves 500g (Carton)", 30, 4200.0, "2026-10-12", "Delivered"),
        (211, 3, "Wheat Flour 2kg (Bale)", 40, 1950.0, "2026-11-09", "Pending"),
        (212, 4, "Maize Flour 2kg (Bale)", 65, 1850.0, "2026-11-21", "Delivered"),
        (213, 5, "Rice 25kg", 40, 3200.0, "2026-10-08", "Delivered"),
        (214, 5, "Sugar 50kg", 22, 6900.0, "2026-10-22", "Delivered"),
        (215, 5, "Cooking Oil 20L", 28, 3800.0, "2026-11-07", "Delivered"),
        (216, 5, "Bar Soap (Carton)", 50, 1450.0, "2026-11-19", "Delivered"),
        (217, 6, "Maize Flour 2kg (Bale)", 50, 1850.0, "2026-10-15", "Delivered"),
        (218, 6, "Rice 25kg", 20, 3200.0, "2026-11-11", "Pending"),
        (219, 7, "Sugar 50kg", 18, 6900.0, "2026-11-14", "Pending"),
        (220, 8, "Sugar 50kg", 20, 6900.0, "2026-10-09", "Delivered"),
        (221, 8, "Cooking Oil 20L", 30, 3800.0, "2026-10-25", "Delivered"),
        (222, 8, "Maize Flour 2kg (Bale)", 40, 1850.0, "2026-11-06", "Delivered"),
        (223, 8, "Sugar 50kg", 15, 6900.0, "2026-11-20", "Pending"),
        (224, 9, "Bar Soap (Carton)", 35, 1450.0, "2026-10-17", "Delivered"),
        (225, 9, "Maize Flour 2kg (Bale)", 22, 1850.0, "2026-11-12", "Delivered"),
        (226, 10, "Maize Flour 2kg (Bale)", 70, 1850.0, "2026-10-11", "Delivered"),
        (227, 10, "Rice 25kg", 35, 3200.0, "2026-11-15", "Delivered"),
        (228, 11, "Cooking Oil 20L", 25, 3800.0, "2026-11-08", "Pending"),
        (229, 12, "Cooking Oil 20L", 40, 3800.0, "2026-10-20", "Delivered"),
        (230, 12, "Wheat Flour 2kg (Bale)", 30, 1950.0, "2026-11-17", "Delivered"),
    ]

    cur.executemany(
        "INSERT INTO customers (customer_id, customer_name, county, account_tier) VALUES (?, ?, ?, ?);",
        customers_data,
    )
    cur.executemany(
        """
        INSERT INTO orders (
            order_id, customer_id, product, quantity, unit_price, order_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        orders_data,
    )

    conn.commit()
    conn.close()


def get_county_report(
    county: str,
    start_date: str,
    end_date: str,
    db_path: str = DB_PATH,
) -> pd.DataFrame:
    """Return product sales summary for a given county and inclusive date range (YYYY-MM-DD)."""
    sql = """
    SELECT
        o.product,
        COUNT(o.order_id) AS total_orders,
        SUM(o.quantity) AS total_quantity,
        ROUND(SUM(o.quantity * o.unit_price), 2) AS total_revenue_kes
    FROM orders o
    INNER JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE LOWER(TRIM(c.county)) = LOWER(TRIM(?))
      AND DATE(o.order_date) >= DATE(?)
      AND DATE(o.order_date) <= DATE(?)
      AND o.status != 'Cancelled'
    GROUP BY o.product
    ORDER BY total_revenue_kes DESC, total_quantity DESC;
    """

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn, params=[county, start_date, end_date])
    finally:
        conn.close()

    if df.empty:
        return pd.DataFrame(columns=REPORT_COLUMNS)

    return df[REPORT_COLUMNS]


def _display_report(label: str, county: str, start_date: str, end_date: str) -> None:
    df = get_county_report(county, start_date, end_date)
    print(f"\n=== {label} ({county} | {start_date} to {end_date}) ===")
    if df.empty:
        print("No matching orders found for this county and date range.")
        print(df.to_string(index=False))
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":
    init_sample_database()

    _display_report("Test 1: Nairobi November 2026", "Nairobi", "2026-11-01", "2026-11-30")
    _display_report("Test 2: Mombasa Oct-Nov 2026", "Mombasa", "2026-10-01", "2026-11-30")
    _display_report("Test 3: Kisumu October 2026", "Kisumu", "2026-10-01", "2026-10-31")
    _display_report("Test 4: No Results Case", "Uasin Gishu", "2026-12-01", "2026-12-31")