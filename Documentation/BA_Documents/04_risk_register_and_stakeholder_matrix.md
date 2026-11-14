# 04. Risk Register and Stakeholder Matrix

## Risk register

| ID | Risk | Likelihood | Impact | Mitigation in this project |
|---|---|---|---|---|
| R1 | Only 473 fraud cases and about 2 days of data, so some rates are uncertain | High | High | 95% confidence intervals and chi-square tests added (`Python/02_...py`). Recommendations marked "pilot first". |
| R2 | `Time` is elapsed seconds, so "fraud at night" claims would be wrong | High | High | No clock-time claims. Time periods labelled as elapsed. |
| R3 | V1-V28 are anonymised PCA features with no business meaning | High | Medium | Described as statistical signals only. Recommendation 5 asks for real attributes. |
| R4 | A period with fewer genuine transactions shows a higher fraud rate (denominator effect) | High | Medium | Tested: fraud COUNT does not follow traffic (Spearman 0.17, p = 0.26) but the RATE does (-0.33, p = 0.02). Quiet hours chosen by volume only. |
| R5 | Removing 1,081 duplicate rows could remove real repeated purchases | Low | Medium | Duplicates were exact on all 31 columns including `Time` and V1-V28, so true repeats are very unlikely. Count (19 fraud) documented. |
| R6 | A blanket review rule would check many genuine customers (about 1 fraud per 268 reviews above 500) | High | High | Recommendation 1 says risk-ranked queue with step-up checks, not blanket review. |
| R7 | Dashboard numbers differ from Python | Low | High | DAX validated against Python (283,726 / 473 / 58,591.39). |
| R8 | Reading patterns as causes | Medium | Medium | Findings worded as "observed in this data". |
| R9 | Amount currency is not stated | Medium | Low | Amounts shown as "currency units" and not converted. |
| R10 | "Card testing" and "quiet window" findings are patterns, not proof (no card ID, no clock time) | High | Medium | Worded as "fits the pattern" and "low-traffic window". Recommendations say pilot first. |

## Stakeholder matrix

| Stakeholder | Influence | Interest | How to engage |
|---|---|---|---|
| Head of Risk | High | High | Manage closely. Share value concentration first. |
| Fraud Operations Manager | High | High | Manage closely. Share threshold and workload view. |
| Card Product Manager | Medium | High | Keep informed. Explain step-up vs block. |
| Senior Management | High | Medium | Keep satisfied with a one-page dashboard. |
| Risk Analytics team | Medium | High | Keep informed. Share limitations and data requests. |

## Who owns each recommendation

| # | Recommendation | Owner | Success measure |
|---|---|---|---|
| 1 | Risk-ranked priority queue above 500 | Fraud Operations Manager | % of fraud value caught; review time |
| 2 | Step-up authentication above 100 instead of blocking | Card Product Manager with Head of Risk | Fraud value rate; customer drop-off |
| 3 | Automated velocity rules for small, repeated amounts | Fraud Operations Manager | Fraud count in small bands; alert volume |
| 4 | Stricter monitoring in low-traffic windows, after real timestamps are captured | Risk Analytics team | Rate vs threshold |
| 5 | Test anomaly rules on real attributes | Risk Analytics team | Share of alerts that are truly fraud |
| 6 | Weekly KPI dashboard | Risk Analytics team | Dashboard refreshed on schedule |
| 7 | Capture merchant, location, channel, timestamp, unique ID | Data / IT team | Data completeness |
