from pathlib import Path
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

CSV_PATH = "ngo_nutrition_outcomes.csv"

HEADLINES = {
    "county": "Kisumu led the way in healthy weight gain across the three counties",
    "attendance": "Families who showed up regularly saw stronger weight gains",
    "age_group": "Babies and toddlers gained more ground than older children",
}

CHART_FILES = {
    "county": "chart1_county_performance.png",
    "attendance": "chart2_attendance_vs_weight_gain.png",
    "age_group": "chart3_age_group_outcomes.png",
}


def generate_dataset(csv_path: str = CSV_PATH) -> pd.DataFrame:
    """Create a 180-participant six-month NGO nutrition outcomes dataset across 3 counties."""
    rng = np.random.default_rng(2026)
    counties = ["Kajiado", "Kilifi", "Kisumu"]
    age_groups = ["6-23 months", "24-59 months", "5-12 years"]

    records = []
    pid = 1
    for county in counties:
        for age_group in age_groups:
            for _ in range(20):
                months_in_program = int(
                    rng.choice([3, 4, 5, 6, 6, 6], p=[0.1, 0.15, 0.2, 0.2, 0.2, 0.15])
                )
                base_sessions = months_in_program * 2
                sessions_attended = int(np.clip(base_sessions - rng.integers(0, 5), 2, 12))

                county_boost = {"Kisumu": 0.95, "Kajiado": 0.35, "Kilifi": 0.0}[county]
                age_boost = {"6-23 months": 0.90, "24-59 months": 0.35, "5-12 years": 0.0}[age_group]
                attendance_effect = sessions_attended * 0.24

                weight_gain_kg = round(
                    float(
                        np.clip(
                            0.3 + county_boost + age_boost + attendance_effect + rng.normal(0, 0.32),
                            0.4,
                            5.2,
                        )
                    ),
                    2,
                )

                records.append(
                    {
                        "participant_id": f"NUT-{pid:03d}",
                        "county": county,
                        "age_group": age_group,
                        "sessions_attended": sessions_attended,
                        "months_in_program": months_in_program,
                        "weight_gain_kg": weight_gain_kg,
                    }
                )
                pid += 1

    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)
    return df


def create_donor_charts(df: pd.DataFrame) -> None:
    """Generate one clear, single-message chart for each of the three donor findings."""
    rng = np.random.default_rng(2026)

    # Chart 1: Horizontal Bar Chart — County Performance
    county_summary = (
        df.groupby("county", as_index=False)["weight_gain_kg"]
        .mean()
        .rename(columns={"weight_gain_kg": "avg_weight_gain_kg"})
        .sort_values("avg_weight_gain_kg", ascending=True)
    )

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    top_county = county_summary.loc[
        county_summary["avg_weight_gain_kg"].idxmax(), "county"
    ]
    colors_c = [
        "#1b6ca8" if county == top_county else "#8d99ae"
        for county in county_summary["county"]
    ]
    bars = ax.barh(
        county_summary["county"],
        county_summary["avg_weight_gain_kg"],
        color=colors_c,
        height=0.52,
    )
    ax.axvline(
        df["weight_gain_kg"].mean(),
        color="#e76f51",
        linestyle="--",
        linewidth=1.4,
        label="Filtered Average",
    )
    ax.set_title("Average Weight Gain by County", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Average Weight Gain (kg)")
    ax.set_xlim(0, max(3.85, county_summary["avg_weight_gain_kg"].max() * 1.15))
    ax.grid(axis="x", linestyle=":", alpha=0.6)
    ax.legend(loc="lower right")
    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + 0.06,
            bar.get_y() + bar.get_height() / 2,
            f"{w:.2f} kg",
            va="center",
            fontsize=10,
            fontweight="bold",
        )
    plt.tight_layout()
    plt.savefig(CHART_FILES["county"], dpi=200)
    plt.close()

    # Chart 2: Scatter Plot with Trend Line — Attendance vs Weight Gain
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    jitter = rng.normal(0, 0.14, size=len(df))
    ax.scatter(
        df["sessions_attended"] + jitter,
        df["weight_gain_kg"],
        color="#2a9d8f",
        alpha=0.65,
        edgecolors="white",
        s=55,
        label="Each Child",
    )
    if df["sessions_attended"].nunique() > 1:
        slope, intercept = np.polyfit(df["sessions_attended"], df["weight_gain_kg"], 1)
        x_vals = np.linspace(df["sessions_attended"].min(), df["sessions_attended"].max(), 50)
        ax.plot(
            x_vals,
            slope * x_vals + intercept,
            color="#e76f51",
            linewidth=2.4,
            label="Filtered Trend",
        )
    else:
        ax.text(
            0.5,
            0.95,
            "Trend line needs more than one session-count value",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=9,
        )
    ax.set_title("Sessions Attended and Weight Gain", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Sessions Attended (out of 12)")
    ax.set_ylabel("Weight Gain Over Six Months (kg)")
    ax.set_xticks(range(2, 13))
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(CHART_FILES["attendance"], dpi=200)
    plt.close()

    # Chart 3: Bar Chart — Age Group Differences
    age_order = ["6-23 months", "24-59 months", "5-12 years"]
    available_age_order = [group for group in age_order if group in df["age_group"].unique()]
    age_plot = (
        df.groupby("age_group", as_index=False)["weight_gain_kg"]
        .mean()
        .rename(columns={"weight_gain_kg": "avg_weight_gain_kg"})
        .set_index("age_group")
        .reindex(available_age_order)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    age_colors = {
        "6-23 months": "#264653",
        "24-59 months": "#457b9d",
        "5-12 years": "#a8dadc",
    }
    colors_a = [age_colors[group] for group in age_plot["age_group"]]
    bars_a = ax.bar(age_plot["age_group"], age_plot["avg_weight_gain_kg"], color=colors_a, width=0.48)
    ax.set_title(HEADLINES["age_group"], fontsize=12, fontweight="bold", pad=14)
    ax.set_xlabel("Age Group at Enrollment")
    ax.set_ylabel("Average Weight Gain (kg)")
    ax.set_ylim(0, max(4.2, age_plot["avg_weight_gain_kg"].max() * 1.18))
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    for bar in bars_a:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.08,
            f"{h:.2f} kg",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
    plt.tight_layout()
    plt.savefig(CHART_FILES["age_group"], dpi=200)
    plt.close()


def write_donor_brief_markdown(path: str = "DONOR_HEADLINES.md") -> None:
    """Write the three plain-language headlines and pricing note for GitHub."""
    content = f"""# Six-Month Nutrition Program Donor Headlines

1. **County Performance:** {HEADLINES["county"]}
2. **Session Attendance:** {HEADLINES["attendance"]}
3. **Age Groups:** {HEADLINES["age_group"]}

## Dashboard Filters
- **County:** Select one or more counties.
- **Age group:** Select one or more enrollment age groups.
- **Sessions attended:** Set the inclusive session-count range.

The dashboard recalculates its KPIs, chart images, and on-screen summaries using the selected records.
The headlines in this file describe the full default sample; they are not rewritten for each active filter selection.

## Charts Included
- `{CHART_FILES["county"]}` — Horizontal bar chart comparing average weight gain by county.
- `{CHART_FILES["attendance"]}` — Scatter plot with trend line showing weight gain as session attendance rises.
- `{CHART_FILES["age_group"]}` — Vertical bar chart comparing average weight gain across enrollment age groups.

## Pricing Note (Six-Month NGO Program Analysis)
- **Light / Donor-Ready Summary Package:** KES 45,000 – 85,000 (or USD 350 – 650) for data cleaning, three donor visuals, and a concise briefing deck/story.
- **Full Six-Month Evaluation Package:** KES 120,000 – 250,000+ (or USD 900 – 2,000+) when adding baseline/endline clinical validation, subgroup equity checks, field interviews, and a live dashboard.
"""
    Path(path).write_text(content, encoding="utf-8")


def push_to_github(commit_message: str = "Add donor nutrition charts and headlines", branch: str = "main") -> None:
    """Stage, commit, and push generated charts and headline summary to GitHub."""
    files_to_stage = [*CHART_FILES.values(), "DONOR_HEADLINES.md", CSV_PATH]
    subprocess.run(["git", "add", *files_to_stage], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push", "origin", branch], check=True)


if __name__ == "__main__":
    data = generate_dataset()
    write_donor_brief_markdown()

    st.title("NGO Nutrition Outcomes Dashboard")
    st.caption("Six-month story view across counties, session attendance, and age groups.")

    with st.sidebar:
        st.header("Data Filters")
        county_options = sorted(data["county"].unique().tolist())
        selected_counties = st.multiselect(
            "County",
            options=county_options,
            default=county_options,
        )
        age_options = [
            "6-23 months",
            "24-59 months",
            "5-12 years",
        ]
        selected_age_groups = st.multiselect(
            "Age group",
            options=age_options,
            default=age_options,
        )
        session_min = int(data["sessions_attended"].min())
        session_max = int(data["sessions_attended"].max())
        selected_session_range = st.slider(
            "Sessions attended",
            min_value=session_min,
            max_value=session_max,
            value=(session_min, session_max),
        )

    filtered_data = data[
        data["county"].isin(selected_counties)
        & data["age_group"].isin(selected_age_groups)
        & data["sessions_attended"].between(*selected_session_range)
    ].copy()

    if filtered_data.empty:
        st.warning("No participants match these filters. Widen your selections and try again.")
        st.stop()

    create_donor_charts(filtered_data)
    st.caption(f"Showing {len(filtered_data):,} of {len(data):,} participants.")

    county_summary = filtered_data.groupby("county").agg(
        avg_weight_gain_kg=("weight_gain_kg", "mean"),
        avg_sessions=("sessions_attended", "mean"),
    )
    age_summary = filtered_data.groupby("age_group")["weight_gain_kg"].mean()
    high_attendance_mean = filtered_data.loc[
        filtered_data["sessions_attended"] >= 10, "weight_gain_kg"
    ].mean()
    low_attendance_mean = filtered_data.loc[
        filtered_data["sessions_attended"] <= 6, "weight_gain_kg"
    ].mean()
    session_correlation = filtered_data["sessions_attended"].corr(
        filtered_data["weight_gain_kg"]
    )

    leading_county = county_summary["avg_weight_gain_kg"].idxmax()
    trailing_county = county_summary["avg_weight_gain_kg"].idxmin()
    leading_age_group = age_summary.idxmax()
    correlation_display = (
        f"r = {session_correlation:.2f}"
        if pd.notna(session_correlation)
        else "N/A"
    )
    attendance_delta = (
        f"{high_attendance_mean - low_attendance_mean:.2f} kg higher at 10+ sessions"
        if pd.notna(high_attendance_mean) and pd.notna(low_attendance_mean)
        else "Not enough data for both session groups"
    )

    st.subheader("Key Performance Indicators")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric(
        "County Performance",
        f"{county_summary.loc[leading_county, 'avg_weight_gain_kg']:.2f} kg",
        leading_county,
    )
    kpi_col2.metric(
        "Attendance vs. Outcomes",
        correlation_display,
        attendance_delta,
    )
    kpi_col3.metric(
        "Age-Group Outcomes",
        f"{age_summary.loc[leading_age_group]:.2f} kg",
        leading_age_group,
    )

    st.subheader("1. County summary")
    st.image(CHART_FILES["county"], use_container_width=True)
    if county_summary.shape[0] > 1:
        st.markdown(
            f"**{leading_county} had the highest average weight gain among the selected counties.**"
        )
        st.write(
            f"Average gain was {county_summary.loc[leading_county, 'avg_weight_gain_kg']:.2f} kg "
            f"in {leading_county}, compared with "
            f"{county_summary.loc[trailing_county, 'avg_weight_gain_kg']:.2f} kg in "
            f"{trailing_county}."
        )
    else:
        st.markdown(f"**Average weight gain for {leading_county} in the selected data.**")
        st.write(
            f"The filtered average was "
            f"{county_summary.loc[leading_county, 'avg_weight_gain_kg']:.2f} kg."
        )

    st.subheader("2. Attendance ")
    st.image(CHART_FILES["attendance"], use_container_width=True)
    st.markdown("**Attendance and weight gain among the selected participants.**")
    if pd.notna(high_attendance_mean) and pd.notna(low_attendance_mean):
        st.write(
            f"Participants attending 10 or more sessions averaged "
            f"{high_attendance_mean:.2f} kg gain, compared with "
            f"{low_attendance_mean:.2f} kg for those attending 6 or fewer."
        )
    else:
        st.write(
            "The selected filters do not include participants from both the 10+ and "
            "6-or-fewer session groups, so that comparison is unavailable."
        )
    st.caption("A correlation shows association, not proof that attendance caused the outcome.")

    st.subheader("3. Age Group ")
    st.image(CHART_FILES["age_group"], use_container_width=True)
    if age_summary.shape[0] > 1:
        st.markdown(
            f"**{leading_age_group} had the highest average gain among the selected age groups.**"
        )
    else:
        st.markdown(f"**Average weight gain for {leading_age_group} in the selected data.**")
    age_details = "; ".join(
        f"{group}: {average:.2f} kg" for group, average in age_summary.items()
    )
    st.write(f"Average gains by age group: {age_details}.")

    with st.expander("Pricing Note for Six-Month NGO Analysis"):
        st.write(
            "Typical range: KES 45,000–85,000 (USD 350–650) for a focused donor story & chart pack, "
            "or KES 120,000–250,000+ (USD 900–2,000+) for a deeper multi-county evaluation."
        )