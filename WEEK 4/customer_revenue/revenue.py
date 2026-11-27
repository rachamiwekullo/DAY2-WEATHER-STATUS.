import sqlite3
import pandas as pd

DB_PATH = "distributor_customers_orders.db"


def setup_database(db_path: str = DB_PATH) -> None:
    """Create and populate related customers and orders tables in SQLite."""
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
        # Kamau Stores (customer_id=1) -> 5 orders
        (201, 1, "Cooking Oil 20L", 40, 3800.0, "2026-10-03", "Delivered"),
        (202, 1, "Rice 25kg", 30, 3200.0, "2026-10-14", "Delivered"),
        (203, 1, "Maize Flour 2kg (Bale)", 50, 1850.0, "2026-10-27", "Delivered"),
        (204, 1, "Cooking Oil 20L", 35, 3800.0, "2026-11-05", "Delivered"),
        (205, 1, "Sugar 50kg", 20, 6900.0, "2026-11-16", "Delivered"),
        # Westlands Provision (customer_id=2) -> 4 orders
        (206, 2, "Rice 25kg", 55, 3200.0, "2026-10-06", "Delivered"),
        (207, 2, "Bar Soap (Carton)", 45, 1450.0, "2026-10-19", "Delivered"),
        (208, 2, "Tea Leaves 500g (Carton)", 25, 4200.0, "2026-11-04", "Delivered"),
        (209, 2, "Rice 25kg", 30, 3200.0, "2026-11-18", "Delivered"),
        # Eastleigh Superstore (customer_id=3) -> 2 orders
        (210, 3, "Tea Leaves 500g (Carton)", 30, 4200.0, "2026-10-12", "Delivered"),
        (211, 3, "Wheat Flour 2kg (Bale)", 40, 1950.0, "2026-11-09", "Pending"),
        # South B Wholesalers (customer_id=4) -> 1 order
        (212, 4, "Maize Flour 2kg (Bale)", 65, 1850.0, "2026-11-21", "Delivered"),
        # Hassan Traders (customer_id=5) -> 4 orders
        (213, 5, "Rice 25kg", 40, 3200.0, "2026-10-08", "Delivered"),
        (214, 5, "Sugar 50kg", 22, 6900.0, "2026-10-22", "Delivered"),
        (215, 5, "Cooking Oil 20L", 28, 3800.0, "2026-11-07", "Delivered"),
        (216, 5, "Bar Soap (Carton)", 50, 1450.0, "2026-11-19", "Delivered"),
        # Pwani Mart (customer_id=6) -> 2 orders
        (217, 6, "Maize Flour 2kg (Bale)", 50, 1850.0, "2026-10-15", "Delivered"),
        (218, 6, "Rice 25kg", 20, 3200.0, "2026-11-11", "Pending"),
        # Kilindini Distributors (customer_id=7) -> 1 order
        (219, 7, "Sugar 50kg", 18, 6900.0, "2026-11-14", "Pending"),
        # Otieno Wholesale (customer_id=8) -> 4 orders
        (220, 8, "Sugar 50kg", 20, 6900.0, "2026-10-09", "Delivered"),
        (221, 8, "Cooking Oil 20L", 30, 3800.0, "2026-10-25", "Delivered"),
        (222, 8, "Maize Flour 2kg (Bale)", 40, 1850.0, "2026-11-06", "Delivered"),
        (223, 8, "Sugar 50kg", 15, 6900.0, "2026-11-20", "Pending"),
        # Kondele Mini Mart (customer_id=9) -> 2 orders
        (224, 9, "Bar Soap (Carton)", 35, 1450.0, "2026-10-17", "Delivered"),
        (225, 9, "Maize Flour 2kg (Bale)", 22, 1850.0, "2026-11-12", "Delivered"),
        # Eldoret Central Stores (customer_id=10) -> 2 orders
        (226, 10, "Maize Flour 2kg (Bale)", 70, 1850.0, "2026-10-11", "Delivered"),
        (227, 10, "Rice 25kg", 35, 3200.0, "2026-11-15", "Delivered"),
        # Uasin Gishu Depot (customer_id=11) -> 1 order
        (228, 11, "Cooking Oil 20L", 25, 3800.0, "2026-11-08", "Pending"),
        # Thika Road Mart (customer_id=12) -> 2 orders
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


def run_queries(db_path: str = DB_PATH) -> None:
    """Execute the three customer revenue and county concentration queries with pandas."""
    conn = sqlite3.connect(db_path)

    query_1_join = """
    SELECT
        o.order_id,
        o.order_date,
        c.customer_name,
        c.county,
        c.account_tier,
        o.product,
        o.quantity,
        o.unit_price,
        ROUND(o.quantity * o.unit_price, 2) AS order_total_kes,
        o.status
    FROM orders o
    INNER JOIN customers c
        ON o.customer_id = c.customer_id
    ORDER BY o.order_id;
    """

    query_2_frequent_customers = """
    SELECT
        c.customer_id,
        c.customer_name,
        c.county,
        c.account_tier,
        COUNT(o.order_id) AS order_count,
        ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend_kes
    FROM customers c
    INNER JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE o.status != 'Cancelled'
    GROUP BY c.customer_id, c.customer_name, c.county, c.account_tier
    HAVING COUNT(o.order_id) > 3
    ORDER BY total_spend_kes DESC;
    """

    query_3_top_per_county = """
    WITH county_customer_spend AS (
        SELECT
            c.county,
            c.customer_id,
            c.customer_name,
            c.account_tier,
            COUNT(o.order_id) AS order_count,
            ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend_kes,
            RANK() OVER (
                PARTITION BY c.county
                ORDER BY SUM(o.quantity * o.unit_price) DESC
            ) AS spend_rank
        FROM customers c
        INNER JOIN orders o
            ON c.customer_id = o.customer_id
        WHERE o.status != 'Cancelled'
        GROUP BY c.county, c.customer_id, c.customer_name, c.account_tier
    )
    SELECT
        county,
        customer_name AS top_customer,
        account_tier,
        order_count,
        total_spend_kes
    FROM county_customer_spend
    WHERE spend_rank = 1
    ORDER BY total_spend_kes DESC;
    """

    results = [
        ("1. Orders Joined with Customer Account Tier", query_1_join),
        ("2. Total Spend per Customer (More Than 3 Orders)", query_2_frequent_customers),
        ("3. Top Customer per County (Window Function)", query_3_top_per_county),
    ]

    for title, sql in results:
        print(f"\n=== {title} ===")
        df = pd.read_sql_query(sql, conn)
        print(df.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    setup_database()
    run_queries()