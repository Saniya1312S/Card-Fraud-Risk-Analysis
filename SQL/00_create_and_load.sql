-- =====================================================================
-- 00_create_and_load.sql          (MySQL 8.0)       RUN THIS FIRST
-- Creates the database and table, then loads Data/fraud_cleaned.csv.
-- Expected result at the end: 283,726 rows and 473 fraud.
--
-- BEFORE YOU RUN:
--   1. Replace the file path below with the real path on YOUR computer
--      (use forward slashes, e.g. 'C:/Users/you/Card-Fraud-Risk-Analysis/Data/fraud_cleaned.csv').
--   2. LOAD DATA LOCAL needs local_infile switched on:
--        - MySQL Workbench: Edit Connection > Advanced > Others > add  OPTION_LOCAL_INFILE=1
--        - and run once:  SET GLOBAL local_infile = 1;
--   3. If loading fails, use Workbench's "Table Data Import Wizard" on the table instead.
-- =====================================================================
CREATE DATABASE IF NOT EXISTS fraud_risk;
USE fraud_risk;

DROP TABLE IF EXISTS creditcard_clean;
CREATE TABLE creditcard_clean (
    `Time`              DOUBLE,          -- seconds since the first transaction (elapsed, NOT clock time)
    Time_Hours          DOUBLE,
    Elapsed_Hour        INT,
    Time_Period         VARCHAR(20),
    Time_Period_Order   INT,
    `Amount`            DECIMAL(12,2),   -- currency not stated in the source data
    Amount_Band         VARCHAR(20),
    Amount_Band_Order   INT,
    `Class`             TINYINT,         -- 0 = legitimate, 1 = fraud
    Transaction_Type    VARCHAR(12)
);

LOAD DATA LOCAL INFILE 'Data/fraud_cleaned.csv'          -- <-- change to your full path
INTO TABLE creditcard_clean
FIELDS TERMINATED BY ','
IGNORE 1 LINES;

-- Check: must return 283726 and 473
SELECT COUNT(*) AS total_rows, SUM(`Class`) AS fraud_rows FROM creditcard_clean;
