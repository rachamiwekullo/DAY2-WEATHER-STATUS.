import matplotlib.pyplot as plt  # pyright: ignore[reportMissingModuleSource]
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 1. Dataset: Two related SACCO tables across multiple quarters & two regions
#    (loans_df + repayments_df, with messy column names & whitespace/casing)
# ---------------------------------------------------------------------------
loans_raw = pd.DataFrame(
    {
        " Loan ID ": [
            "LN-101", "LN-102", "LN-103", "LN-104",
            "LN-105", "LN-106", "LN-107", "LN-108",
            "LN-109", "LN-110", "LN-111", "LN-112",
            "LN-113", "LN-114", "LN-115", "LN-116",
        ],
        "Member Name": [
            "Amina Otieno", "Brian Kiprop", "Caroline Wanjiku", "David Ochieng",
            "Esther Chebet", "Felix Kamau", "Grace Akinyi", "Hassan Mwangi",
            "Irene Nyambura", "Joseph Koech", "Kevin Ouma", "Lilian Mutua",
            "Martin Barasa", "Nancy Jepchirchir", "Oscar Omondi", "Patricia Njeri",
        ],
        "Region": [
            "Rift Valley", "Rift Valley", "Nyanza", "Nyanza",
            "Rift Valley", "Nyanza", "Rift Valley", "Nyanza",
            "Rift Valley", "Nyanza", "Rift Valley", "Nyanza",
            "Rift Valley", "Nyanza", "Rift Valley", "Nyanza",
        ],
        "Loan Amount (KES)": [
            60000, 85000, 75000, 120000,
            95000, 110000, 70000, 120000,
            80000, 105000, 90000, 155000,
            100000, 130000, 115000, 140000,
        ],
        "issue_date_str": [
            "2025-07-10", "2025-07-22", "2025-08-05", "2025-09-14",
            "2025-10-04", "2025-10-19", "2025-11-11", "2025-12-08",
            "2026-01-12", "2026-01-29", "2026-02-17", "2026-03-21",
            "2026-04-06", "2026-04-25", "2026-05-15", "2026-06-18",
        ],
    }
)

repayments_raw = pd.DataFrame(
    {
        "loan_id": [
            "LN-101", "LN-102", "LN-103", "LN-104",
            "LN-105", "LN-106", "LN-107", "LN-108",
            "LN-109", "LN-110", "LN-111", "LN-112",
            "LN-113", "LN-114", "LN-115", "LN-116",
        ],
        "Repayment Status": [
            "Fully Repaid", "Fully Repaid", "Fully Repaid", "Active",
            "Fully Repaid", "Fully Repaid", "Active", "Overdue",
            "Fully Repaid", "Fully Repaid", "Fully Repaid", "Active",
            "Fully Repaid", "Active", "Active", "Overdue",
        ],
        "days_to_full_repayment": [
            45, 72, 61, np.nan,
            58, 84, np.nan, np.nan,
            50, 68, 79, np.nan,
            64, np.nan, np.nan, np.nan,
        ],
    }
)

# ---------------------------------------------------------------------------
# 2. Clean, merge, and transform
# ---------------------------------------------------------------------------
loans_clean = loans_raw.rename(
    columns={
        " Loan ID ": "loan_id",
        "Member Name": "member_name",
        "Region": "region",
        "Loan Amount (KES)": "loan_amount_kes",
        "issue_date_str": "issue_date",
    }
).copy()

repayments_clean = repayments_raw.rename(
    columns={"Repayment Status": "repayment_status"}
).copy()

loans_clean["loan_id"] = loans_clean["loan_id"].astype(str).str.strip().str.upper()
repayments_clean["loan_id"] = repayments_clean["loan_id"].astype(str).str.strip().str.upper()
loans_clean["region"] = loans_clean["region"].astype(str).str.strip()
repayments_clean["repayment_status"] = repayments_clean["repayment_status"].astype(str).str.strip()
loans_clean["issue_date"] = pd.to_datetime(loans_clean["issue_date"])

df = pd.merge(loans_clean, repayments_clean, on="loan_id", how="inner")

# Calculated columns needed for analysis
df["issue_quarter"] = df["issue_date"].dt.to_period("Q").astype(str)
df["repaid_within_90_days"] = (
    (df["repayment_status"] == "Fully Repaid")
    & (df["days_to_full_repayment"].notna())
    & (df["days_to_full_repayment"] <= 90)
)
df["repaid_within_90_flag"] = df["repaid_within_90_days"].astype(int)
df["loan_size_tier"] = np.where(df["loan_amount_kes"] >= 100000, "100k+ KES", "Under 100k KES")

# Deliverable 1: Quarterly repayment rate table
quarterly_summary = (
    df.groupby("issue_quarter", as_index=False)
    .agg(
        total_loans_issued=("loan_id", "count"),
        repaid_within_90_days=("repaid_within_90_flag", "sum"),
        total_disbursed_kes=("loan_amount_kes", "sum"),
    )
)
quarterly_summary["repayment_rate_pct"] = (
    quarterly_summary["repaid_within_90_days"] / quarterly_summary["total_loans_issued"] * 100
).round(1)

print("=== Quarterly 90-Day Repayment Rate Table ===")
print(quarterly_summary.to_string(index=False))

# ---------------------------------------------------------------------------
# 3. Produce at least three charts (each answering one specific question)
# ---------------------------------------------------------------------------

# Chart 1: What percentage of loans issued in each quarter are fully repaid within 90 days?
fig, ax = plt.subplots(figsize=(8, 4.8))
bars = ax.bar(
    quarterly_summary["issue_quarter"],
    quarterly_summary["repayment_rate_pct"],
    color="#1f77b4",
    width=0.55,
)
ax.set_title("Q1: Share of Issued Loans Fully Repaid Within 90 Days by Quarter")
ax.set_xlabel("Issue Quarter")
ax.set_ylabel("Repaid Within 90 Days (%)")
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle=":", alpha=0.6)
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig("chart1_quarterly_90day_repayment_rate.png", dpi=200)
plt.close()

# Chart 2: How does the 90-day repayment rate compare across the two regions by quarter?
region_qtr = (
    df.groupby(["issue_quarter", "region"], as_index=False)["repaid_within_90_flag"]
    .mean()
    .assign(rate_pct=lambda g: g["repaid_within_90_flag"] * 100)
    .pivot(index="issue_quarter", columns="region", values="rate_pct")
)
fig, ax = plt.subplots(figsize=(8, 4.8))
region_qtr.plot(kind="bar", ax=ax, color=["#2ca02c", "#ff7f0e"], width=0.6)
ax.set_title("Q2: 90-Day Repayment Rate by Region Across Quarters")
ax.set_xlabel("Issue Quarter")
ax.set_ylabel("Repaid Within 90 Days (%)")
ax.set_ylim(0, 110)
ax.legend(title="Region")
ax.grid(axis="y", linestyle=":", alpha=0.6)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("chart2_region_90day_repayment_rate.png", dpi=200)
plt.close()

# Chart 3: How does loan size relate to whether a loan is repaid within 90 days?
fig, ax = plt.subplots(figsize=(8, 4.8))
repaid_90 = df[df["repaid_within_90_days"]]
not_repaid_90 = df[~df["repaid_within_90_days"]]

ax.scatter(
    repaid_90["issue_date"],
    repaid_90["loan_amount_kes"],
    color="#1f77b4",
    s=75,
    label="Fully Repaid <= 90 Days",
)
ax.scatter(
    not_repaid_90["issue_date"],
    not_repaid_90["loan_amount_kes"],
    color="#d62728",
    marker="x",
    s=80,
    label="Not Repaid Within 90 Days",
)
ax.set_title("Q3: Loan Amounts Over Time by 90-Day Repayment Outcome")
ax.set_xlabel("Loan Issue Date")
ax.set_ylabel("Loan Amount (KES)")
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend()
plt.tight_layout()
plt.savefig("chart3_loan_amount_vs_90day_outcome.png", dpi=200)
plt.close()