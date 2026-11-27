import sqlite3
import pandas as pd

# Connect to the file you created in DB Browser
conn = sqlite3.connect("sales.db")

# Quick check: print all table names
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
# Expected: [('orders',), ('customers',)]
#If you do not have a saved sales.db file, use sqlite3.connect(":memory:") to create an in-memory database for testing. 
# Add the CREATE TABLE and INSERT statements from Day 16 after connecting.

import sqlite3, pandas as pd

conn = sqlite3.connect("sales.db")

query = """
    SELECT county,
           COUNT(*) AS order_count,
           SUM(total_value) AS total_revenue
    FROM orders
    GROUP BY county
    ORDER BY total_revenue DESC
"""
df = pd.read_sql_query(query, conn)
print(df)
conn.close()
print()


def get_county_orders(conn, county):
    # Safe: the county value is passed separately, never embedded in the string
    query = """
        SELECT customer, product, total_value, status
        FROM orders
        WHERE county = ?
        ORDER BY total_value DESC
    """
    return pd.read_sql_query(query, conn, params=(county,))

conn = sqlite3.connect("sales.db")
print(get_county_orders(conn, "Mombasa"))
print()
print(get_county_orders(conn, "Kisumu"))

print()
conn = sqlite3.connect("sales.db")

# Load, clean, and write back
df = pd.read_sql_query("SELECT * FROM orders", conn)

# Add a calculated column
df['revenue_category'] = df['total_value'].apply(
    lambda x: 'high' if x > 50000 else ('mid' if x > 15000 else 'low')
)

# Write to a new table in the same database
df.to_sql('orders_enriched', conn, if_exists='replace', index=False)
print("Written.")

# Confirm it is there
check = pd.read_sql_query("SELECT * FROM orders_enriched LIMIT 3", conn)
print(check[['customer', 'total_value', 'revenue_category']])
conn.close()