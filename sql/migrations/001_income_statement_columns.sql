-- 001_income_statement_columns.sql
-- Phase 1：fundamental_data 增加損益表欄位（與 load.py 的 INSERT 對齊）
-- 說明：v1.4.1 的 init.sql 缺少這些欄位，導致季報資料無法寫入。

ALTER TABLE fundamental_data
    ADD COLUMN IF NOT EXISTS revenue NUMERIC(20, 2),
    ADD COLUMN IF NOT EXISTS gross_profit NUMERIC(20, 2),
    ADD COLUMN IF NOT EXISTS operating_income NUMERIC(20, 2),
    ADD COLUMN IF NOT EXISTS net_income NUMERIC(20, 2);
