import streamlit as st
import pandas as pd

st.title("Kamau Stores Sales Dashboard")

sales = pd.DataFrame({
    "Month":      ["Jan", "Feb", "Mar", "Apr", "May"],
    "Revenue (KES)": [145000, 162000, 158000, 189000, 201000],
    "County":     ["Nairobi", "Nairobi", "Kisumu", "Nakuru", "Nairobi"]
})

st.sidebar.header("Filters")
counties = sales["County"].unique().tolist()
selected_counties = st.sidebar.multiselect(
    "Select counties",
    options=counties,
    default=counties
)

# Filter the data based on selection
filtered = sales[sales["County"].isin(selected_counties)]

col1, col2, col3 = st.columns(3)

if filtered.empty:
    col1.metric("Total Revenue", "N/A")
    col2.metric("Avg Monthly", "N/A")
    col3.metric("Best Month", "N/A")
else:
    total_rev = filtered["Revenue (KES)"].sum()
    avg_monthly = filtered["Revenue (KES)"].mean()
    best_month = filtered.loc[filtered["Revenue (KES)"].idxmax(), "Month"]

    col1.metric("Total Revenue", f"KES {total_rev:,.0f}")
    col2.metric("Avg Monthly", f"KES {avg_monthly:,.0f}")
    col3.metric("Best Month", best_month)

st.subheader(f"Monthly Sales Data ({len(filtered)} records)")
st.dataframe(filtered)

st.subheader("Revenue Trend")
if filtered.empty:
    st.info("Select at least one county to view the revenue trend.")
else:
    st.bar_chart(filtered.set_index("Month")["Revenue (KES)"])

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    st.success(f"Loaded {len(df)} rows")
    st.dataframe(df.head(10))
else:
    st.info("Upload a sales CSV to get started. Or use the sample data below.")