# Power BI folder

Contains **`Credit_Card_Fraud_Risk_Dashboard.pbix`** (open with Power BI Desktop; GitHub cannot preview `.pbix` files). DAX measures and validation values are in [`DAX_Measures.md`](DAX_Measures.md).

## Pages

| Page | Contents |
|---|---|
| 1. Overview | 5 KPI cards, Fraud vs Legitimate donut, Fraud Rate by Transaction Amount, slicers `Amount_Band` and `Time_Period` |
| 2. Fraud Analysis | Fraud Rate by Elapsed Time, Fraud Frequency vs Financial Impact, Transaction Amount Distribution, Top 10 Fraudulent Transactions, same two slicers |
| 3. Insights & Risk Recommendations | Key findings and 5 headline recommendations (text) |

## Small polish checklist (about 15 minutes in Power BI Desktop)
These were found by reading the saved file. Tick them off, save, and re-export the screenshots in `Images/`.

- [ ] **Card title:** the card showing 58.59K is titled "Fraud Transaction". Rename to **"Fraud Transaction Value"** so it matches the README and KPI table.
- [ ] **Total Transactions card** shows "284K". Set Display units to **None** so it shows **283,726** (the number the README, SQL and Python all use).
- [ ] **Donut chart:** fraud is only 0.17%, so the fraud slice is invisible and its label reads "0K". Replace with a card, or keep it and add a note: "fraud is 1 in 600".
- [ ] **Elapsed-time note:** add a small text box under *Fraud Rate by Elapsed Time*: "Time = hours since the first transaction, not clock time."
- [ ] **Page 3 name:** the page tab is called "IR". Rename to **Insights & Risk Recommendations**. In the text box, add "1." before "Fraud is rare" so the numbering is consistent.
- [ ] **Screenshots:** `Images/dashboard_page1.png` shows charts that the saved file keeps on page 2. Re-export one screenshot per page so the images match the file.
- [ ] *(Optional)* Add a chart of **hourly transactions vs fraud rate** (from `Data/stat_results/stat_hourly_volume_and_fraud.csv`) to show the quiet-hours finding on the dashboard.
