# Automated Weekly County Sales Report

A lightweight Python and SQLite reporting script that summarizes product orders, quantities, and revenue for a selected county and inclusive date range. It replaces a recurring manual query-and-export task with a consistent report for Monday morning operations reviews.

## Features

- **Customer and Order Data:** Uses related `customers` and `orders` tables from `distributor_customers_orders.db`.
- **County and Date Filters:** Selects orders for the requested county and date range. County matching ignores capitalization and surrounding whitespace.
- **Product Summary:** Reports order count, quantity sold, and revenue in KES for each product.
- **Parameterized SQL:** Passes county and dates through `?` placeholders and Pandas' `params` argument.
- **Cancellation Handling:** Excludes orders with `Cancelled` status. Pending orders are included in the totals.
- **Empty-Result Handling:** Returns an empty DataFrame with the same four report columns when no orders match.

## Project Structure

- `report.py`                         # Defines get_county_report, seeds sample data, and demonstrates report calls
- `distributor_customers_orders.db`   # SQLite database used by the report
- `county_report.md`                  # Project documentation

## What the Report Shows & Why the Operations Manager Cares

### Product Summary for a County and Date Range

For each product with matching orders, the report returns:

| Column | Meaning |
| :--- | :--- |
| `product` | Product name |
| `total_orders` | Number of matching orders |
| `total_quantity` | Total units ordered |
| `total_revenue_kes` | Sum of quantity multiplied by unit price, in KES |

This gives operations and sales teams a consistent view of county-level product demand and order value. It can support Monday sales reviews, stock planning, and comparisons between counties or reporting periods.

## Recommendation

Use the same inclusive start and end dates for each county being compared, and review pending orders separately before treating the reported revenue as realized sales. The report excludes cancelled orders but includes pending ones.

## Findings Summary

The bundled sample data contains 12 customers and 30 orders across five counties. Running the included examples produces product summaries for Nairobi, Mombasa, and Kisumu, plus an empty result for a date window with no matching orders. The empty result retains the standard report columns, making it straightforward to handle in downstream exports or workflows.

## Pricing & Business Value Note

Automating the weekly manual query-and-export routine saves operations and sales staff recurring time, reduces copy-paste and date-filter mistakes before Monday briefings, and keeps reported figures consistent across machines. The estimated setup value is **KES 35,000–60,000**, with optional monthly support.

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

Run the included examples from the county report directory:

```powershell
python report.py
```

The script initializes the sample database before printing its examples. **This initialization drops and recreates the `customers` and `orders` tables with the bundled sample data.** To use an existing distributor database without resetting it, import and call the function instead:

```python
from report import get_county_report

df = get_county_report("Nairobi", "2026-11-01", "2026-11-30")
print(df.to_string(index=False))
```

The optional fourth argument can specify another SQLite database path:

```python
df = get_county_report(
    "Nairobi",
    "2026-11-01",
    "2026-11-30",
    db_path="path/to/distributor_customers_orders.db",
)
```

## Sample Output

```text
=== Test 1: Nairobi November 2026 (Nairobi | 2026-11-01 to 2026-11-30) ===
                 product  total_orders  total_quantity  total_revenue_kes
             Sugar 50kg             1              20           138000.0
         Cooking Oil 20L             1              35           133000.0
Maize Flour 2kg (Bale)             1              65           120250.0
Tea Leaves 500g (Carton)            1              25           105000.0
               Rice 25kg             1              30            96000.0
Wheat Flour 2kg (Bale)             1              40            78000.0

=== Test 4: No Results Case (Uasin Gishu | 2026-12-01 to 2026-12-31) ===
Empty DataFrame
Columns: [product, total_orders, total_quantity, total_revenue_kes]
Index: []
```