from src.config import CLEANED_FILE, RAW_FILE
from src.data_cleaning import clean_transactions, load_raw_transactions
from src.features import build_country_sales, build_kpis, build_monthly_sales, build_product_sales


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Place the Kaggle CSV at {RAW_FILE} before running this script.")

    raw = load_raw_transactions(RAW_FILE)
    cleaned = clean_transactions(raw)
    print("Data quality")
    print(f"Raw rows: {len(raw):,}")
    print(f"Valid sales rows: {cleaned['is_valid_sale'].sum():,}")
    print(f"Missing customer rows: {cleaned['is_missing_customer'].sum():,}")
    print(f"Cancelled or invalid rows: {(~cleaned['is_valid_sale']).sum():,}")
    print()

    print("KPIs")
    print(build_kpis(cleaned).to_string(index=False))
    print()

    print("Top countries")
    print(build_country_sales(cleaned, limit=10).to_string(index=False))
    print()

    print("Top products")
    print(build_product_sales(cleaned, limit=10).to_string(index=False))
    print()

    print("Monthly sample")
    print(build_monthly_sales(cleaned).head().to_string(index=False))
    print(f"\nCleaned output target: {CLEANED_FILE}")


if __name__ == "__main__":
    main()
