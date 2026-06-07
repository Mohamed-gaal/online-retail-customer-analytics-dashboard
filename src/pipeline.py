import argparse
from pathlib import Path

from src.config import OUTPUT_FILES, PROCESSED_DIR, RAW_FILE
from src.data_cleaning import clean_transactions, load_raw_transactions
from src.features import build_all_outputs


def run_pipeline(raw_path=RAW_FILE, output_dir=PROCESSED_DIR) -> dict:
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {raw_path}. Download the Kaggle CSV and save it there."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    raw = load_raw_transactions(raw_path)
    cleaned = clean_transactions(raw)
    outputs = build_all_outputs(cleaned)

    for name, frame in outputs.items():
        output_path = OUTPUT_FILES[name]
        frame.to_csv(output_path, index=False)

    return {
        "raw_rows": len(raw),
        "cleaned_rows": len(cleaned),
        "valid_sale_rows": int(cleaned["is_valid_sale"].sum()),
        "output_dir": str(output_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dashboard-ready Online Retail analytics tables.")
    parser.add_argument("--raw-path", default=str(RAW_FILE), help="Path to Kaggle Online Retail CSV.")
    args = parser.parse_args()
    summary = run_pipeline(raw_path=Path(args.raw_path))
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
