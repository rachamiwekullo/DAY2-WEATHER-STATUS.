#Build a Python script that loads fresh data, runs analysis, and generates a report automatically:

import pandas as pd
import matplotlib.pyplot as plt
import datetime, os

def generate_report():
    # 1. Load fresh data
    df = pd.read_csv("data/sales_latest.csv")
    df["revenue"] = df["quantity"] * df["price"]

    # 2. Run analysis
    total_rev = df["revenue"].sum()
    top_county = df.groupby("county")["revenue"].sum().idxmax()
    order_count = len(df)

    # 3. Generate chart
    county_rev = df.groupby("county")["revenue"].sum().sort_values(ascending=False)
    county_rev.plot(kind="bar", color="#1F4E79")
    plt.title("Revenue by County")
    plt.savefig("charts/county_revenue.png")
    plt.close()

    return {
        "total_rev": total_rev,
        "top_county": top_county,
        "order_count": order_count
    }

#Save charts as images and embed them in an HTML report:

import base64

def build_html_report(data, timestamp):
    # Convert chart image to base64 for embedding
    with open("charts/county_revenue.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    html = (
        '<html><body style="font-family:Arial">'
        f'<h2>Sales Report: {timestamp}</h2>'
        f'<p>Total Revenue: <strong>KES {data["total_rev"]:,.0f}</strong></p>'
        f'<p>Top Region: <strong>{data["top_county"]}</strong></p>'
        f'<p>Total Orders: <strong>{data["order_count"]}</strong></p>'
        f'<img src="data:image/png;base64,{img_b64}" width="600">'
        '</body></html>'
    )
    with open("reports/report.html", "w") as f:
        f.write(html)
    print("Report saved to reports/report.html")

#Add a timestamp so the client knows when data was last updated. This is a small thing that builds a lot of trust:

timestamp = datetime.datetime.now().strftime("%A %d %B %Y at %H:%M")
# Produces: "Monday 26 September 2026 at 08:00"

data = generate_report()
build_html_report(data, timestamp)
#Report header
#Sales Report: Monday 26 September 2026 at 08:00
#Total Revenue: KES 778,250
#Top Region: Nairobi
#Total Orders: 198

#Schedule the report to run daily using the schedule library:

import schedule, time, logging

logging.basicConfig(filename="report.log", level=logging.INFO,
                    format="%(asctime)s | %(message)s")

def daily_job():
    try:
        timestamp = datetime.datetime.now().strftime("%A %d %B %Y at %H:%M")
        data = generate_report()
        build_html_report(data, timestamp)
        logging.info("Report generated and saved OK")
    except Exception as e:
        logging.error(f"Report failed: {e}")

schedule.every().day.at("08:00").do(daily_job)

while True:
    schedule.run_pending()
    time.sleep(60)