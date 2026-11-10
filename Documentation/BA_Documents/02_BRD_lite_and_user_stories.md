# 02. BRD-lite, Functional Requirements and User Stories

> A learning project on a public dataset. This shows how I would capture requirements if a real risk team asked for this dashboard.

## 1. Business Requirement Document (BRD-lite)

| Item | Detail |
|---|---|
| Project | Credit Card Fraud & Transaction Risk Analysis |
| Requested by (assumed) | Head of Risk and Fraud Operations Manager |
| Business problem | Fraud is rare, so normal volume reports hide it. The team needs to see frequency, money impact and concentration. |
| Goal | A trusted, validated view of fraud rate, fraud value and where risk sits, with practical recommendations |
| In scope | 283,726 cleaned transactions (about 2 days), KPIs, amount bands, elapsed-time periods, fraud vs legitimate amounts, dashboard, recommendations |
| Out of scope | Fraud prediction model, real-time scoring, merchant or customer analysis, chargeback cost |
| Data source | Kaggle "Credit Card Fraud Detection" (ULB Machine Learning Group) |
| Success criteria | (1) Python and Power BI KPI values match. (2) A risk manager can see fraud rate and fraud value rate within one minute. (3) Every recommendation has a success measure. |
| Assumptions | Class = 1 is confirmed fraud. Exact duplicate rows are data errors. Amount currency is the same for all rows. |
| Constraints | About 2 days of data, 473 fraud cases, anonymised features, no merchant, customer, channel or real timestamp |

## 2. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | Dashboard shows total transactions, fraud transactions, fraud rate, fraud value and fraud value rate as KPI cards | Must |
| FR-2 | Dashboard compares fraud cases and fraud value by amount band | Must |
| FR-3 | Dashboard shows fraud rate by elapsed time with a note that it is not clock time | Must (chart delivered; the on-page note is still to add, see `PowerBI/README.md`; the note is in the README and report) |
| FR-4 | Dashboard compares fraud and legitimate amounts (median and average) | Should |
| FR-5 | Slicers let the user filter by amount band and time period | Should (delivered; a Transaction_Type slicer was deliberately left out because choosing "Fraud" would force the fraud rate to 100%) |
| FR-6 | DAX measures are validated against the Python results | Must |
| FR-7 | Limitations are visible on the dashboard or the README | Must |

## 3. User stories and acceptance criteria

| ID | User story | Acceptance criteria |
|---|---|---|
| US-1 | As the **Head of Risk**, I want fraud rate and fraud value rate side by side, so that I do not mistake count for money. | Cards show 0.167% and 0.233% and match Python |
| US-2 | As the **Fraud Operations Manager**, I want to know where fraud cases are concentrated, so that I can plan analyst time. | Amount band view shows "0 to 10" holds 50.3% of cases |
| US-3 | As the **Head of Risk**, I want to know where fraud money sits, so that I can prioritise checks. | Amount band view shows "500+" holds 52.4% of fraud value |
| US-4 | As the **Card Product Manager**, I want to see how many genuine customers a rule would affect, so that I can judge friction. | Threshold table shows transactions flagged and flagged per fraud found |
| US-5 | As a **Senior Manager**, I want a one-page view that updates, so that I can monitor weekly. | Dashboard refreshes from the cleaned file and slicers work |
| US-7 | As the **Fraud Operations Manager**, I want to know if some time windows need extra monitoring, so that I can staff and set rules. | Quiet-hours result shows the 8 quietest elapsed hours hold 20.9% of fraud in 4.2% of transactions (SQL Q8, chart 10) |
| US-6 | As an **Analyst reviewing the work**, I want to know the limits, so that I do not over-read the results. | Limitations list states PCA features, elapsed time, 2-day window |

## 4. Traceability

| Requirement | Delivered in |
|---|---|
| FR-1 to FR-5 | `PowerBI/Credit_Card_Fraud_Risk_Dashboard.pbix` |
| FR-6 | `PowerBI/DAX_Measures.md` validation table, `Python/` notebook, `SQL/fraud_risk_analysis.sql` |
| FR-7 | README "Limitations" section |
| US-4 | `Python/02_statistical_and_threshold_analysis.py` and SQL Q6 |
| US-7 | SQL Q8, `Images/10_quiet_hours_fraud_rate.png` |
