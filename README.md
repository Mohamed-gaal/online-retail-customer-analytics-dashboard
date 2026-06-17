# 🛒 Online Retail Customer Analytics Dashboard

A portfolio project demonstrating a complete analyst workflow built on the **Kaggle Online Retail Transactions** dataset — a real-world e-commerce transaction log containing cancelled invoices, missing customer IDs, invalid quantities, and country/product variation, making it a practical dataset for cleaning, segmentation, and dashboard design.

## 🎯 Project Goals

- Clean a messy, real-world-style transaction dataset using a reusable pipeline and modular source code
- Engineer business KPIs, RFM customer segments, monthly sales trends, and retention cohorts
- Build an interactive Streamlit dashboard for exploring revenue performance, product demand, customer quality, and repeat-purchase behavior

## 📁 Project Structure

```
online-retail-customer-analytics-dashboard/
├── app.py                          # Streamlit dashboard entrypoint
├── src/
│   ├── data_cleaning.py            # Column normalisation, type coercion, validity flags
│   ├── features.py                 # KPIs, monthly/country/product tables, RFM, cohorts
│   ├── pipeline.py                 # Orchestrates cleaning → feature → CSV export
│   └── config.py                   # Centralised file paths
├── scripts/
│   └── eda_summary.py              # CLI summary of data quality and top-line KPIs
├── tests/
│   └── test_pipeline.py            # Unit tests for cleaning and feature logic
├── data/
│   ├── raw/online_retail.csv       # Raw Kaggle dataset (Git-ignored)
│   └── processed/                  # Dashboard-ready CSVs (pipeline output)
├── assets/
│   └── dashboard-preview.png       # Dashboard screenshot
├── requirements.txt
└── README.md
```

## 🧹 Data Cleaning Summary

The raw dataset had the following issues, all addressed in `src/data_cleaning.py`:

| Issue | Fix |
|---|---|
| Mixed-case / inconsistent column names | Normalised to snake_case via `normalize_column_name()` |
| `CustomerID` stored as float (`12345.0`) | Converted to clean integer string; blanks set to `"Unknown"` |
| `InvoiceDate` stored as string | Parsed with `pd.to_datetime(..., dayfirst=True)` |
| `Quantity` and `UnitPrice` stored as strings | Coerced to numeric; non-parseable values set to NaN |
| Cancelled invoices (prefix `"C"`) | Flagged via `is_cancelled_invoice`; excluded from valid sales |
| Negative quantities / negative revenue rows | Flagged via `is_return_or_adjustment` |
| Rows with missing date, blank description, zero price | Excluded by `is_valid_sale` boolean filter |
| Whitespace and duplicate spacing in `Description` | Stripped and normalised |

**Result:** a cleaned DataFrame with validity flags, derived date parts (`invoice_date`, `invoice_month`, `invoice_year`, `invoice_hour`, `weekday`), and a `net_revenue` column set to `0` for non-valid rows.

## 📊 Key Feature Engineering

- **KPIs** — total revenue, orders, quantity, unique customers, unique products, countries, average order value, missing-customer row count, cancelled/invalid row count
- **Monthly sales** — revenue, orders, quantity, customers, and average order value per calendar month
- **Country & product tables** — top-N aggregations by revenue for geo and product breakdowns
- **RFM segmentation** — recency, frequency, monetary scores (1–5 quintile bins) mapped to 7 named segments: Champions, Loyal Customers, New or Promising, At Risk, Hibernating, High Value, Needs Attention
- **Retention cohorts** — month-0 acquisition cohort tracked across subsequent months to show repeat-purchase rates

## 📊 Dashboard Overview

![Online Retail Customer Analytics dashboard preview](assets/dashboard-preview.png)

Live Streamlit Cloud link: pending deployment.

The dashboard includes five tabs:

- **Sales** — KPI cards, monthly revenue trend, top countries by revenue
- **Products** — top products by revenue (bar chart + data table)
- **Customers** — RFM scatter map, segment revenue bar chart, segment summary table
- **Retention** — monthly cohort pivot table and interactive heatmap
- **Data Quality** — row counts, missing/cancelled breakdown, raw data preview

Sidebar filters for country and invoice date range apply across all views.

## 📦 Dataset

Download the CSV from Kaggle and save it at:

```text
data/raw/online_retail.csv
```

Kaggle dataset: <https://www.kaggle.com/datasets/fareselgohary003/online-retail-transactions-uci/data>

Original source: UCI Machine Learning Repository, Online Retail dataset.

The raw CSV is Git-ignored to keep the repository lightweight and license-conscious.

## 🚀 Running the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the cleaning & feature pipeline

```bash
python -m src.pipeline
```

This reads `data/raw/online_retail.csv`, runs cleaning and feature engineering, and writes all dashboard-ready CSVs to `data/processed/`.

### 3. Launch the dashboard

```bash
streamlit run app.py
```

The dashboard auto-runs the pipeline on first load if processed files are missing and the raw CSV is present.

### 4. Run the EDA summary (optional)

```bash
python scripts/eda_summary.py
```

Prints data quality counts, top-line KPIs, top countries, top products, and a monthly sales sample to the terminal.

### 5. Run tests

```bash
python -m unittest discover -s tests
```

## 🛠️ Tech Stack

- **Python**: pandas, numpy
- **Dashboard**: Streamlit
- **Visualisation**: Plotly
- **Testing**: unittest

## 📌 Notes

- Revenue figures are in the dataset's original currency (GBP, UK-based retailer).
- Transactions with missing `CustomerID` are retained in the cleaned dataset but excluded from customer-level analytics (RFM, cohorts).
- This project focuses on data cleaning, feature engineering, and dashboard design; no predictive model is included.
