# Six-Month NGO Nutrition Program Outcomes — Donor Storytelling Dashboard

A Streamlit dashboard and donor-storytelling project for reviewing six-month child nutrition outcomes across Kajiado, Kilifi, and Kisumu. Each finding pairs a chart with plain-language context: **Expectation → What Happened → Why It Matters**.

> **Important:** The current application generates demonstration data. The figures below describe that sample, not verified clinical outcomes. Replace and validate the data before using the findings in donor or operational decisions.

## Features

- **Three Finding KPIs:** See the leading county, the relationship between session attendance and weight gain, and the leading age group.
- **Interactive Filters:** Filter by county, age group, and sessions attended. The KPIs and charts update to the selected records.
- **Donor-Ready Charts:** View county averages, session attendance versus weight gain, and age-group outcomes.
- **Narrative Context:** Review the expectation, observed sample result, and potential follow-up for each finding.
- **Sample Data and Brief:** Generate a 180-participant dataset, chart PNGs, and a `DONOR_HEADLINES.md` summary.

## Project Structure

- `nutrition.py` — Streamlit dashboard, sample-data generator, chart creation, and donor-headline summary.
- `ngo_nutrition_outcomes.csv` — Generated 180-participant demonstration dataset.
- `chart1_county_performance.png` — Horizontal county comparison chart.
- `chart2_attendance_vs_weight_gain.png` — Attendance and weight-gain scatter plot with trend line when the selected data supports it.
- `chart3_age_group_outcomes.png` — Ordered age-group comparison chart.
- `DONOR_HEADLINES.md` — Generated plain-language headlines and a pricing note.
- `nutrition.md` — Project documentation.

## Sample Data Format

The generated CSV contains these columns:

| Column | Description | Example |
| --- | --- | --- |
| `participant_id` | Synthetic participant identifier | `NUT-001` |
| `county` | County of participation | `Kisumu` |
| `age_group` | Age group at enrollment | `6-23 months` |
| `sessions_attended` | Nutrition sessions attended | `10` |
| `months_in_program` | Months in the program | `6` |
| `weight_gain_kg` | Weight gain over the sample period, in kilograms | `3.60` |

The current script creates this dataset on each run and writes it to `ngo_nutrition_outcomes.csv`. It does not currently load or upload real program records.

## Key Headlines & Narrative Context

### 1. County Performance

**Kisumu children gained the most weight over six months, showing that local delivery practices matter as much as attendance.**

- **Chart:** `chart1_county_performance.png`, a horizontal bar chart with a dashed average benchmark.
- **Expectation:** All three counties were expected to achieve broadly similar gains because they received the same nutrition ration and curriculum.
- **What happened in the sample:** Kisumu averaged **3.58 kg**, Kajiado **3.24 kg**, and Kilifi **2.73 kg**, against an overall sample average of about **3.18 kg**. Kisumu families attended slightly fewer sessions on average than Kajiado families, while Kilifi and Kisumu attendance was similar.
- **Why it matters:** The sample suggests reviewing local delivery practices and testing what may be transferable to lower-performing sites, rather than assuming session counts alone explain the differences.

### 2. Session Attendance and Outcomes

**Children whose families stayed consistent with sessions gained noticeably more weight than those who missed visits.**

- **Chart:** `chart2_attendance_vs_weight_gain.png`, a scatter plot with a fitted trend line when there is enough variation in session counts.
- **Expectation:** Program staff expected some benefit even when families attended intermittently.
- **What happened in the sample:** Sessions attended and weight gain have a positive correlation (**r = 0.67**). Participants attending 10 or more sessions averaged **3.74 kg**, compared with **2.48 kg** for those attending 6 or fewer.
- **Why it matters:** The pattern can help guide follow-up questions about reminders, transport support, or community health worker outreach. Correlation alone does not establish that attendance caused the weight-gain difference.

### 3. Age-Group Differences

**Toddlers under two responded more strongly to the program than school-age children in the sample.**

- **Chart:** `chart3_age_group_outcomes.png`, an ordered column chart comparing mean weight gain by enrollment age group.
- **Expectation:** Stakeholders may expect older children to gain more absolute weight because they are larger at enrollment.
- **What happened in the sample:** Children enrolled at 6–23 months averaged **3.60 kg**, compared with **3.19 kg** for ages 24–59 months and **2.76 kg** for ages 5–12 years.
- **Why it matters:** The sample supports examining age-specific needs and early intervention priorities with validated program data, while tailoring nutrition support for older children.

## Questions for Phase 2 Data Collection

1. What were each child's baseline weight and MUAC measurements at enrollment?
2. Were rations in lower-performing sites shared across household members or affected by seasonal illness?
3. What was the total program delivery cost per child in each county?

## Pricing Note

Proposed pricing for a six-month NGO program evaluation and donor briefing:

- **KES 50,000–85,000** one-time for data cleaning and validation, cohort analysis, three donor-ready charts with narrative context, an executive briefing memo, and a 30-minute preparation walkthrough.

This is a proposed service estimate, not a charge or feature implemented by the application.

## Installation & Setup

### Prerequisites

- Python 3 installed on your system.
- Streamlit, Pandas, NumPy, and Matplotlib.

Install the required packages:

```powershell
python -m pip install streamlit pandas numpy matplotlib
```

## Usage

From the project directory, start the dashboard with:

```powershell
streamlit run nutrition.py
```

Use the sidebar to select counties, age groups, and a session-count range. The KPIs, chart images, and narrative summaries update for the filtered sample. If a selection returns no participants, widen the filters.

## Dashboard Overview

```text
County | Age Group | Sessions Attended filters
County Performance KPI | Attendance/Outcome KPI | Age-Group KPI
County comparison | Attendance vs. weight gain
Age-group comparison
Expectation → What Happened → Why It Matters context
```