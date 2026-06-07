import re

import numpy as np
import pandas as pd


EXPECTED_COLUMNS = {
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_datetime",
    "UnitPrice": "unit_price",
    "CustomerID": "customer_id",
    "Country": "country",
}


def normalize_column_name(column: str) -> str:
    """Convert common Kaggle/UCI column names to snake_case."""
    column = str(column).strip()
    if column in EXPECTED_COLUMNS:
        return EXPECTED_COLUMNS[column]
    column = re.sub(r"(?<!^)(?=[A-Z])", "_", column).lower()
    column = re.sub(r"[^a-z0-9]+", "_", column).strip("_")
    aliases = {
        "invoice_no": "invoice_no",
        "invoice": "invoice_no",
        "stock_code": "stock_code",
        "product_code": "stock_code",
        "invoice_date": "invoice_datetime",
        "date": "invoice_datetime",
        "unit_price": "unit_price",
        "price": "unit_price",
        "customer_id": "customer_id",
    }
    return aliases.get(column, column)


def validate_columns(df: pd.DataFrame) -> None:
    required = set(EXPECTED_COLUMNS.values())
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(
            "Raw dataset is missing required columns after normalization: "
            + ", ".join(missing)
        )


def load_raw_transactions(path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="unicode_escape", sep=None, engine="python")
    df.columns = [normalize_column_name(col) for col in df.columns]
    validate_columns(df)
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [normalize_column_name(col) for col in cleaned.columns]
    validate_columns(cleaned)

    cleaned["invoice_no"] = cleaned["invoice_no"].astype(str).str.strip()
    cleaned["stock_code"] = cleaned["stock_code"].astype(str).str.strip()
    cleaned["description"] = (
        cleaned["description"].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    )
    cleaned["country"] = cleaned["country"].astype("string").str.strip().fillna("Unknown")
    cleaned["invoice_datetime"] = pd.to_datetime(cleaned["invoice_datetime"], errors="coerce", dayfirst=True)
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["unit_price"] = pd.to_numeric(cleaned["unit_price"], errors="coerce")

    cleaned["customer_id"] = cleaned["customer_id"].apply(_format_customer_id)
    cleaned["is_missing_customer"] = cleaned["customer_id"].eq("Unknown")
    cleaned["is_cancelled_invoice"] = cleaned["invoice_no"].str.upper().str.startswith("C")
    cleaned["gross_revenue"] = cleaned["quantity"] * cleaned["unit_price"]
    cleaned["is_return_or_adjustment"] = (cleaned["quantity"] < 0) | (cleaned["gross_revenue"] < 0)

    cleaned["is_valid_sale"] = (
        cleaned["invoice_datetime"].notna()
        & cleaned["description"].notna()
        & cleaned["description"].ne("")
        & cleaned["quantity"].gt(0)
        & cleaned["unit_price"].gt(0)
        & ~cleaned["is_cancelled_invoice"]
    )
    cleaned["net_revenue"] = np.where(cleaned["is_valid_sale"], cleaned["gross_revenue"], 0.0)

    cleaned["invoice_date"] = cleaned["invoice_datetime"].dt.date
    cleaned["invoice_month"] = cleaned["invoice_datetime"].dt.to_period("M").astype("string")
    cleaned["invoice_year"] = cleaned["invoice_datetime"].dt.year
    cleaned["invoice_hour"] = cleaned["invoice_datetime"].dt.hour
    cleaned["weekday"] = cleaned["invoice_datetime"].dt.day_name()

    return cleaned


def _format_customer_id(value) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip()
    if text in {"", "nan", "None"}:
        return "Unknown"
    try:
        number = float(text)
    except ValueError:
        return text
    if number.is_integer():
        return str(int(number))
    return text
