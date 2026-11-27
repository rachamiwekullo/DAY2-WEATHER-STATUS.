# Nakuru School Attendance Monitor

A mobile- and laptop-friendly Streamlit dashboard that helps a school principal monitor daily student attendance, compare class performance, and spot trends over a selected date range.

## Features

- Filter attendance records by date, defaulting to approximately the last 30 calendar days.
- View the overall attendance rate and the best- and worst-attending classes.
- Compare each class's daily attendance in a grouped bar chart.
- Review attendance totals and rates by class.
- Upload an attendance CSV or use generated sample data.

## CSV Format

The app expects a CSV file with these columns:

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| `date` | Date (`YYYY-MM-DD`) | Date of the daily roll call | `2026-11-26` |
| `class_name` | Text | Name or stream of the class | `Form 3 West` |
| `students_present` | Number | Students present on that date | `34` |
| `students_total` | Number | Total students enrolled in the class | `40` |

Include one row per class per date. For example, five class records for a date produce five side-by-side bars for that day. See [attendance.md](./attendance.md) for the full data guide.

## Setup and Usage

Install Python 3 and the required packages:

```bash
python -m pip install streamlit pandas numpy
```

From this folder, start the dashboard:

```bash
streamlit run attendance.py
```

Use the sidebar to upload a CSV. If no file is uploaded, the app reads `nakuru_attendance.csv`; it creates sample data there if the file does not exist.

## Project Structure

- `attendance.py` — Streamlit dashboard
- `attendance.md` — Attendance CSV and data guide
- `nakuru_attendance.csv` — Sample data, generated if missing
