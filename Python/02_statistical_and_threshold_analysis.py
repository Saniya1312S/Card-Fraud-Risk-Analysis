"""
02_statistical_and_threshold_analysis.py
----------------------------------------
Extra checks for the Credit Card Fraud & Transaction Risk Analysis project.

It answers four questions a risk manager (or interviewer) is likely to ask:
  1. How SURE are we about each fraud rate?   -> 95% confidence intervals
  2. Do fraud rates REALLY differ by amount band / time period, or is it chance?
                                              -> chi-square tests
  3. Are fraud amounts really smaller than legitimate amounts?
                                              -> Mann-Whitney U test (amounts are skewed)
  4. If we review / step-up everything ABOVE an amount, what do we catch and what does it cost?
                                              -> threshold table (workload vs fraud value caught)
  5. Is the "500+" band really riskier than the rest?   -> 500+ vs all other transactions
  6. Is the time-period pattern just a quirk of volume? -> the 8 quietest hours vs the other 40
  7. Why are so many frauds tiny?                       -> exact-amount check (1.00 and 0.00 "card testing" pattern)

Run from the repo root:
    python Python/02_statistical_and_threshold_analysis.py

Input : Data/fraud_cleaned.csv  (283,726 rows; needs columns Time, Amount, Class)
Output: Data/stat_results/*.csv, Data/stat_results/stat_summary.txt
        Images/10_quiet_hours_fraud_rate.png, 11_card_testing_amounts.png, 12_threshold_workload.png
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu, spearmanr

INPUT = "Data/fraud_cleaned.csv"
OUT = "Data/stat_results"
IMG = "Images"
os.makedirs(OUT, exist_ok=True)
os.makedirs(IMG, exist_ok=True)
BLUE, RED, GREY, ORANGE = "#4C72B0", "#C44E52", "#A6A6A6", "#DD8452"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "figure.dpi": 110})

BAND_ORDER = ["0 to 10", "10 to 50", "50 to 100", "100 to 500", "500+"]
PERIOD_LABELS = [f"{i*6} to {(i+1)*6} hrs" for i in range(8)]


def wilson_ci(successes, n, z=1.96):
    """95% Wilson confidence interval for a proportion (safe when fraud counts are small)."""
    if n == 0:
        return (np.nan, np.nan)
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (centre - half, centre + half)


def rate_table(df, group_col, order=None):
    """Fraud rate with confidence interval for each group."""
    rows = []
    for g, part in df.groupby(group_col, observed=True):
        x, n = int(part["Class"].sum()), len(part)
        lo, hi = wilson_ci(x, n)
        rows.append({group_col: g, "transactions": n, "fraud": x,
                     "fraud_rate_pct": 100 * x / n,
                     "ci_low_pct": 100 * lo, "ci_high_pct": 100 * hi})
    t = pd.DataFrame(rows)
    if order:
        t[group_col] = pd.Categorical(t[group_col], categories=order, ordered=True)
        t = t.sort_values(group_col)
    return t


def chi_square(df, group_col):
    table = pd.crosstab(df[group_col], df["Class"])
    chi2, p, dof, _ = chi2_contingency(table)
    v = math.sqrt(chi2 / (table.values.sum() * (min(table.shape) - 1)))
    return chi2, p, dof, v


# ---------------- load and prepare ----------------
df = pd.read_csv(INPUT)

if "Amount_Band" not in df.columns:
    df["Amount_Band"] = pd.cut(df["Amount"], bins=[-0.01, 10, 50, 100, 500, np.inf],
                               labels=BAND_ORDER)
if "Time_Period" not in df.columns:
    df["Time_Period"] = pd.cut(df["Time"] / 3600, bins=np.arange(0, 54, 6), right=False,
                               labels=PERIOD_LABELS)

lines = []
n_all, f_all = len(df), int(df["Class"].sum())
lo, hi = wilson_ci(f_all, n_all)
lines.append(f"Transactions: {n_all:,} | Fraud: {f_all:,} | Fraud rate: {100*f_all/n_all:.3f}% "
             f"(95% CI {100*lo:.3f}% to {100*hi:.3f}%)")

# ---------------- 1 & 2. rates, CIs, chi-square ----------------
for col, order, title in [("Amount_Band", BAND_ORDER, "AMOUNT BAND"),
                          ("Time_Period", None, "ELAPSED TIME PERIOD (6-hour blocks)")]:
    t = rate_table(df, col, order)
    t.to_csv(os.path.join(OUT, f"stat_rate_by_{col.lower()}.csv"), index=False)
    chi2, p, dof, v = chi_square(df, col)
    lines.append(f"\nFRAUD RATE BY {title}")
    lines.append(t.assign(fraud_rate_pct=t["fraud_rate_pct"].map("{:.3f}".format),
                          ci_low_pct=t["ci_low_pct"].map("{:.3f}".format),
                          ci_high_pct=t["ci_high_pct"].map("{:.3f}".format)).to_string(index=False))
    lines.append(f"Chi-square = {chi2:.1f}, dof = {dof}, p = {p:.2e}, Cramer's V = {v:.3f}")
    lines.append("p < 0.05 means the rate differs between groups by more than chance. "
                 "Cramer's V says how strong (small values are normal when fraud is this rare). "
                 "Wide confidence intervals = few fraud cases = be careful.")

lines.append("\nNOTE on time periods: 'Time' is seconds elapsed since the first transaction, not clock time. "
             "The busiest and quietest periods differ a lot in legitimate volume, so a period with FEWER "
             "normal transactions can show a HIGHER fraud rate even when fraud cases are similar "
             "(a denominator effect).")

# ---------------- 3. fraud vs legitimate amounts ----------------
fa = df.loc[df["Class"] == 1, "Amount"]
la = df.loc[df["Class"] == 0, "Amount"]
u, p_mw = mannwhitneyu(fa, la, alternative="two-sided")
cles = u / (len(fa) * len(la))  # probability a random fraud amount is larger than a random legit amount
lines.append("\nFRAUD vs LEGITIMATE AMOUNTS")
lines.append(f"Median fraud = {fa.median():.2f} | median legitimate = {la.median():.2f} | "
             f"mean fraud = {fa.mean():.2f} | mean legitimate = {la.mean():.2f}")
lines.append(f"Mann-Whitney U p = {p_mw:.2e}; chance that a random fraud is larger than a random "
             f"legitimate transaction = {cles:.1%} (50% would mean no difference)")
lines.append("Why Mann-Whitney: amounts are very skewed, so a mean-based test would be misleading.")

# ---------------- 4. threshold table (workload vs value caught) ----------------
total_fraud_value = df.loc[df["Class"] == 1, "Amount"].sum()
rows = []
for thr in [10, 50, 100, 200, 500]:
    flagged = df["Amount"] > thr
    fr = df["Class"] == 1
    n_flag = int(flagged.sum())
    f_flag = int((flagged & fr).sum())
    rows.append({
        "rule": f"Amount > {thr}",
        "transactions_flagged": n_flag,
        "pct_of_all_transactions": 100 * n_flag / n_all,
        "fraud_cases_caught": f_flag,
        "pct_of_fraud_cases": 100 * f_flag / f_all,
        "pct_of_fraud_value": 100 * df.loc[flagged & fr, "Amount"].sum() / total_fraud_value,
        "flagged_per_fraud_found": n_flag / f_flag if f_flag else np.nan,
    })
thr_df = pd.DataFrame(rows)
thr_df.to_csv(os.path.join(OUT, "stat_threshold_table.csv"), index=False)
lines.append("\nTHRESHOLD TABLE: what a simple 'check everything above X' rule catches and costs")
lines.append(thr_df.round(2).to_string(index=False))
lines.append("Read it like this: a lower threshold catches more fraud value but checks many more genuine "
             "customers. 'flagged_per_fraud_found' is the review workload for each fraud found.")

# ---------------- 5. concentration ----------------
fs = df.loc[df["Class"] == 1, "Amount"].sort_values(ascending=False)
top5 = fs.head(5).sum() / fs.sum()
top10pct = fs.head(max(1, int(round(0.10 * len(fs))))).sum() / fs.sum()
lines.append("\nCONCENTRATION OF FRAUD VALUE")
lines.append(f"Top 5 frauds = {top5:.1%} of fraud value | top 10% of fraud cases = {top10pct:.1%} of fraud value")


# ---------------- 6. Is "500+" riskier than everything else? ----------------
big = df["Amount"] > 500
xb, nb_ = int(df.loc[big, "Class"].sum()), int(big.sum())
xr, nr = int(df.loc[~big, "Class"].sum()), int((~big).sum())
chi_b, p_b, _, _ = chi2_contingency(np.array([[xb, nb_ - xb], [xr, nr - xr]]), correction=False)
lb, hb = wilson_ci(xb, nb_)
lr, hr = wilson_ci(xr, nr)
lines.append("\n500+ BAND vs ALL OTHER TRANSACTIONS")
lines.append(f"500+: {xb}/{nb_:,} = {100*xb/nb_:.3f}% (95% CI {100*lb:.3f}% to {100*hb:.3f}%) | "
             f"all others: {xr}/{nr:,} = {100*xr/nr:.3f}% (95% CI {100*lr:.3f}% to {100*hr:.3f}%) | "
             f"{(xb/nb_)/(xr/nr):.1f}x higher | chi-square = {chi_b:.1f}, p = {p_b:.1e}")
lines.append("Meaning: the 500+ band is riskier than the rest by more than chance. (Compared with ALL OTHERS, "
             "not with the overall rate, because the overall rate already contains the 500+ band.)")

# ---------------- 7. Quiet hours: is the time pattern just volume? ----------------
df["hour"] = (df["Time"] // 3600).astype(int)
hourly = df.groupby("hour").agg(tx=("Class", "size"), fraud=("Class", "sum")).reset_index()
hourly["rate_pct"] = 100 * hourly["fraud"] / hourly["tx"]
rho_c, p_c = spearmanr(hourly["tx"], hourly["fraud"])
rho_r, p_r = spearmanr(hourly["tx"], hourly["rate_pct"])
quiet_hours = hourly.nsmallest(8, "tx")["hour"].tolist()      # chosen by VOLUME only, not by fraud
hourly["group"] = np.where(hourly["hour"].isin(quiet_hours), "Quietest 8 hours", "Other 40 hours")
grp = hourly.groupby("group")[["tx", "fraud"]].sum()
grp["rate_pct"] = 100 * grp["fraud"] / grp["tx"]
grp["pct_of_transactions"] = 100 * grp["tx"] / grp["tx"].sum()
grp["pct_of_fraud"] = 100 * grp["fraud"] / grp["fraud"].sum()
q, o = grp.loc["Quietest 8 hours"], grp.loc["Other 40 hours"]
chi_q, p_q, _, _ = chi2_contingency(np.array([[q["fraud"], q["tx"] - q["fraud"]], [o["fraud"], o["tx"] - o["fraud"]]]), correction=False)
grp.round(3).to_csv(os.path.join(OUT, "stat_quiet_hours.csv"))
hourly.to_csv(os.path.join(OUT, "stat_hourly_volume_and_fraud.csv"), index=False)
lines.append("\nQUIET HOURS: fraud keeps coming when genuine traffic drops")
lines.append(f"Quietest 8 elapsed hours (picked by volume alone): {sorted(quiet_hours)}")
lines.append(grp.round(3).to_string())
lines.append(f"Quiet hours hold {q['pct_of_fraud']:.1f}% of fraud in {q['pct_of_transactions']:.1f}% of transactions: "
             f"fraud rate {q['rate_pct']:.3f}% vs {o['rate_pct']:.3f}% ({q['rate_pct']/o['rate_pct']:.1f}x), chi-square = {chi_q:.1f}, p = {p_q:.1e}")
lines.append(f"Spearman, hourly volume vs fraud COUNT: rho = {rho_c:.2f}, p = {p_c:.2f} (no clear link: fraud does not follow customer traffic)")
lines.append(f"Spearman, hourly volume vs fraud RATE : rho = {rho_r:.2f}, p = {p_r:.2f} (busier hour -> lower rate)")
lines.append("Meaning: the high-rate periods are not just a maths quirk. Genuine traffic falls in two windows exactly 24 hours apart "
             "while fraud keeps arriving, so fraud becomes a much bigger share of traffic. 'Time' is elapsed time, so we cannot say "
             "these are night hours; we only see a repeating low-traffic window. Real timestamps are needed before setting time rules.")

fig, ax = plt.subplots(figsize=(10, 4.6))
colors = [ORANGE if h in quiet_hours else GREY for h in hourly["hour"]]
ax.bar(hourly["hour"], hourly["tx"], color=colors, width=0.8)
ax.set_xlabel("Elapsed hour since first transaction (0 to 47)"); ax.set_ylabel("Transactions in the hour")
ax2 = ax.twinx(); ax2.spines["right"].set_visible(True)
ax2.plot(hourly["hour"], hourly["rate_pct"], color=RED, lw=2, marker="o", ms=3)
ax2.set_ylabel("Fraud rate % (red line)", color=RED)
ax.set_title("Fraud rate spikes when genuine traffic is lowest (orange = 8 quietest hours)")
ax.text(0.99, 0.93, f"Quiet hours: {q['pct_of_fraud']:.0f}% of fraud in {q['pct_of_transactions']:.0f}% of transactions\n"
        f"Fraud rate {q['rate_pct']:.2f}% vs {o['rate_pct']:.2f}% in other hours", transform=ax.transAxes, ha="right", va="top", fontsize=9,
        bbox=dict(boxstyle="round", fc="white", ec=GREY))
plt.tight_layout(); plt.savefig(os.path.join(IMG, "10_quiet_hours_fraud_rate.png"), bbox_inches="tight"); plt.close()

# ---------------- 8. Why are so many frauds tiny? (exact amounts) ----------------
fr_amt, lg_amt = df.loc[df["Class"] == 1, "Amount"].round(2), df.loc[df["Class"] == 0, "Amount"].round(2)
rows = []
for label, val in [("Exactly 1.00", 1.00), ("Exactly 0.00", 0.00), ("Exactly 99.99", 99.99)]:
    rows.append({"amount": label, "fraud_cases": int((fr_amt == val).sum()),
                 "pct_of_fraud": 100 * (fr_amt == val).mean(), "pct_of_genuine": 100 * (lg_amt == val).mean(),
                 "fraud_rate_pct_at_this_amount": 100 * df.loc[df["Amount"].round(2) == val, "Class"].mean()})
amt = pd.DataFrame(rows)
amt.round(3).to_csv(os.path.join(OUT, "stat_exact_amount_pattern.csv"), index=False)
le1 = fr_amt <= 1.00
lines.append("\nEXACT-AMOUNT PATTERN (possible 'card testing')")
lines.append(amt.round(2).to_string(index=False))
lines.append(f"Frauds of 1.00 or less: {int(le1.sum())} = {100*le1.mean():.1f}% of fraud cases but only "
             f"{100*fr_amt[le1].sum()/fr_amt.sum():.2f}% of fraud value.")
lines.append("Meaning: about 1 in 5 frauds is exactly 1.00 against about 1 in 20 genuine transactions. Fraudsters often make a tiny "
             "charge to test whether a stolen card works. This data has no card ID, so it cannot be CONFIRMED; it fits the pattern and "
             "supports velocity rules (many tiny charges on one card in a short time) for the small bands.")
fig, ax = plt.subplots(figsize=(7.5, 4.3))
x = np.arange(len(amt)); w = 0.38
b1 = ax.bar(x - w/2, amt["pct_of_fraud"], w, color=RED, label="% of fraud cases")
b2 = ax.bar(x + w/2, amt["pct_of_genuine"], w, color=BLUE, label="% of genuine transactions")
for bars in (b1, b2):
    for r in bars: ax.text(r.get_x() + r.get_width()/2, r.get_height() + 0.4, f"{r.get_height():.1f}%", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(amt["amount"]); ax.set_ylabel("% of group")
ax.set_title("Fraud clusters on a few exact amounts (possible card testing)"); ax.legend(frameon=False)
plt.tight_layout(); plt.savefig(os.path.join(IMG, "11_card_testing_amounts.png"), bbox_inches="tight"); plt.close()

# ---------------- 9. Threshold chart (workload vs value covered) ----------------
fig, ax = plt.subplots(figsize=(7.5, 4.3))
ax.plot(thr_df["pct_of_all_transactions"], thr_df["pct_of_fraud_value"], color=RED, marker="o", lw=2)
for _, r in thr_df.iterrows():
    ax.annotate(r["rule"].replace("Amount > ", "> "), (r["pct_of_all_transactions"], r["pct_of_fraud_value"]),
                textcoords="offset points", xytext=(6, -12), fontsize=9)
ax.set_xlabel("% of ALL transactions that would be checked (workload)"); ax.set_ylabel("% of fraud VALUE covered")
ax.set_title("Check everything above X: workload vs fraud value covered"); ax.set_ylim(40, 104)
plt.tight_layout(); plt.savefig(os.path.join(IMG, "12_threshold_workload.png"), bbox_inches="tight"); plt.close()

text = "\n".join(lines)
print(text)
with open(os.path.join(OUT, "stat_summary.txt"), "w", encoding="utf-8") as f:
    f.write(text + "\n")
