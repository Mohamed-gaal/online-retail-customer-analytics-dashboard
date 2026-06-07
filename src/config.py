from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_FILE = RAW_DIR / "online_retail.csv"
CLEANED_FILE = PROCESSED_DIR / "cleaned_transactions.csv"
KPI_FILE = PROCESSED_DIR / "kpis.csv"
MONTHLY_FILE = PROCESSED_DIR / "monthly_sales.csv"
COUNTRY_FILE = PROCESSED_DIR / "country_sales.csv"
PRODUCT_FILE = PROCESSED_DIR / "product_sales.csv"
RFM_FILE = PROCESSED_DIR / "rfm_segments.csv"
SEGMENT_FILE = PROCESSED_DIR / "segment_summary.csv"
RETENTION_FILE = PROCESSED_DIR / "retention_cohorts.csv"

OUTPUT_FILES = {
    "cleaned": CLEANED_FILE,
    "kpis": KPI_FILE,
    "monthly": MONTHLY_FILE,
    "country": COUNTRY_FILE,
    "product": PRODUCT_FILE,
    "rfm": RFM_FILE,
    "segments": SEGMENT_FILE,
    "retention": RETENTION_FILE,
}
