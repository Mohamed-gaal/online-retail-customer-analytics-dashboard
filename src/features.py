import numpy as np
import pandas as pd


def valid_sales(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[df["is_valid_sale"]].copy()


def build_kpis(df: pd.DataFrame) -> pd.DataFrame:
    sales = valid_sales(df)
    known_customers = sales.loc[~sales["is_missing_customer"], "customer_id"]
    invoices = sales["invoice_no"].nunique()
    revenue = sales["net_revenue"].sum()
    quantity = sales["quantity"].sum()
    return pd.DataFrame(
        [
            {
                "total_revenue": revenue,
                "total_orders": invoices,
                "total_quantity": quantity,
                "unique_customers": known_customers.nunique(),
                "unique_products": sales["stock_code"].nunique(),
                "countries": sales["country"].nunique(),
                "average_order_value": revenue / invoices if invoices else 0.0,
                "missing_customer_rows": int(df["is_missing_customer"].sum()),
                "cancelled_or_adjustment_rows": int((~df["is_valid_sale"]).sum()),
            }
        ]
    )


def build_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    sales = valid_sales(df)
    monthly = (
        sales.groupby("invoice_month", as_index=False)
        .agg(
            revenue=("net_revenue", "sum"),
            orders=("invoice_no", "nunique"),
            quantity=("quantity", "sum"),
            customers=("customer_id", lambda values: values[values != "Unknown"].nunique()),
        )
        .sort_values("invoice_month")
    )
    monthly["average_order_value"] = monthly["revenue"] / monthly["orders"].replace(0, np.nan)
    return monthly.fillna({"average_order_value": 0})


def build_country_sales(df: pd.DataFrame, limit: int = 25) -> pd.DataFrame:
    sales = valid_sales(df)
    return (
        sales.groupby("country", as_index=False)
        .agg(
            revenue=("net_revenue", "sum"),
            orders=("invoice_no", "nunique"),
            customers=("customer_id", lambda values: values[values != "Unknown"].nunique()),
        )
        .sort_values("revenue", ascending=False)
        .head(limit)
    )


def build_product_sales(df: pd.DataFrame, limit: int = 30) -> pd.DataFrame:
    sales = valid_sales(df)
    return (
        sales.groupby(["stock_code", "description"], as_index=False)
        .agg(revenue=("net_revenue", "sum"), quantity=("quantity", "sum"), orders=("invoice_no", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(limit)
    )


def build_rfm_segments(df: pd.DataFrame) -> pd.DataFrame:
    sales = valid_sales(df)
    sales = sales.loc[~sales["is_missing_customer"]].copy()
    if sales.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "recency",
                "frequency",
                "monetary",
                "recency_score",
                "frequency_score",
                "monetary_score",
                "rfm_score",
                "segment",
            ]
        )

    snapshot_date = sales["invoice_datetime"].max() + pd.Timedelta(days=1)
    rfm = (
        sales.groupby("customer_id", as_index=False)
        .agg(
            recency=("invoice_datetime", lambda values: (snapshot_date - values.max()).days),
            frequency=("invoice_no", "nunique"),
            monetary=("net_revenue", "sum"),
        )
    )
    rfm["recency_score"] = _score_series(rfm["recency"], ascending=False)
    rfm["frequency_score"] = _score_series(rfm["frequency"], ascending=True)
    rfm["monetary_score"] = _score_series(rfm["monetary"], ascending=True)
    rfm["rfm_score"] = (
        rfm["recency_score"].astype(str)
        + rfm["frequency_score"].astype(str)
        + rfm["monetary_score"].astype(str)
    )
    rfm["segment"] = rfm.apply(_segment_customer, axis=1)
    return rfm.sort_values(["monetary", "frequency"], ascending=False)


def build_segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    if rfm.empty:
        return pd.DataFrame(columns=["segment", "customers", "revenue", "avg_recency", "avg_frequency"])
    return (
        rfm.groupby("segment", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            revenue=("monetary", "sum"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )


def build_retention_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    sales = valid_sales(df)
    sales = sales.loc[~sales["is_missing_customer"]].copy()
    if sales.empty:
        return pd.DataFrame(columns=["cohort_month", "invoice_month", "period_number", "customers"])

    sales["invoice_period"] = sales["invoice_datetime"].dt.to_period("M")
    first_month = sales.groupby("customer_id")["invoice_period"].transform("min")
    sales["cohort_month"] = first_month.astype(str)
    period_number = (sales["invoice_period"].dt.year - first_month.dt.year) * 12
    period_number += sales["invoice_period"].dt.month - first_month.dt.month
    sales["period_number"] = period_number

    return (
        sales.groupby(["cohort_month", "invoice_month", "period_number"], as_index=False)
        .agg(customers=("customer_id", "nunique"))
        .sort_values(["cohort_month", "period_number"])
    )


def build_all_outputs(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rfm = build_rfm_segments(df)
    return {
        "cleaned": df,
        "kpis": build_kpis(df),
        "monthly": build_monthly_sales(df),
        "country": build_country_sales(df),
        "product": build_product_sales(df),
        "rfm": rfm,
        "segments": build_segment_summary(rfm),
        "retention": build_retention_cohorts(df),
    }


def _score_series(series: pd.Series, ascending: bool) -> pd.Series:
    if series.nunique(dropna=True) <= 1:
        return pd.Series(3, index=series.index)
    ranks = series.rank(method="first", ascending=ascending)
    return pd.qcut(ranks, q=5, labels=[1, 2, 3, 4, 5]).astype(int)


def _segment_customer(row: pd.Series) -> str:
    r = int(row["recency_score"])
    f = int(row["frequency_score"])
    m = int(row["monetary_score"])
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 4:
        return "Loyal Customers"
    if r >= 4 and f <= 2:
        return "New or Promising"
    if r <= 2 and f >= 4:
        return "At Risk"
    if r <= 2 and f <= 2:
        return "Hibernating"
    if m >= 4:
        return "High Value"
    return "Needs Attention"
