"""Data layer for the HR Attendance Dashboard (v1.0).

Expected schema (one row per staff member per working day):
    date, staff_id, name, department, status
where status is one of: Present, Late, Absent, Leave
"""
from __future__ import annotations

import numpy as np
import pandas as pd

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
}  # totals 50 staff

FIRST_NAMES = [
    "Wanjiru", "Kamau", "Achieng", "Otieno", "Njeri", "Mwangi", "Akinyi", "Kiprop",
    "Wambui", "Ochieng", "Chebet", "Mutua", "Nyambura", "Kipchoge", "Atieno", "Maina",
    "Wairimu", "Omondi", "Jepkosgei", "Kariuki", "Nduta", "Barasa", "Adhiambo", "Karanja",
    "Muthoni", "Odhiambo", "Cherono", "Njoroge", "Awino", "Rotich",
]
LAST_NAMES = [
    "Kimani", "Odera", "Wekesa", "Mbugua", "Naliaka", "Kiplagat", "Gathoni", "Owino",
    "Macharia", "Cheruiyot", "Waweru", "Ndungu", "Simiyu", "Koech", "Mumbi", "Onyango",
]


def generate_sample_data(seed: int = 42, working_days: int = 130) -> pd.DataFrame:
    """Create realistic synthetic attendance for 50 staff over ~6 months."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=working_days)

    staff = []
    idx = 1
    for dept, count in DEPARTMENTS.items():
        for _ in range(count):
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            staff.append(
                {
                    "staff_id": f"EMP{idx:03d}",
                    "name": name,
                    "department": dept,
                    # Per-person tendencies so trend lines look different
                    "p_absent": rng.uniform(0.01, 0.10),
                    "p_late": rng.uniform(0.02, 0.15),
                    "p_leave": rng.uniform(0.02, 0.05),
                }
            )
            idx += 1

    # Make names unique if random picks collided
    seen: dict[str, int] = {}
    for s in staff:
        seen[s["name"]] = seen.get(s["name"], 0) + 1
        if seen[s["name"]] > 1:
            s["name"] = f'{s["name"]} ({s["staff_id"][-3:]})'

    rows = []
    for s in staff:
        draws = rng.random(len(dates))
        t1 = s["p_leave"]
        t2 = t1 + s["p_absent"]
        t3 = t2 + s["p_late"]
        for d, r in zip(dates, draws):
            if r < t1:
                status = "Leave"
            elif r < t2:
                status = "Absent"
            elif r < t3:
                status = "Late"
            else:
                status = "Present"
            rows.append((d, s["staff_id"], s["name"], s["department"], status))

    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate an uploaded CSV and return a cleaned frame. Raises ValueError."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    df = df[REQUIRED_COLUMNS]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Some values in 'date' could not be read as dates.")

    df["status"] = df["status"].astype(str).str.strip().str.title()
    bad = sorted(set(df["status"]) - set(VALID_STATUSES))
    if bad:
        raise ValueError(
            f"Unknown status value(s): {', '.join(bad)}. Allowed: {', '.join(VALID_STATUSES)}"
        )

    for col in ["staff_id", "name", "department"]:
        df[col] = df[col].astype(str).str.strip()

    return df.drop_duplicates(subset=["date", "staff_id"]).sort_values(["date", "staff_id"])


# --------------------------------------------------------------------------
# Metrics
#
# Attendance rate  = (Present + Late) / (Present + Late + Absent)
#                    Approved Leave is excluded: it is not a scheduled day.
# Punctuality rate = Present / (Present + Late)
#                    Of the days someone showed up, how many were on time.
# --------------------------------------------------------------------------
def _rates(g: pd.DataFrame) -> pd.Series:
    present = (g["status"] == "Present").sum()
    late = (g["status"] == "Late").sum()
    absent = (g["status"] == "Absent").sum()
    leave = (g["status"] == "Leave").sum()
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
    out = (
        df.assign(Month=df["date"].dt.to_period("M").astype(str))
        .groupby("Month")
        .apply(_rates, include_groups=False)
        .reset_index()
    )
    return out


def department_month_matrix(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.assign(Month=df["date"].dt.to_period("M").astype(str))
    res = (
        tmp.groupby(["department", "Month"])
        .apply(_rates, include_groups=False)
        .reset_index()
    )
    return res.pivot(index="department", columns="Month", values="Attendance %")


def staff_summary(df: pd.DataFrame) -> pd.DataFrame:
    res = (
        df.groupby(["staff_id", "name", "department"])
        .apply(_rates, include_groups=False)
        .reset_index()
    )
    return res.sort_values("Attendance %")


def staff_trend(df: pd.DataFrame, staff_id: str, window: int = 10) -> pd.DataFrame:
    """Rolling attendance rate for one person (leave days are skipped)."""
    s = df[(df["staff_id"] == staff_id) & (df["status"] != "Leave")].sort_values("date")
    s = s.assign(attended=s["status"].isin(["Present", "Late"]).astype(float))
    s["Rolling attendance %"] = (
        s["attended"].rolling(window, min_periods=max(3, window // 3)).mean() * 100
    )
    return s[["date", "status", "Rolling attendance %"]]


def company_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Daily company-wide attendance rate."""
    d = df[df["status"] != "Leave"].copy()
    d["attended"] = d["status"].isin(["Present", "Late"]).astype(float)
    return d.groupby("date")["attended"].mean().mul(100).rename("Attendance %").reset_index()