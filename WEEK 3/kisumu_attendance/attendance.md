## Kisumu Attendance vs. Classrooms Analysis

A lightweight Python data analysis script built for education officials to clean and merge Kisumu County school attendance and infrastructure datasets, evaluate whether schools with more classrooms have higher average attendance rates, and generate a correlation summary and scatter plot.

## Features

- Name Standardization: Normalizes school names across files by handling casing, punctuation, abbreviations (`pri` / `sec`), and extra spacing.
- Deduplication & Missing-Value Filtering: Removes duplicate entries and drops incomplete rows missing attendance or classroom counts before analysis.
- Correlation Analysis: Computes both Pearson and Spearman correlation coefficients on merged school records.
- Scatter Plot Visualization: Saves a trendline scatter plot (`attendance_vs_classrooms.png`) comparing classroom counts against average attendance rates.

## Project Structure

- `attendance.py` — analysis and plotting script
- `attendance_vs_classrooms.png` — generated scatter plot
- `attendance.md` — project documentation

## Report Finding

Across Kisumu County schools with complete paired records, a higher number of classrooms is strongly associated with higher average student attendance rates (Pearson *r* = 0.99 across seven schools ranging from 6 to 18 classrooms).

## Installation

Install Python 3.7 or later, then install the required packages:

```bash
python -m pip install pandas numpy matplotlib
```

## Usage

From the `kisumu_attendance` directory, run:

```bash
python attendance.py
```

The script prints the cleaned records and correlation coefficients, then saves
`attendance_vs_classrooms.png` in the current working directory. Spearman
correlation is calculated from the ranked columns, so SciPy is not required.

## Example Output

The table formatting may vary depending on the console and pandas version. The
correlation results and final message should look like this:

```text
Pearson correlation (r): 0.9915
Spearman correlation (rho): 1.0000

Saved scatter plot to attendance_vs_classrooms.png
```

## Finding for the Officer's Report
Across Kisumu County schools with complete paired records, a higher number of classrooms is strongly associated with higher average student attendance rates (Pearson r = 0.99 across seven schools ranging from 6 to 18 classrooms).