import os
import pandas as pd


def generate_sample_data():
  """Generates sample CSV files if they do not exist for testing."""
  if not os.path.exists("milk_collection.csv"):
    milk_data = {
        "farmer_name": [
            "Kiprono Koech",
            "Mary Wangui",
            "Juma Omondi",
            "Grace Cheruiyot",
            "Peter Kamau",
            "Fatma Omar",
            "David Kiprotich",
            "Esther Wanjiru",
            "John Otieno",
            "Beatrice Chebet",
            "Samuel Maina",
            "Amina Abdi",
        ],
        "date": [
            "2026-11-01",
            "2026-11-01",
            "2026-11-01",
            "2026-11-02",
            "2026-11-02",
            "2026-11-02",
            "2026-11-03",
            "2026-11-03",
            "2026-11-03",
            "2026-11-04",
            "2026-11-04",
            "2026-11-04",
        ],
        "litres": [
            45.5,
            62.0,
            30.0,
            50.0,
            75.5,
            40.0,
            55.0,
            68.0,
            35.5,
            48.0,
            82.0,
            42.5,
        ],
    }
    pd.DataFrame(milk_data).to_csv("milk_collection.csv", index=False)

  if not os.path.exists("farmer_details.csv"):
    farmer_data = {
        "farmer_name": [
            "Kiprono Koech",
            "Mary Wangui",
            "Juma Omondi",
            "Grace Cheruiyot",
            "Peter Kamau",
            "Fatma Omar",
            "David Kiprotich",
            "Esther Wanjiru",
            "John Otieno",
            "Beatrice Chebet",
            "Samuel Maina",
            "Amina Abdi",
        ],
        "zone": [
            "Rongai",
            "Bahati",
            "Njoro",
            "Rongai",
            "Bahati",
            "Njoro",
            "Rongai",
            "Bahati",
            "Njoro",
            "Rongai",
            "Bahati",
            "Njoro",
        ],
        "payment_rate": [
            45.0,
            48.0,
            46.0,
            45.0,
            48.0,
            46.0,
            45.0,
            48.0,
            46.0,
            45.0,
            48.0,
            46.0,
        ],
    }
    pd.DataFrame(farmer_data).to_csv("farmer_details.csv", index=False)


def process_dairy_report():
  # Ensure mock input files exist for demonstration
  generate_sample_data()

  # 1. Load the two spreadsheets
  milk_df = pd.read_csv("milk_collection.csv")
  farmers_df = pd.read_csv("farmer_details.csv")

  # 2. Merge DataFrames on 'farmer_name'
  merged_df = pd.merge(milk_df, farmers_df, on="farmer_name", how="inner")

  # 3. Calculate payout per record
  merged_df["payout"] = merged_df["litres"] * merged_df["payment_rate"]

  # --- NEW: Print all merged data first before generating summary ---
  print("=" * 105)
  print(" RAW MERGED MILK COLLECTION DATA (ALL RECORDS)")
  print("=" * 105)
  print(merged_df.to_string(index=False, col_space=15))
  print("=" * 105 + "\n")
  # -----------------------------------------------------------------

  # 4. Aggregate totals per farmer within each zone first
  farmer_zone_totals = (
      merged_df.groupby(["zone", "farmer_name"])
      .agg({"litres": "sum", "payout": "sum"})
      .reset_index()
  )

  # 5. Compute total litres and total payout per zone
  zone_summary = (
      farmer_zone_totals.groupby("zone")
      .agg({"litres": "sum", "payout": "sum"})
      .reset_index()
  )
  zone_summary.rename(
      columns={
          "litres": "Total Litres",
          "payout": "Total Payout (KES)",
      },
      inplace=True,
  )

  # 6. Identify the top farmer per zone based on total litres supplied
  top_farmers = (
      farmer_zone_totals.sort_values(["zone", "litres"], ascending=[True, False])
      .groupby("zone")
      .first()
      .reset_index()
  )
  top_farmers = top_farmers[["zone", "farmer_name"]].rename(
      columns={"farmer_name": "Top Farmer"}
  )

  # 7. Merge metrics together for the final clean presentation table
  final_report = pd.merge(zone_summary, top_farmers, on="zone")

  # Format numeric outputs for clear presentation
  final_report["Total Litres"] = final_report["Total Litres"].round(2)
  final_report["Total Payout (KES)"] = final_report["Total Payout (KES)"].apply(
      lambda x: f"KES {x:,.2f}"
  )

  # 8. Print clean summary table
  print("=" * 80)
  print(" NAKURU DAIRY CO-OPERATIVE: MONTHLY ZONE SUMMARY REPORT")
  print("=" * 80)
  print(final_report.to_string(
        index=False, col_space=18, justify="left"))
  print("=" * 80)


if __name__ == "__main__":
  process_dairy_report()