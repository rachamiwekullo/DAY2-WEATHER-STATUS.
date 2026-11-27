from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Nakuru School Attendance Monitor",
    page_icon="",
    layout="wide",
)

DEFAULT_CSV_PATH = Path("nakuru_attendance.csv")
REQUIRED_COLUMNS = ["date", "class_name", "students_present", "students_total"]


def generate_sample_attendance_csv(csv_path: Path = DEFAULT_CSV_PATH) -> pd.DataFrame:
    """Create a realistic 9-week (45 school day) sample CSV across 5 classes."""
    rng = np.random.default_rng(2026)
    dates = pd.bdate_range(end="2026-11-26", periods=45)
    classes = [
        "Form 1 East",
        "Form 2 North",
        "Form 3 West",
        "Form 4 South",
        "Grade 8 Central",
    ]
    base_rates = {
        "Form 1 East": 94.5,
        "Form 2 North": 91.0,
        "Form 3 West": 88.5,
        "Form 4 South": 92.5,
        "Grade 8 Central": 89.0,
    }
    class_sizes = {
        "Form 1 East": 44,
        "Form 2 North": 42,
        "Form 3 West": 40,
        "Form 4 South": 38,
        "Grade 8 Central": 45,
    }

    rows = []
    n_days = len(dates)
    for i, dt in enumerate(dates):
        for cls in classes:
            total = class_sizes[cls]
            rate = base_rates[cls] + float(rng.normal(0, 1.6))

            # Simulate a steady decline in Form 3 West over the last ~30 days
            if cls == "Form 3 West" and i >= n_days - 22:
                days_in_decline = i - (n_days - 22) + 1
                rate -= days_in_decline * 0.65

            if dt.dayofweek in (0, 4):
                rate -= 1.0

            rate = float(np.clip(rate, 68.0, 99.0))
            present = int(np.clip(round((rate / 100.0) * total), 1, total))

            rows.append(
                {
                    "date": dt.strftime("%Y-%m-%d"),
                    "class_name": cls,
                    "students_present": present,
                    "students_total": total,
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    return df


@st.cache_data
def load_attendance_data(source) -> pd.DataFrame:
    """Load, validate, and clean attendance CSV records."""
    df = pd.read_csv(source)
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing_cols)}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["class_name"] = df["class_name"].astype(str).str.strip()
    df["students_present"] = pd.to_numeric(df["students_present"], errors="coerce")
    df["students_total"] = pd.to_numeric(df["students_total"], errors="coerce")

    df = df.dropna(subset=["date", "class_name", "students_present", "students_total"])
    df = df[df["students_total"] > 0]
    df["students_present"] = df["students_present"].clip(lower=0)
    df["attendance_rate"] = (df["students_present"] / df["students_total"]) * 100.0
    df["date_only"] = df["date"].dt.date
    return df.sort_values(["date", "class_name"])


def main() -> None:
    st.title(" Nakuru School Attendance Monitor")
    st.caption(
        "Daily attendance overview for the principal — track overall rates, compare classes, "
        "and spot recent attendance dips without opening Excel."
    )

    with st.sidebar:
        st.header("Data Source")
        uploaded_file = st.file_uploader("Upload attendance CSV", type=["csv"])
        if not DEFAULT_CSV_PATH.exists():
            generate_sample_attendance_csv(DEFAULT_CSV_PATH)

    try:
        if uploaded_file is not None:
            df = load_attendance_data(uploaded_file)
            st.info(f"Showing uploaded file: **{uploaded_file.name}**")
        else:
            df = load_attendance_data(DEFAULT_CSV_PATH)
    except Exception as exc:
        st.error(f"Could not load attendance data: {exc}")
        st.stop()

    if df.empty:
        st.warning("No valid attendance rows found in the dataset.")
        st.stop()

    min_date = df["date_only"].min()
    max_date = df["date_only"].max()

    # Default slider window to roughly the last 30 calendar days so dips stand out immediately
    default_start = max(min_date, max_date - pd.Timedelta(days=30))

    st.subheader("Date Range Filter")
    selected_start, selected_end = st.slider(
        "Select date range",
        min_value=min_date,
        max_value=max_date,
        value=(default_start, max_date),
        format="YYYY-MM-DD",
    )

    filtered_df = df[
        (df["date_only"] >= selected_start) & (df["date_only"] <= selected_end)
    ].copy()

    if filtered_df.empty:
        st.warning("No attendance records fall inside the selected date range.")
        st.stop()

    # Overall attendance rate across selected period
    total_present = filtered_df["students_present"].sum()
    total_enrolled = filtered_df["students_total"].sum()
    overall_rate = (total_present / total_enrolled) * 100.0 if total_enrolled else 0.0

    # Attendance summary by class
    class_summary = (
        filtered_df.groupby("class_name", as_index=False)[["students_present", "students_total"]]
        .sum()
        .assign(
            attendance_pct=lambda g: (g["students_present"] / g["students_total"]) * 100.0
        )
        .sort_values("attendance_pct", ascending=False)
    )

    best_row = class_summary.iloc[0]
    worst_row = class_summary.iloc[-1]

    # Top 3 KPI metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Attendance Rate", f"{overall_rate:.1f}%")
    col2.metric(
        "Best-Attending Class",
        f"{best_row['class_name']}",
        f"{best_row['attendance_pct']:.1f}%",
    )
    col3.metric(
        "Worst-Attending Class",
        f"{worst_row['class_name']}",
        f"{worst_row['attendance_pct']:.1f}%",
        delta_color="inverse",
    )

    st.divider()

    # Show each class as a separate bar for every date.
    st.subheader("Daily Attendance Rate by Class (%)")
    st.caption(
        "Showing daily attendance percentage per class across the selected window "
        "(defaults to the last 30 days to highlight declining trends)."
    )

    st.bar_chart(
        filtered_df,
        x="date",
        y="attendance_rate",
        color="class_name",
        x_label="Date",
        y_label="Attendance Rate (%)",
        stack=False,
        height=380,
    )

    # Attendance by class breakdown table
    st.subheader("Attendance by Class")
    display_summary = class_summary.copy()
    display_summary["attendance_pct"] = display_summary["attendance_pct"].round(1)
    display_summary.columns = [
        "Class Name",
        "Total Students Present",
        "Total Student-Days",
        "Attendance Rate (%)",
    ]
    st.dataframe(display_summary, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()