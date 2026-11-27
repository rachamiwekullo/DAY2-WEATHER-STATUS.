import sqlite3, pandas as pd

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE sales (id INTEGER, product TEXT, category TEXT, revenue REAL, month TEXT)")
conn.executemany("INSERT INTO sales VALUES (?,?,?,?,?)", [
    (1,"Maize Flour","Food",8500,"Jan"),(2,"Beans","Food",6200,"Jan"),
    (3,"Cooking Oil","Food",12000,"Feb"),(4,"Phone Case","Electronics",3500,"Feb")
])
conn.commit()

query = """
SELECT category, COUNT(*) as orders, SUM(revenue) as total, AVG(revenue) as avg_order
FROM sales GROUP BY category ORDER BY total DESC
"""
df = pd.read_sql_query(query, conn)
print("Sales by Category:")
print(df.to_string(index=False))
conn.close()