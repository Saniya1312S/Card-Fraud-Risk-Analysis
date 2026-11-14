# Power BI - data model and DAX measures

**Source table:** `fraud_cleaned` (from `Data/fraud_cleaned.csv`). Optional: `fraud_feature_summary` for the feature chart.

**Model settings**
- `Amount_Band` -> Sort by column -> `Amount_Band_Order`
- `Time_Period` -> Sort by column -> `Time_Period_Order`
- `Time`, `Time_Hours`, `Elapsed_Hour`, `Class` -> Summarization: Don't summarize

```DAX
-- Used by the dashboard visuals: Total Transactions, Fraud Transactions, Fraud Rate %,
-- Fraud Transaction Value, Fraud Value Rate %, Avg Transaction Amount, Median Amount,
-- P90 Amount, % of Fraud Transactions, % of Fraud Value.
-- The other measures (Legitimate, Total Value, Avg/Max Fraud Amount) are optional extras.

Total Transactions        = COUNTROWS(fraud_cleaned)
Fraud Transactions        = CALCULATE(COUNTROWS(fraud_cleaned), fraud_cleaned[Class] = 1)
Legitimate Transactions   = CALCULATE(COUNTROWS(fraud_cleaned), fraud_cleaned[Class] = 0)
Fraud Rate %              = DIVIDE([Fraud Transactions], [Total Transactions])

Total Transaction Value   = SUM(fraud_cleaned[Amount])
Fraud Transaction Value   = CALCULATE(SUM(fraud_cleaned[Amount]), fraud_cleaned[Class] = 1)
Fraud Value Rate %        = DIVIDE([Fraud Transaction Value], [Total Transaction Value])

Avg Transaction Amount    = AVERAGE(fraud_cleaned[Amount])
Avg Fraud Amount          = CALCULATE(AVERAGE(fraud_cleaned[Amount]), fraud_cleaned[Class] = 1)
Max Fraud Amount          = CALCULATE(MAX(fraud_cleaned[Amount]), fraud_cleaned[Class] = 1)
Median Amount             = MEDIAN(fraud_cleaned[Amount])
P90 Amount                = PERCENTILE.INC(fraud_cleaned[Amount], 0.9)

% of Fraud Transactions   = DIVIDE([Fraud Transactions],
                              CALCULATE([Fraud Transactions], ALL(fraud_cleaned[Amount_Band])))
% of Fraud Value          = DIVIDE([Fraud Transaction Value],
                              CALCULATE([Fraud Transaction Value], ALL(fraud_cleaned[Amount_Band])))
```

## Validation (dashboard cards must match the Python results)
| KPI | Expected |
|---|---|
| Total Transactions | 283,726 |
| Fraud Transactions | 473 |
| Fraud Rate % | 0.167% |
| Total Transaction Value | 25,102,001.68 |
| Fraud Transaction Value | 58,591.39 |
| Fraud Value Rate % | 0.233% |
| Avg Fraud Amount | 123.87 |
| Max Fraud Amount | 2,125.87 |

## Design notes
- No `Transaction_Type` slicer on the main page: selecting "Fraud" would force Fraud Rate to 100%.
- "Top 10 Fraudulent Transactions" table: visual filters `Transaction_Type = Fraud` and Top N 10 by `Amount`.
- Time visuals use **elapsed** time since the first transaction, not clock time.
