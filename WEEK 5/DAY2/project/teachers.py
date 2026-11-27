from io import BytesIO
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Nakuru School Attendance Monitor",
    page_icon="🏫",
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
def load_attendance_data(file_contents: bytes) -> pd.DataFrame:
    """Load, validate, and normalize attendance CSV data."""
    df = pd.read_csv(BytesIO(file_contents))
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing_cols)}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["class_name"] = df["class_name"].astype(str).str.strip()
    df["students_present"] = pd.to_numeric(df["students_present"], errors="coerce")
    df["students_total"] = pd.to_numeric(df["students_total"], errors="coerce")

    df = df.dropna(subset=REQUIRED_COLUMNS)
    df = df[df["students_total"] > 0]
    df["students_present"] = df["students_present"].clip(lower=0, upper=df["students_total"])
    df["attendance_rate"] = (df["students_present"] / df["students_total"]) * 100.0
    df["date_only"] = df["date"].dt.date
    return df.sort_values(["date", "class_name"])


def main() -> None:
    st.title(" Nakuru School Attendance Monitor")
    st.caption(
        "Self-service attendance dashboard for the principal and class teachers — "
        "upload your class CSV, filter by class and date range, and export clean reports."
    )

    with st.sidebar:
        st.header("1. Upload Attendance CSV")
        uploaded_file = st.file_uploader(
            "Drag and drop your attendance CSV here",
            type=["csv"],
            help="Required columns: date, class_name, students_present, students_total",
        )
        if not DEFAULT_CSV_PATH.exists():
            generate_sample_attendance_csv(DEFAULT_CSV_PATH)

    try:
        if uploaded_file is not None:
            df = load_attendance_data(uploaded_file.getvalue())
            active_source = uploaded_file.name
        else:
            df = load_attendance_data(DEFAULT_CSV_PATH.read_bytes())
            active_source = f"{DEFAULT_CSV_PATH.name} (default sample)"
    except Exception as exc:
        st.error(f"Could not read CSV file: {exc}")
        st.stop()

    if df.empty:
        st.warning("No valid attendance rows found in the uploaded file.")
        st.stop()

    st.info(f"Active dataset: **{active_source}** ({len(df):,} valid records)")

    # Filters: Class dropdown + Date range picker
    available_classes = sorted(df["class_name"].unique().tolist())
    class_options = ["All Classes"] + available_classes
    default_class_index = 1 if len(available_classes) == 1 else 0

    min_date = df["date_only"].min()
    max_date = df["date_only"].max()
    default_start = max(min_date, max_date - pd.Timedelta(days=30))

    filter_col1, filter_col2 = st.columns([1, 1])

    with filter_col1:
        selected_class = st.selectbox(
            "Filter by Class Name",
            options=class_options,
            index=default_class_index,
            help="Teachers can select only their assigned class; the principal can view All Classes.",
        )

    with filter_col2:
        selected_dates = st.date_input(
            "Select Date Range",
            value=(default_start, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif isinstance(selected_dates, tuple) and len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date = end_date = selected_dates

    filtered_df = df[
        (df["date_only"] >= start_date) & (df["date_only"] <= end_date)
    ].copy()

    if selected_class != "All Classes":
        filtered_df = filtered_df[filtered_df["class_name"] == selected_class].copy()

    if filtered_df.empty:
        st.warning("No attendance records match the selected class and date range.")
        st.stop()

    # Summary KPIs
    total_present = int(filtered_df["students_present"].sum())
    total_enrolled = int(filtered_df["students_total"].sum())
    overall_rate = (total_present / total_enrolled) * 100.0 if total_enrolled else 0.0

    class_summary = (
        filtered_df.groupby("class_name", as_index=False)[["students_present", "students_total"]]
        .sum()
        .assign(attendance_pct=lambda g: (g["students_present"] / g["students_total"]) * 100.0)
        .sort_values("attendance_pct", ascending=False)
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Attendance Rate", f"{overall_rate:.1f}%")

    if selected_class == "All Classes":
        best_row = class_summary.iloc[0]
        worst_row = class_summary.iloc[-1]
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
    else:
        best_day = filtered_df.loc[filtered_df["attendance_rate"].idxmax()]
        lowest_day = filtered_df.loc[filtered_df["attendance_rate"].idxmin()]
        col2.metric(
            f"Best Day ({selected_class})",
            best_day["date"].strftime("%Y-%m-%d"),
            f"{best_day['attendance_rate']:.1f}%",
        )
        col3.metric(
            f"Lowest Day ({selected_class})",
            lowest_day["date"].strftime("%Y-%m-%d"),
            f"{lowest_day['attendance_rate']:.1f}%",
            delta_color="inverse",
        )

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader(
            f"Daily Attendance Rate (%) — {selected_class}"
            if selected_class != "All Classes"
            else "Daily Attendance Rate by Class (%)"
        )

        chart_df = filtered_df.pivot(
            index="date",
            columns="class_name",
            values="attendance_rate",
        ).sort_index()

        st.line_chart(chart_df, height=360)

    with chart_col2:
        st.subheader("Attendance Rate by Class (%)")
        class_chart_df = (
            class_summary.set_index("class_name")[["attendance_pct"]]
            .rename(columns={"attendance_pct": "Attendance Rate (%)"})
        )
        st.bar_chart(class_chart_df, height=360)

    # Filtered data table + Download button
    st.subheader("Filtered Attendance Records")

    export_df = filtered_df[
        ["date", "class_name", "students_present", "students_total", "attendance_rate"]
    ].copy()
    export_df["date"] = export_df["date"].dt.strftime("%Y-%m-%d")
    export_df["attendance_rate"] = export_df["attendance_rate"].round(2)

    safe_class_slug = selected_class.lower().replace(" ", "_")
    download_filename = f"attendance_{safe_class_slug}_{start_date}_to_{end_date}.csv"

    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name=download_filename,
        mime="text/csv",
    )

    st.dataframe(export_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()