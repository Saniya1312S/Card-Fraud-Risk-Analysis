# 06. Interview Preparation and Resume Points

## 30-second version
> "Fraud is very rare, about 1 in 600 card transactions, so normal reports hide it. I analysed 283,726 transactions in Python and Power BI. Small transactions make up half of the fraud cases but under 1% of fraud money, while transactions above 500 hold over half of the fraud value. I also found that fraud keeps arriving when genuine traffic drops: the 8 quietest hours hold 21% of fraud in 4% of transactions. So I recommended a risk-ranked review for large amounts, step-up checks in the middle range, and automated rules for small ones."

## 2-minute version
1. **Context:** A card issuer loses money when fraud is approved, but fraud is about 0.17% of transactions, so it is hard to see.
2. **Questions:** How often does fraud happen, how much money is involved, and where is it concentrated?
3. **Data:** ULB card transactions from Kaggle, 284,807 rows, 31 columns. I removed 1,081 exact duplicates (19 were fraud), leaving 283,726 rows and 473 fraud cases.
4. **What I did:** Cleaned and explored the data in Python, defined 10 KPIs, built an amount band and elapsed-time analysis, validated everything in SQL, tested the patterns statistically, and built a 3-page Power BI dashboard with DAX measures that I validated against Python.
5. **Findings:** Fraud rate 0.167%, fraud value rate 0.233%. Typical fraud is small (median 9.82 vs 22.00 for legitimate), but a few large cases lift the average (123.87). "0 to 10" holds 50.3% of fraud cases but 0.8% of fraud value. "500+" holds 52.4% of fraud value.
6. **Recommendations:** Risk-ranked queue above 500, step-up authentication above 100, automated rules for small frauds, weekly dashboard, and capture better data.
7. **Limits:** Only two days, anonymised features, elapsed time instead of clock time, no merchant or customer data. It is descriptive, not a prediction model.

## Likely questions and model answers

**Q1. Why is accuracy a bad KPI here?**
If I say "every transaction is legitimate" I am 99.83% accurate and catch zero fraud. So I track fraud rate, fraud value, fraud value rate and concentration instead.

**Q2. Fraud rate vs fraud value rate, what is the difference?**
Fraud rate counts cases (0.167%). Fraud value rate compares money (0.233%). The value rate is higher because the average fraud (123.87) is larger than the average transaction (88.47), pulled up by a few large cases. They answer different business questions: how often vs how costly.

**Q3. Why did you not build a machine learning model?**
The goal was risk reporting and monitoring for a business team, which is a descriptive task. Also, V1-V28 are anonymised, so a model would not give business-readable rules. A natural next step is a baseline model judged on precision-recall, not accuracy.

**Q4. What are V1 to V28?**
Anonymised features produced by a PCA transformation to protect customer data. They have no business meaning, so I only report that V17, V14 and V12 are statistically linked to fraud and recommend testing real attributes.

**Q5. Why not say "fraud happens at night"?**
`Time` is seconds elapsed since the first transaction, not clock time. I can only talk about elapsed periods.

**Q6. Why was fraud rate highest in two of the quietest periods?**
Partly a denominator effect, so I tested it. Fraud COUNT per hour does not follow traffic (Spearman 0.17, not significant), but the RATE falls as traffic rises (-0.33). The 8 quietest hours, picked by volume alone, hold 21% of fraud in 4% of transactions: a rate of 0.83% against 0.14%. They are two windows exactly 24 hours apart, but because `Time` is elapsed time I do not call them night. I recommend real timestamps before setting time rules.

**Q7. Why use the median for amounts?**
Amounts are skewed. A few large frauds pull the average up (123.87) while the typical fraud is only 9.82.

**Q8. How did you handle duplicates?**
I removed 1,081 rows that were identical on all 31 columns, including `Time` and all V features, which makes real repeats very unlikely. 19 of them were fraud. I documented the count.

**Q9. How do you know the dashboard is right?**
I validated the DAX measures against Python: 283,726 transactions, 473 fraud and 58,591.39 fraud value.

**Q10. Is the fraud rate difference between amount bands real or luck?**
I ran chi-square tests and calculated 95% confidence intervals. I compared "500+" with all other transactions: 0.373% (95% interval 0.27% to 0.52%) against 0.160% (0.15% to 0.18%), 2.3 times higher, chi-square p < 0.001. I compared it with the others, not the overall rate, because the overall rate already contains the 500+ band. The effect is modest (Cramer's V about 0.02) because fraud is so rare. Time periods have fewer cases each, so I treat them with more care.

**Q11. A risk manager asks: should we check everything above 500?**
Blanket review means about 268 checks per fraud found, with 99.6% hitting genuine customers. I would rank by risk and use step-up checks first, and pilot it before rollout.

**Q13. Why are so many frauds tiny?**
105 of 473 frauds (22%) are exactly 1.00, against 4.8% of genuine transactions; another 25 are exactly 0.00. In total 36% of fraud cases are 1.00 or less, yet they hold only 0.2% of fraud value. This fits card testing, where a fraudster checks a stolen card with a tiny charge. The data has no card ID, so I cannot confirm it. It supports velocity rules for small repeated amounts.

**Q14. Are fraud amounts really different from genuine ones?**
Yes, in the middle, not the average. A Mann-Whitney test gives p < 0.001 and the typical fraud is smaller (median 9.82 vs 22.00). The average is higher (123.87 vs 88.41) only because of a few large cases, which is why I use the median.

**Q15. How did you check your SQL?**
I loaded the same cleaned file into a database and confirmed every query gives the same numbers as Python and Power BI (283,726 / 473 / 58,591.39 / 0.167% / 0.233%).

**Q12. What would you do with more data?**
Add real timestamps, merchant, location, channel and a unique transaction ID, then look at velocity rules and build a baseline model measured by precision-recall.

## Resume bullets (choose 3-4)
- Analysed 283,726 card transactions (473 fraud cases) with Python, SQL and Power BI to quantify fraud frequency (0.167%) and financial impact (0.233% of value).
- Showed that fraud keeps arriving when genuine traffic drops (0.83% fraud rate in the 8 quietest hours vs 0.14%, p < 0.001) and that 22% of fraud cases are exactly 1.00, a possible card-testing pattern, supporting velocity-rule recommendations.
- Found that transactions in the "0 to 10" band hold 50.3% of fraud cases but 0.8% of fraud value, while the "500+" band holds 52.4% of fraud value, and turned this into 7 owner-assigned recommendations.
- Built a Power BI dashboard with DAX measures validated against Python, and used 9 SQL queries (CTEs, window functions, running totals, percentiles), confidence intervals and chi-square tests to cross-check the results.
- Wrote BA documentation (BRD, user stories, As-Is/To-Be process, risk register, stakeholder matrix) to turn the analysis into requirements for a fraud risk team.
