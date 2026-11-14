# 01. Business Context, Domain Knowledge, KPIs and Stakeholders

## Business context
A **card issuer** (a bank or card company) earns fees and customer trust when cards are used. When a fraudulent transaction is approved, the issuer usually carries the loss, pays the cost of investigating it, and risks losing the customer. Fraud is **very rare** (about 1 in 600 transactions here), so it is easy to miss in normal reports, and treating every transaction as suspicious would annoy genuine customers.

This project helps a risk team answer: **how often does fraud happen, how much money is involved, and where is it concentrated?**

## How a card transaction and fraud check work (simple view)

```
Customer pays  ->  Authorisation (approve / decline)  ->  Fraud monitoring (alerts, rules)
                                                              |
                                          Alert queue -> Analyst review -> Confirm fraud / false alarm
                                                              |
                                         Confirmed fraud -> loss recorded, customer contacted, card blocked
```

## Glossary (simple words first)

| Term | Plain meaning |
|---|---|
| **Fraud rate** | Of every 100 transactions, how many are fraud (0.167 per 100 here) |
| **Fraud value rate** | Of every 100 currency units spent, how much is fraud (0.233 here) |
| **Class imbalance** | One outcome (legitimate) is far more common than the other (fraud) |
| **Accuracy trap** | Saying "everything is legitimate" is 99.83% accurate and catches no fraud, so accuracy is a poor KPI here |
| **False positive** | A genuine transaction wrongly flagged. It annoys the customer and costs review time |
| **False negative** | A fraud that slips through. It costs money |
| **Step-up authentication** | An extra check (for example a one-time password) only for risky transactions, instead of blocking them |
| **Card testing** | A fraudster makes a tiny charge (often 1.00) to check that a stolen card works before using it for larger amounts |
| **Velocity rule** | An automatic rule such as "many small transactions on one card in a short time" |
| **Alert queue** | The list of flagged transactions analysts review |
| **Chargeback** | When the customer disputes a charge and the money is taken back from the merchant or issuer |
| **PCA features (V1-V28)** | Numbers created by a mathematical transformation to hide the real fields. They have no business meaning |
| **Elapsed time** | Seconds since the first transaction in the file. It is not the time of day |

## KPI definitions

| KPI | Formula | Value |
|---|---|---|
| Total transactions | Count of rows | 283,726 |
| Fraud transactions | Count where Class = 1 | 473 |
| Fraud rate % | Fraud / Total x 100 | 0.167% |
| Total transaction value | Sum of Amount | 25,102,001.68 |
| Fraud transaction value | Sum of Amount where Class = 1 | 58,591.39 |
| Fraud value rate % | Fraud value / Total value x 100 | 0.233% |
| Average transaction amount | Total value / Total transactions | 88.47 |
| Average fraud amount | Fraud value / Fraud transactions | 123.87 |
| Legitimate transactions | Count where Class = 0 | 283,253 |
| Maximum fraud amount | Max Amount where Class = 1 | 2,125.87 |

These are the 10 KPIs in `Data/fraud_kpi_summary.csv`. Extra statistics (not KPIs): median fraud amount 9.82, median legitimate amount 22.00.

## Business questions this project answers

| # | Business question | Where answered |
|---|---|---|
| 1 | How often does fraud happen, and how much money is it? | KPIs, SQL Q1 |
| 2 | Which transaction sizes hold the most fraud cases, and which hold the most money? | SQL Q2-Q3, Power BI page 1 |
| 3 | If we check everything above X, what does it cost in customer checks? | SQL Q6, chart 12 |
| 4 | Is the time pattern real, or just fewer genuine customers? | SQL Q8, chart 10 |
| 5 | Why are so many frauds tiny? | SQL Q9, chart 11 |

## Business objectives (measurable)

| # | Objective | Success looks like |
|---|---|---|
| 1 | Understand fraud frequency and money impact | Fraud rate and fraud value rate reported separately and validated across Python, SQL (optional) and Power BI |
| 2 | Show where risk is concentrated | Fraud cases and fraud value compared by amount band and time period |
| 3 | Support a sensible review policy | A threshold view showing workload vs fraud covered |
| 4 | Give the risk team a monitoring view | A dashboard with 5 KPI cards and 2 slicers (Amount_Band, Time_Period) that match the Python numbers |

## Stakeholders

| Stakeholder | Interest | What they get |
|---|---|---|
| Fraud Operations Manager | Alert queue size and analyst time | Threshold view, workload per fraud found |
| Head of Risk | Total loss and where it sits | Fraud value rate, value concentration by band |
| Card Product Manager | Customer friction | Step-up vs block trade-off |
| Senior Management | Overall fraud exposure | Headline KPIs, one-page dashboard |
| Risk Analytics team | Data quality and next analysis | Limitations and data-capture recommendations |
