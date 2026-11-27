# SACCO Loan Portfolio 90-Day Repayment Analysis

A lightweight Python data analysis script built for SACCO credit teams to clean and merge loan disbursement and repayment tables across quarters and regions, calculate quarterly 90-day full repayment rates, and generate visual reports for portfolio review.

## Features

- **Data Cleaning & Merging:** Standardizes inconsistent column names, trims whitespace, normalizes loan IDs, and merges loan issuance records with repayment status records.
- **Calculated Portfolio Metrics:** Derives issue quarters (`YYYYQn`), 90-day full repayment flags, and loan size tiers (`Under 100k KES` vs. `100k+ KES`).
- **Quarterly Repayment Summary:** Outputs a structured quarterly table tracking loans issued, loans fully repaid within 90 days, 90-day repayment percentage, and total disbursed amount.
- **Three Targeted Charts:** Generates three PNG charts answering specific questions on quarterly repayment rates, regional performance, and loan size outcomes.

## Project Structure

- `sacco_loan_portfolio_analysis.py`          # Main data cleaning, analysis, and visualization script
- `chart1_quarterly_90day_repayment_rate.png` # Chart 1: 90-day repayment percentage by issue quarter
- `chart2_region_90day_repayment_rate.png`    # Chart 2: 90-day repayment rate comparison across regions
- `chart3_loan_amount_vs_90day_outcome.png`   # Chart 3: Loan amounts over time by 90-day repayment outcome
- `README.md`                                 # Project documentation

## Quarterly Repayment Rate Table

| Issue Quarter | Total Loans Issued | Fully Repaid Within 90 Days | 90-Day Repayment Rate (%) | Total Disbursed (KES) |
| :--- | :---: | :---: | :---: | :---: |
| `2025Q3` | 4 | 3 | 75.0% | 340,000 |
| `2025Q4` | 4 | 2 | 50.0% | 395,000 |
| `2026Q1` | 4 | 3 | 75.0% | 430,000 |
| `2026Q2` | 4 | 1 | 25.0% | 485,000 |

## Recommendation

Introduce a structured borrower reminder and flexible installment check-in at **day 60**—especially for loans of KES 100,000 or more and branches experiencing slower collections—so members can clear balances before the 90-day window closes.

## Findings Summary

Across the four quarters reviewed, the share of SACCO loans fully repaid within 90 days ranged from a high of 75.0% in Q3 2025 and Q1 2026 down to 25.0% in Q2 2026. Larger loan amounts and later quarters saw a smaller share of loans paid off completely within the 90-day window. Differences between the two regions also showed that timing and repayment pace vary by local branch activity. Checking in with borrowers before day 90 can help keep repayment rates steady even as total lending grows.

## Installation & Setup

### Prerequisites

- Python 3.7+ installed on your system.

### Steps

Clone or download the script files into your target directory.

Install the required packages:

```bash
pip install pandas numpy matplotlib
```

For a project virtual environment on Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install pandas numpy matplotlib
```

## Usage

1. Open a terminal in the project directory.
2. Run the analysis script with Python:

```powershell
python loans.py
```

If `python` is not available on your PATH, run the script with the virtual-environment interpreter:

```powershell
D:\AI DATA ANALYST\.venv\Scripts\python.exe "D:\AI DATA ANALYST\WEEK 3\project\loans.py"
```

The script prints the quarterly summary in the terminal and saves the following PNG files beside `loans.py`:

- `chart1_quarterly_90day_repayment_rate.png`
- `chart2_region_90day_repayment_rate.png`
- `chart3_loan_amount_vs_90day_outcome.png`

## Sample Output

```text
=== Quarterly 90-Day Repayment Rate Table ===
issue_quarter  total_loans_issued  repaid_within_90_days  total_disbursed_kes  repayment_rate_pct
       2025Q3                   4                      3               340000                75.0
       2025Q4                   4                      2               395000                50.0
       2026Q1                   4                      3               430000                75.0
       2026Q2                   4                      1               485000                25.0
```