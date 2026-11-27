# Nakuru Dairy Co-op Monthly Zone Summary Tool

A lightweight Python script utilizing **Pandas** to process dairy collection records, merge them with farmer profiles, and generate a clean monthly summary grouped by geographic zone.

## Features
- **Data Merging:** Combines daily milk collections with static farmer registry records using an inner join on `farmer_name`.
- **Financial Calculation:** Multiplies total volume delivered by individual zone payment rates to compute total payouts (KES).
- **Zone Pivot & Analytics:** Computes total volume and total payout per zone while dynamically pinpointing the top-performing farmer in each zone.

## Required Input Files

The script expects two CSV files to be present in the working directory:

1. **`milk_collection.csv`**
   - Contains daily transaction logs.
   - **Columns:** `farmer_name` (string), `date` (YYYY-MM-DD), `litres` (float)

2. **`farmer_details.csv`**
   - Contains metadata for registered cooperative members.
   - **Columns:** `farmer_name` (string), `zone` (string - e.g., Rongai, Bahati, Njoro), `payment_rate` (float - KES per litre)

*(Note: If these files do not exist when you first run the script, sample data will automatically be generated for demonstration purposes.)*

## Usage

1. Ensure Python and Pandas are installed:
   ```bash
   pip install pandas
   ```