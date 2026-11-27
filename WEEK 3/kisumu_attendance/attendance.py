import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Sample attendance DataFrame (school name, average_attendance_pct, county)
attendance_df = pd.DataFrame(
    {
        "school name": [
            "Ahero Girls High School",
            "Kondele Primary School",
            "Nyamasaria Secondary School",
            "Muhoroni Mixed Day",
            "Rabuor Primary School",
            "Katito High School",
            "Onyuongo Primary School",
            "Kondele Primary School",        # Duplicate row
            "Chiga Primary School",          # Missing attendance value
        ],
        "average_attendance_pct": [
            91.4,
            84.2,
            88.7,
            79.5,
            86.1,
            93.0,
            76.8,
            84.2,
            np.nan,
        ],
        "county": ["Kisumu"] * 9,
    }
)

# 2. Sample infrastructure DataFrame (school_name, num_classrooms, water_access)
# Includes naming inconsistencies (punctuation, casing, abbreviations, spacing)
# and a missing classroom value.
infrastructure_df = pd.DataFrame(
    {
        "school_name": [
            "ahero girls' high school",      # Casing + apostrophe difference
            "Kondele Pri School",            # Abbreviation ("Pri" vs "Primary")
            "Nyamasaria  Sec. School",       # Double space + abbreviation ("Sec.")
            "Muhoroni Mixed Day",
            "Rabuor Primary School",
            "Katito High School",
            "Onyuongo Primary School",
            "Kombewa Mixed Secondary",       # Missing classroom count
        ],
        "num_classrooms": [
            16,
            10,
            14,
            8,
            12,
            18,
            6,
            np.nan,
        ],
        "water_access": [
            True,
            True,
            True,
            False,
            True,
            True,
            False,
            True,
        ],
    }
)


def normalize_school_name(name: str) -> str:
    """Standardize school names for reliable joining."""
    if not isinstance(name, str):
        return ""
    cleaned = name.lower().strip()
    cleaned = re.sub(r"['’.,-]", " ", cleaned)
    cleaned = re.sub(r"\bpri\b", "primary", cleaned)
    cleaned = re.sub(r"\bsec\b", "secondary", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


# 3. Clean & deduplicate
attendance_clean = attendance_df.copy()
attendance_clean["clean_name"] = attendance_clean["school name"].apply(normalize_school_name)
attendance_clean = attendance_clean.drop_duplicates(subset=["clean_name"], keep="first")

infra_clean = infrastructure_df.copy()
infra_clean["clean_name"] = infra_clean["school_name"].apply(normalize_school_name)
infra_clean = infra_clean.drop_duplicates(subset=["clean_name"], keep="first")

# Merge on normalized school name
merged_df = pd.merge(
    attendance_clean[["clean_name", "school name", "county", "average_attendance_pct"]],
    infra_clean[["clean_name", "num_classrooms", "water_access"]],
    on="clean_name",
    how="inner",
)

# Drop rows with missing values in either analysis column
analysis_df = merged_df.dropna(subset=["average_attendance_pct", "num_classrooms"]).copy()
analysis_df["num_classrooms"] = analysis_df["num_classrooms"].astype(int)

# 4. Correlation analysis
pearson_r = analysis_df["num_classrooms"].corr(analysis_df["average_attendance_pct"], method="pearson")
spearman_rho = analysis_df["num_classrooms"].rank().corr(
    analysis_df["average_attendance_pct"].rank(), method="pearson"
)

print("Merged & cleaned records for correlation:")
print(analysis_df[["school name", "county", "num_classrooms", "water_access", "average_attendance_pct"]])
print(f"\nPearson correlation (r): {pearson_r:.4f}")
print(f"Spearman correlation (rho): {spearman_rho:.4f}")

# 5. Scatter plot with linear trendline
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(
    analysis_df["num_classrooms"],
    analysis_df["average_attendance_pct"],
    color="#1f77b4",
    s=70,
    label="Schools (Kisumu County)",
)

slope, intercept = np.polyfit(
    analysis_df["num_classrooms"],
    analysis_df["average_attendance_pct"],
    deg=1,
)
x_line = np.linspace(analysis_df["num_classrooms"].min(), analysis_df["num_classrooms"].max(), 100)
ax.plot(x_line, slope * x_line + intercept, color="#d62728", linestyle="--", label=f"Trendline (r = {pearson_r:.2f})")

for _, row in analysis_df.iterrows():
    ax.annotate(
        row["school name"].split()[0],
        (row["num_classrooms"], row["average_attendance_pct"]),
        textcoords="offset points",
        xytext=(0, 7),
        ha="center",
        fontsize=8,
    )

ax.set_title("Classrooms vs. Average Student Attendance (Kisumu County)")
ax.set_xlabel("Number of Classrooms")
ax.set_ylabel("Average Attendance (%)")
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend()
plt.tight_layout()
plt.savefig("attendance_vs_classrooms.png", dpi=200)
print("\nSaved scatter plot to attendance_vs_classrooms.png")