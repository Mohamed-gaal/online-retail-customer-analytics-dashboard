import unittest

import pandas as pd

from src.data_cleaning import clean_transactions
from src.features import build_all_outputs, build_rfm_segments


class PipelineTests(unittest.TestCase):
    def sample_raw(self):
        return pd.DataFrame(
            [
                {
                    "InvoiceNo": "536365",
                    "StockCode": "85123A",
                    "Description": "WHITE HANGING HEART T-LIGHT HOLDER",
                    "Quantity": 6,
                    "InvoiceDate": "2010-12-01 08:26",
                    "UnitPrice": 2.55,
                    "CustomerID": 17850.0,
                    "Country": "United Kingdom",
                },
                {
                    "InvoiceNo": "C536379",
                    "StockCode": "D",
                    "Description": "Discount",
                    "Quantity": -1,
                    "InvoiceDate": "2010-12-01 09:41",
                    "UnitPrice": 27.50,
                    "CustomerID": 14527.0,
                    "Country": "United Kingdom",
                },
                {
                    "InvoiceNo": "536370",
                    "StockCode": "22728",
                    "Description": "ALARM CLOCK BAKELIKE PINK",
                    "Quantity": 24,
                    "InvoiceDate": "2010-12-01 08:45",
                    "UnitPrice": 3.75,
                    "CustomerID": None,
                    "Country": "France",
                },
            ]
        )

    def test_cleaning_flags_valid_sales_and_returns(self):
        cleaned = clean_transactions(self.sample_raw())
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(int(cleaned["is_valid_sale"].sum()), 2)
        self.assertTrue(cleaned.loc[1, "is_cancelled_invoice"])
        self.assertEqual(cleaned.loc[2, "customer_id"], "Unknown")
        self.assertAlmostEqual(cleaned.loc[0, "net_revenue"], 15.30)
        self.assertEqual(cleaned.loc[1, "net_revenue"], 0)

    def test_outputs_are_dashboard_ready(self):
        cleaned = clean_transactions(self.sample_raw())
        outputs = build_all_outputs(cleaned)
        self.assertIn("kpis", outputs)
        self.assertIn("monthly", outputs)
        self.assertIn("retention", outputs)
        self.assertEqual(outputs["kpis"].loc[0, "total_orders"], 2)
        self.assertGreater(outputs["product"].loc[0, "revenue"], 0)

    def test_rfm_excludes_unknown_customers(self):
        cleaned = clean_transactions(self.sample_raw())
        rfm = build_rfm_segments(cleaned)
        self.assertEqual(rfm["customer_id"].tolist(), ["17850"])
        self.assertIn("segment", rfm.columns)


if __name__ == "__main__":
    unittest.main()
