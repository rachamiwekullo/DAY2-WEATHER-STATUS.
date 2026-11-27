from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st


APP_VERSION = "v1.0"
TARGET_STAFF_CAPACITY = 50
SETUP_PRICE_RANGE_KES = (25_000, 40_000)

SETUP_TIERS = [
    {
        "Package": "Core Setup (Up to 50 Staff)",
        "Price (KES)": "KES 25,000",
        "Includes": (
            "CSV upload & validation, KPI cards, department attendance bar/trend charts, "
            "individual rolling trend lines, monthly summary & CSV export, Streamlit Cloud deploy"
        ),
    },
    {
        "Package": "Standard + Custom Branding & Schema Mapping",
        "Price (KES)": "KES 32,500",
        "Includes": (
            "Everything in Core Setup + custom company colors/logo, column mapping for existing "
            "HR/biometric CSV exports, and staff onboarding walkthrough"
        ),
    },
    {
        "Package": "Full Setup + Custom Rules & Handover",
        "Price (KES)": "KES 40,000",
        "Includes": (
            "Everything in Standard + custom lateness/threshold rules, tailored monthly report "
            "templates, documentation, and team training session"
        ),
    },
]

REQUIRED_COLUMNS = ["date", "staff_id", "name", "department", "status"]
VALID_STATUSES = ["Present", "Late", "Absent", "Leave"]

DEPARTMENTS = {
    "Operations": 14,
    "Sales": 10,
    "Finance": 8,
    "IT": 7,
    "HR & Admin": 6,
    "Customer Service": 5,
}

NAMES = [
    "Patrick Rachami", "Betty Koech", "Ben Anyango", "Felix Wekesa",
    "Betty Wafula", "Rachel Ndungu", "Samuel Macharia", "Cynthia Macharia",
    "Sharon Ouma", "Eric Njoroge", "Lilian Wekesa", "Felix Wafula",
    "Faith Gathoni", "Joseph Chebet", "Lilian Ochieng", "Paul Wafula",
    "Irene Juma", "Daniel Mumbi", "Cynthia Barasa", "Collins Ndungu",
    "Lucy Owino", "Joseph Kiplagat", "Mercy Naliaka", "Felix Mumbi",
    "Samuel Waweru", "Paul Kibet", "Sharon Rachami", "Mark Ndungu",
    "Alice Macharia", "Joseph Mbugua", "Mark Ruto", "Dennis Waweru",
    "Collins Gathoni", "Ronald Mbugua", "Evans Rotich", "Agnes Ouma",
    "Naomi Ruto", "Brian Macharia", "Mark Chebet", "Doreen Mutiso",
    "Simon Waweru", "Mary Njoroge", "Patrick Owino", "Mary Sitati",
    "Mary Owino", "Samuel Kiplagat", "Faith Sitati", "Andrew Naliaka",
    "John Simiyu", "Mark Mutiso",
]

def generate_sample_data(seed: int = 42, working_days: int = 130) -> pd.DataFrame:
    """Create realistic synthetic attendance for 50 staff over ~6 months."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=working_days)

    # Draw each name without replacement so no two employees share a name
    total_staff = sum(DEPARTMENTS.values())
    names = [str(n) for n in rng.choice(NAMES, size=total_staff, replace=False)]

    staff = []
    idx = 0
    for dept, count in DEPARTMENTS.items():
        for _ in range(count):
            staff.append(
                {
                    "staff_id": f"EMP{idx + 1:03d}",
                    "name": names[idx],
                    "department": dept,
                    "p_absent": rng.uniform(0.01, 0.10),
                    "p_late": rng.uniform(0.02, 0.15),
                    "p_leave": rng.uniform(0.02, 0.05),
                }
            )
            idx += 1

    rows = []
    for person in staff:
        draws = rng.random(len(dates))
        leave_threshold = person["p_leave"]
        absent_threshold = leave_threshold + person["p_absent"]
        late_threshold = absent_threshold + person["p_late"]
        for workday, draw in zip(dates, draws):
            if draw < leave_threshold:
                status = "Leave"
            elif draw < absent_threshold:
                status = "Absent"
            elif draw < late_threshold:
                status = "Late"
            else:
                status = "Present"
            rows.append(
                (workday, person["staff_id"], person["name"], person["department"], status)
            )

    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate an uploaded CSV and return a cleaned frame. Raises ValueError."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    df = df[REQUIRED_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Some values in 'date' could not be read as dates.")

    df["status"] = df["status"].astype(str).str.strip().str.title()
    bad = sorted(set(df["status"]) - set(VALID_STATUSES))
    if bad:
        raise ValueError(
            f"Unknown status value(s): {', '.join(bad)}. Allowed: {', '.join(VALID_STATUSES)}"
        )

    for column in ["staff_id", "department"]:
        df[column] = df[column].astype(str).str.strip()
    df["name"] = df["name"].astype(str).map(lambda s: " ".join(s.split()))

    return df.drop_duplicates(subset=["date", "staff_id"]).sort_values(["date", "staff_id"])


def _rates(df: pd.DataFrame) -> pd.Series:
    present = (df["status"] == "Present").sum()
    late = (df["status"] == "Late").sum()
    absent = (df["status"] == "Absent").sum()
    leave = (df["status"] == "Leave").sum()
    scheduled = present + late + absent
    attended = present + late
    return pd.Series(
        {
            "Present": present,
            "Late": late,
            "Absent": absent,
            "Leave": leave,
            "Attendance %": round(100 * attended / scheduled, 1) if scheduled else np.nan,
            "Punctuality %": round(100 * present / attended, 1) if attended else np.nan,
        }
    )


def department_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("department").apply(_rates, include_groups=False).reset_index()


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(Month=df["date"].dt.to_period("M").astype(str))
        .groupby("Month")
        .apply(_rates, include_groups=False)
        .reset_index()
    )


def department_month_matrix(df: pd.DataFrame) -> pd.DataFrame:
    by_month = df.assign(Month=df["date"].dt.to_period("M").astype(str))
    summary = (
        by_month.groupby(["department", "Month"])
        .apply(_rates, include_groups=False)
        .reset_index()
    )
    return summary.pivot(index="department", columns="Month", values="Attendance %")


def staff_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["staff_id", "name", "department"])
        .apply(_rates, include_groups=False)
        .reset_index()
    )
    return summary.sort_values("Attendance %")


def staff_trend(df: pd.DataFrame, staff_id: str, window: int = 10) -> pd.DataFrame:
    """Rolling attendance rate for one person (leave days are skipped)."""
    staff_data = df[
        (df["staff_id"] == staff_id) & (df["status"] != "Leave")
    ].sort_values("date")
    staff_data = staff_data.assign(
        attended=staff_data["status"].isin(["Present", "Late"]).astype(float)
    )
    staff_data["Rolling attendance %"] = (
        staff_data["attended"]
        .rolling(window, min_periods=max(3, window // 3))
        .mean()
        * 100
    )
    return staff_data[["date", "status", "Rolling attendance %"]]


def company_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Daily company-wide attendance rate."""
    scheduled_data = df[df["status"] != "Leave"].copy()
    scheduled_data["attended"] = scheduled_data["status"].isin(
        ["Present", "Late"]
    ).astype(float)
    return (
        scheduled_data.groupby("date")["attended"]
        .mean()
        .mul(100)
        .rename("Attendance %")
        .reset_index()
    )


def fmt_pct(value) -> str:
    return "N/A" if pd.isna(value) else f"{value:.1f}%"


# ============================================================================
# UI
# ============================================================================
st.set_page_config(
    page_title="HR Attendance Monitor",
    page_icon=":material/groups:",
    layout="wide",
)

st.title("HR attendance monitor")
st.caption("Review attendance, punctuality, and staff trends across departments.")

with st.sidebar:
    st.header("Attendance data")
    uploaded_file = st.file_uploader("Upload attendance CSV", type=["csv"])
    st.caption("Columns: date, staff_id, name, department, status")

if uploaded_file is None:
    data = generate_sample_data()
    data_source = "Generated sample data"
else:
    try:
        uploaded_data = pd.read_csv(uploaded_file)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        st.error(f"Invalid CSV: could not read the uploaded file ({error})")
        st.stop()

    try:
        data = validate_and_clean(uploaded_data)
    except ValueError as error:
        st.error(f"Invalid attendance data: {error}")
        st.stop()

    if data.empty:
        st.error("The uploaded CSV contains no attendance records.")
        st.stop()

    data_source = uploaded_file.name

# Lookup used by every employee picker: staff_id -> "Name (EMP001)"
staff_lookup = (
    data[["staff_id", "name", "department"]].drop_duplicates("staff_id").set_index("staff_id")
)

with st.sidebar:
    st.caption(f"Data source: {data_source}")
    st.caption("Approved leave is excluded from attendance and punctuality rates.")
    st.warning("This dashboard has no sign-in or access controls. Do not expose real staff data publicly.")

    st.header("Filters")
    minimum_date = data["date"].min().date()
    maximum_date = data["date"].max().date()
    selected_dates = st.date_input(
        "Date range",
        value=(minimum_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
        key="attendance_date_range",
    )
    departments = sorted(data["department"].unique().tolist())
    selected_departments = st.multiselect(
        "Departments",
        options=departments,
        default=departments,
        key="attendance_departments",
    )

    # Employee filter: only offers people from the chosen departments
    eligible = staff_lookup[staff_lookup["department"].isin(selected_departments)].sort_values("name")
    employee_labels = {sid: f"{row.name} ({sid})" for sid, row in eligible.iterrows()}
    selected_employees = st.multiselect(
        "Employees",
        options=list(employee_labels),
        format_func=employee_labels.get,
        placeholder="All employees (type a name to search)",
        key="attendance_employees",
    )

if isinstance(selected_dates, tuple):
    start_date = selected_dates[0]
    end_date = selected_dates[-1]
else:
    start_date = end_date = selected_dates

mask = data["date"].dt.date.between(start_date, end_date) & data["department"].isin(selected_departments)
if selected_employees:
    mask &= data["staff_id"].isin(selected_employees)
filtered_data = data[mask].copy()

if filtered_data.empty:
    st.info("No attendance records match the selected filters.")
    st.stop()

# ---------------------------------------------------------------------- KPIs
overall = _rates(filtered_data)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Attendance rate", fmt_pct(overall["Attendance %"]), border=True)
k2.metric("Punctuality rate", fmt_pct(overall["Punctuality %"]), border=True)
k3.metric("Staff in view", f"{filtered_data['staff_id'].nunique():,}", border=True)
k4.metric("Absent days", f"{int(overall['Absent']):,}", border=True)

department_summary_data = department_summary(filtered_data).sort_values(
    "Attendance %", ascending=False
)
daily_trend = company_trend(filtered_data)

left_chart, right_chart = st.columns(2)
with left_chart:
    with st.container(border=True):
        st.subheader("Attendance rate by department")
        st.bar_chart(department_summary_data, x="department", y="Attendance %")

with right_chart:
    with st.container(border=True):
        st.subheader("Daily attendance trend")
        if daily_trend.empty:
            st.info("No scheduled workdays are available for the selected filters.")
        else:
            st.line_chart(daily_trend, x="date", y="Attendance %")

st.subheader("Department summary")
st.dataframe(department_summary_data, hide_index=True)

# --------------------------------------------------------- individual employee
st.subheader("Individual employee")
staff_options = (
    filtered_data[["staff_id", "name", "department"]]
    .drop_duplicates("staff_id")
    .sort_values(["name", "staff_id"])
)
staff_labels = {
    row.staff_id: f"{row.name} — {row.department}"
    for row in staff_options.itertuples(index=False)
}

pick_col, window_col = st.columns([3, 1])
with pick_col:
    selected_staff_id = st.selectbox(
        "Employee",
        options=staff_options["staff_id"].tolist(),
        format_func=lambda staff_id: staff_labels[staff_id],
        key="attendance_staff",
    )
with window_col:
    window = st.select_slider("Rolling window (days)", options=[5, 10, 15, 20], value=10)

employee_data = filtered_data[filtered_data["staff_id"] == selected_staff_id]
employee_rates = _rates(employee_data)

e1, e2, e3, e4, e5 = st.columns(5)
e1.metric("Attendance", fmt_pct(employee_rates["Attendance %"]), border=True)
e2.metric("Punctuality", fmt_pct(employee_rates["Punctuality %"]), border=True)
e3.metric("Late days", f"{int(employee_rates['Late'])}", border=True)
e4.metric("Absent days", f"{int(employee_rates['Absent'])}", border=True)
e5.metric("Leave days", f"{int(employee_rates['Leave'])}", border=True)

trend_col, status_col = st.columns([2, 1])
with trend_col:
    selected_staff_trend = staff_trend(filtered_data, selected_staff_id, window)
    if selected_staff_trend.empty:
        st.info("No scheduled workdays are available for this employee.")
    else:
        st.line_chart(selected_staff_trend, x="date", y="Rolling attendance %")
with status_col:
    breakdown = (
        employee_data["status"].value_counts().reindex(VALID_STATUSES, fill_value=0).rename("Days")
    )
    st.bar_chart(breakdown)

# -------------------------------------------------------- attendance records
st.subheader("Filtered attendance records")

f1, f2, f3 = st.columns([2, 2, 2])
with f1:
    status_filter = st.multiselect(
        "Status", options=VALID_STATUSES, default=VALID_STATUSES, key="records_status"
    )
with f2:
    search_text = st.text_input("Search name or staff ID", key="records_search").strip()
with f3:
    only_selected = st.toggle("Only the employee selected above", key="records_only_selected")

records = filtered_data
if status_filter:
    records = records[records["status"].isin(status_filter)]
if search_text:
    records = records[
        records["name"].str.contains(search_text, case=False, regex=False)
        | records["staff_id"].str.contains(search_text, case=False, regex=False)
    ]
if only_selected:
    records = records[records["staff_id"] == selected_staff_id]

records_view = (
    records.sort_values(["date", "name"], ascending=[False, True])
    .rename(
        columns={
            "date": "Date",
            "staff_id": "Staff ID",
            "name": "Employee",
            "department": "Department",
            "status": "Status",
        }
    )
    .assign(Date=lambda d: d["Date"].dt.date)
    [["Date", "Staff ID", "Employee", "Department", "Status"]]
)

st.caption(f"Showing {len(records_view):,} of {len(filtered_data):,} records")
st.dataframe(
    records_view,
    hide_index=True,
    column_config={"Date": st.column_config.DateColumn("Date", format="DD MMM YYYY")},
)
st.download_button(
    "Download these records (CSV)",
    data=records_view.to_csv(index=False).encode("utf-8"),
    file_name="filtered_hr_attendance.csv",
    mime="text/csv",
)