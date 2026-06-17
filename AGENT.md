# Agent Notes

## Project Context

This workspace is the first GitHub portfolio project in a planned data science portfolio series for Mohamed-gaal.

Current project: **Online Retail Customer Analytics Dashboard**.

Goal: showcase practical data cleaning, exploratory analysis, business visualization, customer segmentation, and a polished dashboard using the Kaggle Online Retail Transactions dataset.

Dataset chosen:

- Kaggle: <https://www.kaggle.com/datasets/fareselgohary003/online-retail-transactions-uci/data>
- Expected local path: `data/raw/online_retail.csv`
- Raw data should stay out of Git.

## Resume Instructions

When returning to this chat:

1. Check `git status --short --branch`.
2. Confirm whether `data/raw/online_retail.csv` exists.
3. If the raw file exists, run `python -m src.pipeline`.
4. Install dashboard dependencies from `requirements.txt` if needed.
5. Run `streamlit run app.py` for local QA.
6. Add dashboard screenshots to the README after visual review.
7. Connect GitHub remote once Mohamed provides the empty repo URL.

## Implementation Conventions

- Keep source code in `src/`.
- Keep one-click dashboard entrypoint at `app.py`.
- Keep raw data in `data/raw/` and processed dashboard tables in `data/processed/`.
- Avoid committing raw Kaggle data.
- Prefer clear analyst-facing names over clever abstractions.
- Add tests for cleaning and feature logic when behavior changes.

## Planned Portfolio Roadmap

Future portfolio projects can cover:

- Predictive modeling with a documented experiment workflow
- Time-series forecasting
- Geospatial analysis
- NLP text analytics
- Recommendation systems
- A capstone end-to-end analytics app

Each future project should include a strong README, reproducible environment, clear dataset citation, and a dashboard or interactive artifact when useful.
