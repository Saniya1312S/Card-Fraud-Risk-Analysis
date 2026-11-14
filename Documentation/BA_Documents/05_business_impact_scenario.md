# 05. Business Impact Scenario (illustrative)

> This is a "what if", not a forecast. It uses only numbers from the analysis. The assumed catch rates are my own, so change them to test other cases.

## Facts from the data
- The "500+" band has **9,109 transactions**, of which **34 are fraud** (0.373%, about 1 fraud per 268 transactions).
- Those 34 frauds hold **30,682.65** of the **58,591.39** total fraud value (**52.4%**).
- Data covers about 2 days, so the figures below are for that window and should not be multiplied up to a year.

## What blanket review would mean
Reviewing every "500+" transaction means **9,109 checks to find 34 frauds** (about 268 checks per fraud, with 99.6% of checks hitting genuine customers). That is why Recommendation 1 asks for a **risk-ranked queue and step-up checks**, not blanket review.

## Value protected under assumed catch rates (500+ band only)

| Assumed share of fraud value stopped | Value stopped in the 2-day window |
|---|---|
| 20% | 6,136.53 |
| 40% | 12,273.06 |
| 60% | 18,409.59 |

Even the 20% case is about **10% of all fraud value** (6,136.53 / 58,591.39). The cost side (analyst time, customer friction) is **not** included because no cost data exists in the dataset.

## What to say in an interview
"I did not claim a precise ROI because the dataset has no cost, chargeback or customer-friction data. I showed the size of the prize and the workload, and said a pilot or back-test should set the real catch rate."
