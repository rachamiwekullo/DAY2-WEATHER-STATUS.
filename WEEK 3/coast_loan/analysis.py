"""Loan repayment analysis for a fictional Mombasa microfinance institution.

Generates 150 fictional loan records, prints a statistical summary, flags
outliers with the IQR method, measures the link between loan size and days
to first repayment, and saves a histogram of loan amounts.
"""
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(42)
N = 150
COUNTIES = ["Mombasa", "Kilifi", "Kwale", "Taita Taveta", "Lamu", "Tana River"]
COUNTY_WEIGHTS = [0.40, 0.22, 0.16, 0.10, 0.06, 0.06]


def make_dataset() -> pd.DataFrame:
    # Typical microloans: right-skewed, centred around ~KES 30,000.
    amounts = RNG.lognormal(mean=np.log(30_000), sigma=0.45, size=N)
    # A handful of unusual loans: large SME loans and very small emergency loans.
    amounts[[7, 41, 88, 123]] = [185_000, 240_000, 162_000, 310_000]
    amounts[[19, 102]] = [2_500, 3_000]
    amounts = np.round(amounts / 500) * 500  # loans issued in KES 500 steps

    # Days to first repayment: base ~ 14-30 days, with a mild upward drift for
    # larger loans plus plenty of borrower-level noise.
    days = 18 + 4 * np.log(amounts / 30_000) + RNG.normal(0, 6, size=N)
    days = np.clip(np.round(days), 3, 60).astype(int)

    return pd.DataFrame({
        "loan_id": [f"LN-{i:04d}" for i in range(1, N + 1)],
        "amount_kes": amounts.astype(int),
        "days_to_first_repayment": days,
        "county": RNG.choice(COUNTIES, size=N, p=COUNTY_WEIGHTS),
    })


def iqr_outliers(s: pd.Series):
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return lo, hi, (s < lo) | (s > hi)


def describe_r(r: float) -> str:
    a = abs(r)
    strength = ("no real" if a < 0.1 else "a weak" if a < 0.3
                else "a moderate" if a < 0.5 else "a strong")
    direction = "positive" if r > 0 else "negative"
    if a < 0.1:
        return (f"The correlation is {r:.2f}: loan size tells us essentially "
                "nothing about how quickly a borrower makes their first repayment.")
    tendency = "slightly longer" if r > 0 else "slightly shorter"
    return (f"The correlation is {r:.2f} ({strength} {direction} link): borrowers "
            f"with bigger loans tend to take {tendency} to make their first "
            "repayment, but loan size alone is a poor predictor of any "
            "individual borrower's timing.")


def plot_histogram(df: pd.DataFrame, path: str) -> None:
    s = df["amount_kes"]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    bins = np.arange(0, s.max() + 10_000, 10_000)
    ax.hist(s, bins=bins, color="#2a78d6", edgecolor="#fcfcfb", linewidth=2)
    med = s.median()
    ax.axvline(med, color="#0b0b0b", linewidth=1.5, linestyle="--")
    ax.text(med + 3_000, ax.get_ylim()[1] * 0.92,
            f"Median KES {med:,.0f}", color="#0b0b0b", fontsize=10)
    ax.set_title("Distribution of loan amounts (150 loans)", loc="left",
                 fontsize=13, color="#0b0b0b")
    ax.set_xlabel("Loan amount (KES)", color="#52514e")
    ax.set_ylabel("Number of loans", color="#52514e")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda x, _: f"{x/1000:,.0f}k"))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#c9c8c3")
    ax.tick_params(colors="#52514e")
    ax.grid(axis="y", color="#e6e5e1", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())


def main() -> None:
    df = make_dataset()
    df.to_csv("loans.csv", index=False)
    pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

    print("=== Statistical summary ===")
    num = df[["amount_kes", "days_to_first_repayment"]]
    summary = num.describe().rename(index={"50%": "50% (median)"})
    print(summary)
    print(f"\nMedian loan amount: KES {df.amount_kes.median():,.0f}")
    print(f"Mean loan amount:   KES {df.amount_kes.mean():,.0f}")

    print("\n=== Outliers (IQR method, 1.5 x IQR) ===")
    for col in num.columns:
        lo, hi, mask = iqr_outliers(df[col])
        print(f"\n{col}: normal range {lo:,.0f} to {hi:,.0f}; "
              f"{mask.sum()} outlier(s)")
        if mask.any():
            print(df.loc[mask, ["loan_id", "amount_kes",
                                "days_to_first_repayment", "county"]]
                  .sort_values(col).to_string(index=False))

    print("\n=== Correlation: amount vs days to first repayment ===")
    pearson = df.amount_kes.corr(df.days_to_first_repayment)
    spearman = df.amount_kes.rank().corr(df.days_to_first_repayment.rank())
    print(f"Pearson r  = {pearson:.3f}")
    print(f"Spearman ρ = {spearman:.3f} (rank-based, less affected by outliers)")
    print(describe_r(pearson))

    print("\n=== Loans by county ===")
    print(df.groupby("county").agg(loans=("loan_id", "count"),
                                   median_amount=("amount_kes", "median"),
                                   median_days=("days_to_first_repayment", "median"))
          .sort_values("loans", ascending=False))

    plot_histogram(df, "loan_amount_histogram.png")
    print("\nSaved: loans.csv, loan_amount_histogram.png")


if __name__ == "__main__":
    main()
