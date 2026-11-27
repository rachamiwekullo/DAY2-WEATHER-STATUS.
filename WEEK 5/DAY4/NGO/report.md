# NGO Nutrition Program Weekly Report

A local Python reporting tool that summarizes nutrition program data, creates three charts, and saves a standalone dated HTML report. It can generate a report immediately and then run every Monday at 07:00 local time.

## Features

- **CSV Input:** Reads program records from `nutrition_program-v2.csv`.
- **Program Metrics:** Calculates total enrollment, total completions, overall completion rate, average nutrition score, and average adherence.
- **Site Comparison:** Ranks sites by completion rate and identifies the leading site.
- **Charts:** Generates site completion rates, nutrition scores over time, and adherence by cohort.
- **Dated HTML Output:** Creates a self-contained HTML report with the charts embedded.
- **Weekly Scheduling:** Generates a report on startup and schedules a run for Monday at 07:00.
- **Logging:** Writes scheduler activity and failures to `report.log`.

## Project Structure

- `monday.py` — Loads data, calculates metrics, creates charts and HTML reports, and starts the weekly schedule.
- `nutrition_program-v2.csv` — Source nutrition program data.
- `charts/` — Generated PNG chart files.
- `report_YYYY-MM-DD.html` — Dated, standalone HTML report generated for a run date.
- `report.log` — Log file used by the scheduled application.
- `requirements.txt` — Python package dependencies.

## Expected CSV Format

The input CSV must contain these columns:

| Column Name | Type | Description | Example |
| --- | --- | --- | --- |
| `period` | Date-like text | Reporting period for the program record; parsed day-first | `06/07/2026` |
| `cohort` | Text | Program cohort | `Cohort A` |
| `site` | Text | Program location | `Eldoret Clinic` |
| `enrolled` | Numeric | Number enrolled for the record | `84` |
| `completed` | Numeric | Number who completed for the record | `66` |
| `nutrition_score` | Numeric | Nutrition score for the record | `71.5` |
| `adherence_pct` | Numeric | Adherence percentage for the record | `82.1` |

Example:

```csv
period,cohort,site,enrolled,completed,nutrition_score,adherence_pct
06/07/2026,Cohort A,Eldoret Clinic,84,66,71.5,82.1
06/07/2026,Cohort B,Kitale Hub,83,75,83.8,79.6
```

The `period` value is parsed with day-first date handling. For example, `06/07/2026` means 6 July 2026.

## What the Report Shows & Why It Matters

### 1. Program Summary

The report displays total enrollments and completions, the overall completion rate, mean nutrition score, mean adherence rate, and the site with the highest completion rate.

The overall completion rate is calculated as total completions divided by total enrollments. Average score and adherence metrics are calculated as means across the CSV records.

### 2. Program Completion Rate by Site

The bar chart compares each site's completion rate, calculated from that site's total completions divided by its total enrollments.

### 3. Average Nutrition Score Over Time

The line chart shows the mean nutrition score for each reporting period, ordered by parsed date.

### 4. Average Adherence Rate by Cohort

The bar chart compares mean adherence percentages across cohorts.

## Data Handling and Access Note

The program checks that all required columns exist, that the CSV has records, and that required fields contain no missing values. It converts the enrollment, completion, nutrition score, and adherence fields to numeric values and requires a positive total enrollment.

The report date determines the generated filename and displayed run timestamp; it does not filter the source records by period. This is a local reporting script and does not provide user authentication, access controls, or hosted deployment.

## Output and Scheduling

Reports are saved beside `monday.py` using the run date, for example `report_2026-11-23.html`. The HTML embeds the chart images, so each report can be opened on its own. The PNG files in `charts/` are also generated and replaced on each run. Running the report again for the same date replaces that date's HTML file.

## Installation & Setup

### Prerequisites

- Python 3.
- The packages listed in `requirements.txt` (`matplotlib`, `pandas`, and `schedule`).

Install the packages from the project directory:

```powershell
python -m pip install -r requirements.txt
```

## Usage

Run the application from the project directory:

```powershell
python monday.py
```

It generates a report immediately, then stays running to check for the scheduled Monday 07:00 run. Press **Ctrl+C** to stop the scheduler.

To generate reports for two specific run dates for testing:

```powershell
python -c "from datetime import datetime; from monday import weekly_job; weekly_job(datetime(2026, 11, 23, 7, 0)); weekly_job(datetime(2026, 11, 30, 7, 0))"
```

This creates `report_2026-11-23.html` and `report_2026-11-30.html` in the project directory.

## Report Workflow

```text
nutrition_program-v2.csv
          |
          v
Validate columns and values
          |
          v
Calculate summary metrics
          |
          +--> Site completion rate chart
          +--> Nutrition score trend chart
          +--> Cohort adherence chart
          |
          v
Embed charts and write dated HTML report
          |
          v
Log scheduled run to report.log
```