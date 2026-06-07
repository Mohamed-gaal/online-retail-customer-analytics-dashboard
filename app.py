from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import (
    CLEANED_FILE,
    COUNTRY_FILE,
    KPI_FILE,
    MONTHLY_FILE,
    PRODUCT_FILE,
    RAW_FILE,
    RETENTION_FILE,
    RFM_FILE,
    SEGMENT_FILE,
)
from src.pipeline import run_pipeline


st.set_page_config(page_title="Online Retail Customer Analytics", layout="wide")


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame]:
    if not CLEANED_FILE.exists() and RAW_FILE.exists():
        run_pipeline()
    required = [CLEANED_FILE, KPI_FILE, MONTHLY_FILE, COUNTRY_FILE, PRODUCT_FILE, RFM_FILE, SEGMENT_FILE, RETENTION_FILE]
    missing = [path for path in required if not path.exists()]
    if missing:
        return {}
    return {
        "cleaned": pd.read_csv(CLEANED_FILE, parse_dates=["invoice_datetime"]),
        "kpis": pd.read_csv(KPI_FILE),
        "monthly": pd.read_csv(MONTHLY_FILE),
        "country": pd.read_csv(COUNTRY_FILE),
        "product": pd.read_csv(PRODUCT_FILE),
        "rfm": pd.read_csv(RFM_FILE),
        "segments": pd.read_csv(SEGMENT_FILE),
        "retention": pd.read_csv(RETENTION_FILE),
    }


def money(value: float) -> str:
    return f"${value:,.0f}"


def filtered_sales(df: pd.DataFrame, countries: list[str], date_range) -> pd.DataFrame:
    sales = df.loc[df["is_valid_sale"]].copy()
    if countries:
        sales = sales.loc[sales["country"].isin(countries)]
    if date_range and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        sales = sales.loc[(sales["invoice_datetime"] >= start) & (sales["invoice_datetime"] <= end + pd.Timedelta(days=1))]
    return sales


data = load_data()

st.title("Online Retail Customer Analytics")
st.caption("Sales performance, customer segmentation, product demand, and retention signals from the UCI Online Retail dataset.")

if not data:
    st.info(
        "Place the Kaggle CSV at data/raw/online_retail.csv, then run `python -m src.pipeline` or refresh this dashboard."
    )
    st.stop()

cleaned = data["cleaned"]
sales = cleaned.loc[cleaned["is_valid_sale"]].copy()

with st.sidebar:
    st.header("Filters")
    countries = sorted(sales["country"].dropna().unique().tolist())
    selected_countries = st.multiselect("Country", countries, default=[])
    min_date = sales["invoice_datetime"].min().date()
    max_date = sales["invoice_datetime"].max().date()
    date_range = st.date_input("Invoice date", value=(min_date, max_date), min_value=min_date, max_value=max_date)

view = filtered_sales(cleaned, selected_countries, date_range)

orders = view["invoice_no"].nunique()
revenue = view["net_revenue"].sum()
customers = view.loc[view["customer_id"] != "Unknown", "customer_id"].nunique()
products = view["stock_code"].nunique()
average_order_value = revenue / orders if orders else 0

metric_cols = st.columns(5)
metric_cols[0].metric("Revenue", money(revenue))
metric_cols[1].metric("Orders", f"{orders:,}")
metric_cols[2].metric("Customers", f"{customers:,}")
metric_cols[3].metric("Products", f"{products:,}")
metric_cols[4].metric("Avg Order", money(average_order_value))

tabs = st.tabs(["Sales", "Products", "Customers", "Retention", "Data Quality"])

with tabs[0]:
    monthly = (
        view.assign(invoice_month=view["invoice_datetime"].dt.to_period("M").astype(str))
        .groupby("invoice_month", as_index=False)
        .agg(revenue=("net_revenue", "sum"), orders=("invoice_no", "nunique"))
        .sort_values("invoice_month")
    )
    country = (
        view.groupby("country", as_index=False)
        .agg(revenue=("net_revenue", "sum"), orders=("invoice_no", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(20)
    )
    st.plotly_chart(px.line(monthly, x="invoice_month", y="revenue", markers=True, title="Monthly Revenue"), use_container_width=True)
    st.plotly_chart(px.bar(country, x="revenue", y="country", orientation="h", title="Top Countries by Revenue"), use_container_width=True)

with tabs[1]:
    product = (
        view.groupby(["stock_code", "description"], as_index=False)
        .agg(revenue=("net_revenue", "sum"), quantity=("quantity", "sum"), orders=("invoice_no", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(25)
    )
    st.plotly_chart(px.bar(product, x="revenue", y="description", orientation="h", title="Top Products by Revenue"), use_container_width=True)
    st.dataframe(product, use_container_width=True, hide_index=True)

with tabs[2]:
    rfm = data["rfm"]
    segments = data["segments"]
    st.plotly_chart(px.bar(segments, x="segment", y="revenue", color="customers", title="Customer Segments by Revenue"), use_container_width=True)
    st.plotly_chart(
        px.scatter(rfm, x="recency", y="monetary", size="frequency", color="segment", hover_data=["customer_id"], title="RFM Customer Map"),
        use_container_width=True,
    )
    st.dataframe(segments, use_container_width=True, hide_index=True)

with tabs[3]:
    retention = data["retention"]
    if retention.empty:
        st.info("Retention cohorts require known customer IDs.")
    else:
        cohort = retention.pivot(index="cohort_month", columns="period_number", values="customers").fillna(0)
        st.dataframe(cohort, use_container_width=True)
        st.plotly_chart(
            px.imshow(cohort, aspect="auto", title="Monthly Customer Retention Cohorts", labels={"x": "Months Since First Purchase", "y": "Cohort Month"}),
            use_container_width=True,
        )

with tabs[4]:
    kpis = data["kpis"].iloc[0]
    quality = pd.DataFrame(
        [
            {"check": "Total raw/cleaned rows", "value": f"{len(cleaned):,}"},
            {"check": "Rows retained as valid sales", "value": f"{int(cleaned['is_valid_sale'].sum()):,}"},
            {"check": "Rows with missing customer ID", "value": f"{int(kpis['missing_customer_rows']):,}"},
            {"check": "Cancelled, return, or invalid rows", "value": f"{int(kpis['cancelled_or_adjustment_rows']):,}"},
            {"check": "Date range", "value": f"{min_date} to {max_date}"},
        ]
    )
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.dataframe(cleaned.head(200), use_container_width=True, hide_index=True)
