-- =====================================================================
-- fraud_risk_analysis.sql        (works in MySQL 8+ and SQLite 3.25+)
-- Credit Card Fraud & Transaction Risk Analysis
--
-- Purpose: the same business questions as the Python notebook and the
--          Power BI dashboard, answered in SQL, so all three can be
--          cross-checked (283,726 transactions, 473 fraud, 58,591.39 fraud value).
--
-- HOW TO LOAD: run 00_create_and_load.sql first (it creates the table
--   creditcard_clean from Data/fraud_cleaned.csv). Then run ONE query at a time
--   (click inside the query, press Ctrl+Enter in MySQL Workbench).
-- TESTED: all 9 queries were run on the real data and match Python and Power BI.
-- BAND EDGES: the CASE bands below are right-closed like pandas.cut
--   (0-10 means up to and including 10; 500+ means above 500). If your
--   notebook used different edges, change them in the view only.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. Helper view: one row per transaction with bands and periods
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_tx;
CREATE VIEW v_tx AS
SELECT
    `Time`   AS time_sec,
    `Amount` AS amount,
    `Class`  AS is_fraud,
    CASE WHEN `Amount` <= 10  THEN '1) 0 to 10'
         WHEN `Amount` <= 50  THEN '2) 10 to 50'
         WHEN `Amount` <= 100 THEN '3) 50 to 100'
         WHEN `Amount` <= 500 THEN '4) 100 to 500'
         ELSE                      '5) 500+' END AS amount_band,
    CASE WHEN `Time` < 21600  THEN '1) 0-6 hrs'
         WHEN `Time` < 43200  THEN '2) 6-12 hrs'
         WHEN `Time` < 64800  THEN '3) 12-18 hrs'
         WHEN `Time` < 86400  THEN '4) 18-24 hrs'
         WHEN `Time` < 108000 THEN '5) 24-30 hrs'
         WHEN `Time` < 129600 THEN '6) 30-36 hrs'
         WHEN `Time` < 151200 THEN '7) 36-42 hrs'
         ELSE                      '8) 42-48 hrs' END AS time_period
FROM creditcard_clean;


-- ---------------------------------------------------------------------
-- Q1. Headline KPIs
-- Business question: How often does fraud happen and how much money is it?
-- Keep four ideas apart: count, rate, amount, value rate.
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                                    AS total_transactions,
    SUM(is_fraud)                                               AS fraud_transactions,
    COUNT(*) - SUM(is_fraud)                                    AS legitimate_transactions,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 3)                  AS fraud_rate_pct,
    ROUND(SUM(amount), 2)                                       AS total_value,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) AS fraud_value,
    ROUND(100.0 * SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END)
          / SUM(amount), 3)                                     AS fraud_value_rate_pct,
    ROUND(AVG(amount), 2)                                       AS avg_amount,
    ROUND(AVG(CASE WHEN is_fraud = 1 THEN amount END), 2)       AS avg_fraud_amount,
    MAX(CASE WHEN is_fraud = 1 THEN amount END)                 AS max_fraud_amount
FROM v_tx;


-- ---------------------------------------------------------------------
-- Q2. Where is fraud concentrated by amount?  (CTE + window functions)
-- Business question: Which amount bands hold the most fraud CASES and
--                    which hold the most fraud MONEY?
-- ---------------------------------------------------------------------
WITH band AS (
    SELECT amount_band,
           COUNT(*)                                                    AS transactions,
           SUM(is_fraud)                                               AS fraud_cases,
           SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END)          AS fraud_value
    FROM v_tx
    GROUP BY amount_band
)
SELECT
    amount_band,
    transactions,
    fraud_cases,
    ROUND(100.0 * fraud_cases / transactions, 3)               AS fraud_rate_pct,
    ROUND(100.0 * fraud_cases / SUM(fraud_cases) OVER (), 1)   AS pct_of_fraud_cases,
    ROUND(fraud_value, 2)                                      AS fraud_value,
    ROUND(100.0 * fraud_value / SUM(fraud_value) OVER (), 1)   AS pct_of_fraud_value,
    ROUND((1.0 * fraud_cases / transactions)
          / (SUM(fraud_cases) OVER () * 1.0 / SUM(transactions) OVER ()), 2) AS times_average_rate
FROM band
ORDER BY amount_band;


-- ---------------------------------------------------------------------
-- Q3. Running total: how fast does fraud value build up with amount?
-- Business question: Which bands carry most of the loss?
-- ---------------------------------------------------------------------
WITH band AS (
    SELECT amount_band,
           SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) AS fraud_value
    FROM v_tx
    GROUP BY amount_band
)
SELECT
    amount_band,
    ROUND(fraud_value, 2)                                                    AS fraud_value,
    ROUND(100.0 * fraud_value / SUM(fraud_value) OVER (), 1)                 AS pct_of_fraud_value,
    ROUND(100.0 * SUM(fraud_value) OVER (ORDER BY amount_band DESC)
          / SUM(fraud_value) OVER (), 1)                                     AS cumulative_pct_from_top_band
FROM band
ORDER BY amount_band DESC;


-- ---------------------------------------------------------------------
-- Q4. Fraud rate by elapsed 6-hour period, ranked  (RANK + LAG)
-- Business question: Does fraud rate change across the data window?
-- Remember: Time is ELAPSED seconds, not clock time. Do not say "at night".
-- ---------------------------------------------------------------------
WITH period AS (
    SELECT time_period,
           COUNT(*)       AS transactions,
           SUM(is_fraud)  AS fraud_cases
    FROM v_tx
    GROUP BY time_period
)
SELECT
    time_period,
    transactions,
    fraud_cases,
    ROUND(100.0 * fraud_cases / transactions, 3)                         AS fraud_rate_pct,
    RANK() OVER (ORDER BY 1.0 * fraud_cases / transactions DESC)         AS rate_rank,
    ROUND(100.0 * fraud_cases / transactions
        - 100.0 * LAG(fraud_cases) OVER (ORDER BY time_period)
                / LAG(transactions) OVER (ORDER BY time_period), 3)      AS change_vs_prev_period_pts
FROM period
ORDER BY time_period;


-- ---------------------------------------------------------------------
-- Q5. Median amount: fraud vs legitimate  (ROW_NUMBER + COUNT window)
-- Business question: Is the TYPICAL fraud small, even though the average
--                    is lifted by a few big cases?
-- Portable median: rows whose position is within 0.5 of the middle.
-- ---------------------------------------------------------------------
WITH ranked AS (
    SELECT is_fraud,
           amount,
           ROW_NUMBER() OVER (PARTITION BY is_fraud ORDER BY amount) AS rn,
           COUNT(*)     OVER (PARTITION BY is_fraud)                 AS n
    FROM v_tx
)
SELECT
    CASE WHEN is_fraud = 1 THEN 'Fraud' ELSE 'Legitimate' END AS transaction_type,
    COUNT(*)                                                  AS transactions,
    ROUND(AVG(amount), 2)                                     AS average_amount,
    ROUND(AVG(CASE WHEN rn >= n / 2.0 AND rn <= n / 2.0 + 1 THEN amount END), 2) AS median_amount
FROM ranked
GROUP BY is_fraud;


-- ---------------------------------------------------------------------
-- Q6. "Check everything above X": workload vs fraud caught
-- Business question: If we review or step-up transactions above a given
--                    amount, how many customers are checked and how much
--                    fraud value is covered?  (supports recommendations 1 and 2)
-- ---------------------------------------------------------------------
WITH thresholds AS (
    SELECT 10 AS t UNION ALL SELECT 50 UNION ALL SELECT 100
    UNION ALL SELECT 200 UNION ALL SELECT 500
),
totals AS (
    SELECT SUM(is_fraud) AS all_fraud,
           SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) AS all_fraud_value,
           COUNT(*) AS all_tx
    FROM v_tx
)
SELECT
    th.t                                                               AS amount_above,
    SUM(CASE WHEN v.amount > th.t THEN 1 ELSE 0 END)                   AS transactions_flagged,
    ROUND(100.0 * SUM(CASE WHEN v.amount > th.t THEN 1 ELSE 0 END)
          / MAX(tt.all_tx), 2)                                         AS pct_of_all_transactions,
    SUM(CASE WHEN v.amount > th.t AND v.is_fraud = 1 THEN 1 ELSE 0 END) AS fraud_cases_caught,
    ROUND(100.0 * SUM(CASE WHEN v.amount > th.t AND v.is_fraud = 1 THEN v.amount ELSE 0 END)
          / MAX(tt.all_fraud_value), 1)                                AS pct_of_fraud_value_covered,
    ROUND(1.0 * SUM(CASE WHEN v.amount > th.t THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN v.amount > th.t AND v.is_fraud = 1 THEN 1 ELSE 0 END), 0), 0)
                                                                       AS flagged_per_fraud_found
FROM thresholds th
CROSS JOIN v_tx v
CROSS JOIN totals tt
GROUP BY th.t
ORDER BY th.t;


-- ---------------------------------------------------------------------
-- Q7. How concentrated are the biggest frauds?  (ROW_NUMBER)
-- Business question: How much of the fraud value sits in the top 5 cases?
-- ---------------------------------------------------------------------
WITH fraud_only AS (
    SELECT amount,
           ROW_NUMBER() OVER (ORDER BY amount DESC) AS rank_by_amount
    FROM v_tx
    WHERE is_fraud = 1
)
SELECT
    ROUND(SUM(CASE WHEN rank_by_amount <= 5 THEN amount ELSE 0 END), 2)           AS top5_fraud_value,
    ROUND(100.0 * SUM(CASE WHEN rank_by_amount <= 5 THEN amount ELSE 0 END)
          / SUM(amount), 1)                                                       AS top5_pct_of_fraud_value
FROM fraud_only;


-- ---------------------------------------------------------------------
-- Q8. Quiet hours: does fraud keep coming when genuine traffic drops?
--     (GROUP BY + RANK + SUM() OVER)
-- Business question: Are the high-rate time periods just a maths effect,
--                    or does fraud really stay steady when customers are fewer?
-- The 8 quietest hours are picked by TRANSACTION VOLUME only (not by fraud),
-- so the result is not cherry-picked. Time is ELAPSED hours: do not say "night".
-- ---------------------------------------------------------------------
WITH hourly AS (
    SELECT FLOOR(time_sec / 3600) AS elapsed_hour,
           COUNT(*)               AS transactions,
           SUM(is_fraud)          AS fraud_cases
    FROM v_tx
    GROUP BY FLOOR(time_sec / 3600)
),
ranked AS (
    SELECT elapsed_hour, transactions, fraud_cases,
           RANK() OVER (ORDER BY transactions) AS volume_rank      -- 1 = quietest hour
    FROM hourly
)
SELECT CASE WHEN volume_rank <= 8 THEN 'Quietest 8 hours' ELSE 'Other 40 hours' END AS hour_group,
       SUM(transactions)                                                  AS transactions,
       SUM(fraud_cases)                                                   AS fraud_cases,
       ROUND(100.0 * SUM(fraud_cases) / SUM(transactions), 3)             AS fraud_rate_pct,
       ROUND(100.0 * SUM(transactions) / SUM(SUM(transactions)) OVER (), 1) AS pct_of_transactions,
       ROUND(100.0 * SUM(fraud_cases) / SUM(SUM(fraud_cases)) OVER (), 1)   AS pct_of_fraud
FROM ranked
GROUP BY CASE WHEN volume_rank <= 8 THEN 'Quietest 8 hours' ELSE 'Other 40 hours' END
ORDER BY fraud_rate_pct DESC;


-- ---------------------------------------------------------------------
-- Q9. Exact-amount pattern: why are so many frauds tiny?   (CASE + subquery shares)
-- Business question: Do frauds cluster on a few exact amounts, such as 1.00,
--                    the way "card testing" does?
-- Read: pct_of_fraud far above pct_of_transactions = over-represented in fraud.
-- The data has no card ID, so this fits the pattern but cannot confirm it.
-- ---------------------------------------------------------------------
SELECT CASE WHEN amount = 1.00  THEN 'Exactly 1.00'
            WHEN amount = 0.00  THEN 'Exactly 0.00'
            WHEN amount = 99.99 THEN 'Exactly 99.99'
            ELSE 'Any other amount' END                                    AS amount_group,
       COUNT(*)                                                            AS transactions,
       SUM(is_fraud)                                                       AS fraud_cases,
       ROUND(100.0 * SUM(is_fraud) / (SELECT SUM(is_fraud) FROM v_tx), 1)  AS pct_of_fraud,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM v_tx), 2)            AS pct_of_transactions,
       ROUND(100.0 * SUM(is_fraud) / COUNT(*), 3)                          AS fraud_rate_pct
FROM v_tx
GROUP BY CASE WHEN amount = 1.00  THEN 'Exactly 1.00'
              WHEN amount = 0.00  THEN 'Exactly 0.00'
              WHEN amount = 99.99 THEN 'Exactly 99.99'
              ELSE 'Any other amount' END
ORDER BY fraud_cases DESC;
