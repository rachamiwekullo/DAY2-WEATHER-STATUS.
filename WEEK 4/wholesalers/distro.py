import sqlite3
import pandas as pd

DB_PATH = "distributor_orders.db"


def setup_database(db_path: str = DB_PATH) -> None:
    """Create the orders table and populate 22 realistic wholesale distributor rows."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS orders")
    cur.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            county TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    sample_orders = [
        (1001, "Kamau Stores", "Nairobi", "Cooking Oil 20L", 35, 3800.0, "2026-11-02", "Delivered"),
        (1002, "Pwani Mart", "Mombasa", "Maize Flour 2kg (Bale)", 50, 1850.0, "2026-11-02", "Delivered"),
        (1003, "Otieno Wholesale", "Kisumu", "Sugar 50kg", 20, 6900.0, "2026-11-03", "Pending"),
        (1004, "Hassan Traders", "Mombasa", "Rice 25kg", 40, 3200.0, "2026-11-04", "Delivered"),
        (1005, "Rift Valley Grocers", "Nakuru", "Wheat Flour 2kg (Bale)", 45, 1950.0, "2026-11-05", "Delivered"),
        (1006, "Uasin Gishu Depot", "Uasin Gishu", "Cooking Oil 20L", 25, 3800.0, "2026-11-06", "Pending"),
        (1007, "Kilindini Distributors", "Mombasa", "Sugar 50kg", 18, 6900.0, "2026-11-07", "Pending"),
        (1008, "Eastleigh Superstore", "Nairobi", "Tea Leaves 500g (Carton)", 30, 4200.0, "2026-11-08", "Delivered"),
        (1009, "Nyali Cash & Carry", "Mombasa", "Bar Soap (Carton)", 60, 1450.0, "2026-11-09", "Delivered"),
        (1010, "Kondele Mini Mart", "Kisumu", "Maize Flour 2kg (Bale)", 22, 1850.0, "2026-11-10", "Pending"),
        (1011, "Westlands Provision", "Nairobi", "Rice 25kg", 55, 3200.0, "2026-11-11", "Delivered"),
        (1012, "Likoni Retailers", "Mombasa", "Cooking Oil 20L", 12, 3800.0, "2026-11-12", "Pending"),
        (1013, "Naivasha Supply Co", "Nakuru", "Sugar 50kg", 15, 6900.0, "2026-11-13", "Delivered"),
        (1014, "Eldoret Central Stores", "Uasin Gishu", "Maize Flour 2kg (Bale)", 70, 1850.0, "2026-11-14", "Delivered"),
        (1015, "Industrial Area Traders", "Nairobi", "Bar Soap (Carton)", 80, 1450.0, "2026-11-15", "Pending"),
        (1016, "Mtwapa General Stores", "Kilifi", "Wheat Flour 2kg (Bale)", 30, 1950.0, "2026-11-16", "Delivered"),
        (1017, "Bamburi Wholesale", "Mombasa", "Tea Leaves 500g (Carton)", 15, 4200.0, "2026-11-17", "Delivered"),
        (1018, "Thika Road Mart", "Kiambu", "Cooking Oil 20L", 40, 3800.0, "2026-11-18", "Delivered"),
        (1019, "Ruiru Mega Distributors", "Kiambu", "Rice 25kg", 25, 3200.0, "2026-11-19", "Pending"),
        (1020, "Milimani Traders", "Kisumu", "Bar Soap (Carton)", 35, 1450.0, "2026-11-20", "Delivered"),
        (1021, "South B Wholesalers", "Nairobi", "Maize Flour 2kg (Bale)", 65, 1850.0, "2026-11-21", "Delivered"),
        (1022, "Changamwe Depot", "Mombasa", "Wheat Flour 2kg (Bale)", 20, 1950.0, "2026-11-22", "Cancelled"),
    ]

    cur.executemany(
        """
        INSERT INTO orders (
            order_id, customer_name, county, product, quantity, unit_price, order_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_orders,
    )
    conn.commit()
    conn.close()


def run_monday_report(db_path: str = DB_PATH) -> None:
    """Answer all five Monday morning sales manager questions using pandas.read_sql_query."""
    conn = sqlite3.connect(db_path)

    queries = [
        (
            "1. All Orders from Mombasa County",
            """
            SELECT order_id, customer_name, product, quantity, unit_price,
                   (quantity * unit_price) AS total_value_kes, order_date, status
            FROM orders
            WHERE county = 'Mombasa'
            ORDER BY order_date;
            """,
        ),
        (
            "2. Top 10 Orders by Total Value",
            """
            SELECT order_id, customer_name, county, product, quantity, unit_price,
                   (quantity * unit_price) AS total_value_kes, status
            FROM orders
            ORDER BY total_value_kes DESC
            LIMIT 10;
            """,
        ),
        (
            "3. Total Revenue per County (Excluding Cancelled Orders)",
            """
            SELECT county,
                   COUNT(order_id) AS total_orders,
                   SUM(quantity * unit_price) AS total_revenue_kes
            FROM orders
            WHERE status != 'Cancelled'
            GROUP BY county
            ORDER BY total_revenue_kes DESC;
            """,
        ),
        (
            "4. All Pending Orders Over KES 50,000",
            """
            SELECT order_id, customer_name, county, product, quantity, unit_price,
                   (quantity * unit_price) AS total_value_kes, order_date
            FROM orders
            WHERE status = 'Pending'
              AND (quantity * unit_price) > 50000
            ORDER BY total_value_kes DESC;
            """,
        ),
        (
            "5. Three Best-Selling Products by Quantity (Excluding Cancelled Orders)",
            """
            SELECT product,
                   SUM(quantity) AS total_units_sold,
                   SUM(quantity * unit_price) AS total_sales_kes
            FROM orders
            WHERE status != 'Cancelled'
            GROUP BY product
            ORDER BY total_units_sold DESC
            LIMIT 3;
            """,
        ),
    ]

    for title, sql in queries:
        print(f"\n=== {title} ===")
        df = pd.read_sql_query(sql, conn)
        print(df.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    setup_database()
    run_monday_report()