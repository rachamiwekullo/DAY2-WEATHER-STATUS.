#Add a selectbox that filters data by category. This is the most common Streamlit interaction:

import streamlit as st
import pandas as pd

df = pd.read_csv("sales_data.csv")

# Selectbox for county filter
counties = ["All"] + sorted(df["county"].unique().tolist())
selected_county = st.selectbox("Filter by county", counties)

# Apply filter
if selected_county == "All":
    filtered = df
else:
    filtered = df[df["county"] == selected_county]

st.write(f"Showing {len(filtered)} rows for {selected_county}")
st.dataframe(filtered)

#Add a date range selector for time series data:

import datetime

df["date"] = pd.to_datetime(df["date"])

# Date range picker
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("From", df["date"].min())
with col2:
    end_date = st.date_input("To", df["date"].max())

# Filter by date range
mask = (df["date"] >= pd.Timestamp(start_date)) & (df["date"] <= pd.Timestamp(end_date))
date_filtered = df[mask]
st.write(f"Orders between {start_date} and {end_date}: {len(date_filtered)}")

#Display two charts side by side using st.columns:

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by County")
    county_rev = filtered.groupby("county")["revenue"].sum().sort_values()
    st.bar_chart(county_rev)

with col2:
    st.subheader("Orders per Month")
    monthly = filtered.set_index("date").resample("M")["order_id"].count()
    st.line_chart(monthly)

#Add a file uploader so the user can analyze their own CSV:

st.subheader("Upload your own data")
uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded is not None:
    user_df = pd.read_csv(uploaded)
    st.success(f"Loaded {len(user_df)} rows")
    st.dataframe(user_df.head(10))
    # Run your analysis on user_df just like the built-in data
else:
    st.info("Upload a CSV or use the default dataset below")

#Cache expensive operations so the app does not reload data on every interaction:

@st.cache_data
def load_data(filepath):
    """Loads and cleans the data once. Cached until the file changes."""
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    df["revenue"] = df["quantity"] * df["price"]
    return df

# This only runs ONCE. After that, Streamlit uses the cached result.
df = load_data("sales_data.csv")