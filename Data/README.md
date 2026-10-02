# Data folder

| File | Rows | What it is |
|---|---|---|
| `fraud_cleaned.csv` | 283,726 | Cleaned transaction-level table used by **Power BI**. Columns: `Time, Time_Hours, Elapsed_Hour, Time_Period, Time_Period_Order, Amount, Amount_Band, Amount_Band_Order, Class, Transaction_Type`. |
| `fraud_kpi_summary.csv` | 10 | The 10 KPIs with formulas |
| `fraud_by_amount_band.csv` | 5 | Transactions, fraud, fraud rate, fraud value, shares by amount band |
| `fraud_by_time_period.csv` | 8 | Same, by 6-hour **elapsed-time** period |
| `fraud_by_elapsed_hour.csv` | 48 | Same, by elapsed hour 0-47 |
| `fraud_by_transaction_type.csv` | 2 | Average, median, P25-P99, max amount for Fraud vs Legitimate |
| `fraud_feature_summary.csv` | 28 | Correlation of V1-V28 with `Class` (statistical only) |
| `top_fraud_transactions.csv` | 20 | Top 20 fraud transactions by amount |

## Raw dataset (not stored here)
The original `creditcard.csv` (about 144 MB) is too large for GitHub.
Download it from Kaggle: **"Credit Card Fraud Detection"** (ULB Machine Learning Group) and see the Kaggle page for the licence and citation details.

## Why `fraud_cleaned.csv` has no V1-V28 columns
To keep the file under GitHub's upload limits it contains only the interpretable columns. The notebook in `Python/` exports a **full** `fraud_cleaned.csv` that also includes V1-V28 (about 166 MB) if you want it.

## Cleaning applied
1,081 exact duplicate rows removed (19 were fraud): 284,807 rows -> 283,726 rows; fraud 492 -> 473. Zero-amount rows were kept.
