# HR Attendance Monitor (Employee & HR Edition)

A self-service Streamlit dashboard for reviewing staff attendance by department, employee, and date range. It accepts an attendance CSV or generates sample data when no file is uploaded.

## Features

- **CSV Upload:** Upload attendance records from the sidebar.
- **Sample Data:** Generate sample records for 50 employees across 130 working days when no CSV is uploaded.
- **Date, Department, and Employee Filters:** Narrow the dashboard to a selected period, departments, and employees.
- **Attendance Metrics:** Review attendance rate, punctuality rate, staff in view, and absent records.
- **Department Charts:** Compare attendance rates by department and follow daily attendance trends.
- **Employee Analysis:** Review an employee's attendance and punctuality, status counts, and rolling attendance trend.
- **Filtered Records:** Filter the records by status, search by name or staff ID, and optionally limit them to the selected employee.
- **CSV Download:** Export the records currently shown in the filtered records table.

## Project Structure

- `app.py` — Self-contained Streamlit app, including sample-data generation, CSV validation, metric calculations, and dashboard UI.
- `hr.py` — Original data-layer module retained as a backup; `app.py` no longer imports it.
- `hr.md` — Project documentation.
- Uploaded CSV files — Supplied by the user at runtime; no default CSV file is required.

## Expected CSV Format

The uploaded CSV must contain these columns:

| Column Name | Type | Description | Example |
| --- | --- | --- | --- |
| `date` | Date | Date of the attendance record; ISO format is recommended | `2026-11-26` |
| `staff_id` | Text | Unique staff identifier | `EMP001` |
| `name` | Text | Staff member's name | `Alex Example` |
| `department` | Text | Department or team | `Operations` |
| `status` | Text | Attendance status: `Present`, `Late`, `Absent`, or `Leave` | `Present` |

Example:

```csv
date,staff_id,name,department,status
2026-11-26,EMP001,Alex Example,Operations,Present
2026-11-26,EMP002,Jamie Example,Sales,Late
```

Column names are normalized to lowercase, and spaces in column names become underscores. Status values are trimmed and normalized before validation.

## What Each Dashboard Section Shows & Why It Matters

### 1. Data and Filters

The sidebar shows whether the dashboard is using generated sample data or an uploaded CSV. The date range defaults to the full date span in the active data. Department selection defaults to all departments; the employee filter offers employees from the selected departments.

### 2. Attendance Metrics

The top row shows attendance rate, punctuality rate, unique staff in the filtered data, and the number of absent records.

- **Attendance rate:** `(Present + Late) / (Present + Late + Absent)`. Approved leave is excluded from the denominator.
- **Punctuality rate:** `Present / (Present + Late)`. Approved leave is excluded.

Rates show `N/A` when the relevant denominator is zero.

### 3. Department and Daily Charts

The bar chart compares attendance rates across the selected departments. The line chart shows daily attendance across the selected records. Both respond to the date, department, and employee filters.

### 4. Individual Employee

Choose an employee from the filtered data and set a rolling window of 5, 10, 15, or 20 days (10 by default). This section shows that employee's attendance and punctuality rates, late/absent/leave counts, a rolling attendance trend, and a count of records by status. Leave records are skipped in the rolling trend.

### 5. Filtered Attendance Records and Download

The records table starts with the date, department, and employee filters. It can then be narrowed by status, name or staff ID search, and the **Only the employee selected above** toggle. The CSV download contains those same table records with columns `Date`, `Staff ID`, `Employee`, `Department`, and `Status`.

## Data Handling and Access Note

The app checks for the required columns, parseable dates, and recognized statuses. It normalizes column names and text fields, removes duplicate records for the same date and staff ID, and sorts the cleaned data. Invalid CSVs or attendance values are reported in the dashboard.

When no file is uploaded, the app generates synthetic sample data for 50 staff across 130 weekdays. Uploaded files replace the sample data for the current app session; the app does not save uploaded CSVs. Downloads are generated from the currently filtered table.

The department and employee filters are data filters, not account permissions. The app does not authenticate users or restrict access to assigned departments. Do not expose it publicly with real staff records without adding appropriate access controls.

## Commercial Pricing & Billing Model

The app contains proposed setup-tier details for a service sized for up to 50 staff:

- **Core Setup:** KES 25,000 for CSV upload and validation, KPI cards, department charts, individual trends, monthly summaries and CSV export, plus a proposed Streamlit Cloud deployment.
- **Standard + Custom Branding & Schema Mapping:** KES 32,500 for the Core offering plus branding, mapping existing HR/biometric CSV columns, and staff onboarding.
- **Full Setup + Custom Rules & Handover:** KES 40,000 for the Standard offering plus custom rules, report templates, documentation, and training.

These are informational values in the source code, not charges or features implemented by the dashboard. Hosting, deployment, branding, onboarding, and billing must be arranged separately.

## Installation & Setup

### Prerequisites

- Python 3.
- Streamlit, Pandas, and NumPy.

Install the packages:

```powershell
python -m pip install streamlit pandas numpy
```

## Usage

Open a terminal in the project directory and run:

```powershell
streamlit run app.py
```

Upload a CSV from the sidebar, or use the generated sample data. Select the date range, departments, and employees, review the metrics and trends, then filter and download the attendance records.

## Dashboard Overview

```text
CSV Upload or Generated Sample Data
Date Range | Department Filter | Employee Filter
Attendance Rate | Punctuality Rate | Staff in View | Absent Records
Attendance by Department | Daily Attendance Trend
Employee Metrics | Rolling Attendance Trend | Status Breakdown
Filtered Records: Status | Search | Selected Employee
Download Filtered CSV
```