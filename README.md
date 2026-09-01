# Taiwan Stock Data Pipeline

> **Current Version: v2.0.0**

A Taiwan stock market data engineering and analytics platform built with **Python, PostgreSQL, Docker, and Streamlit**.

This project builds an end-to-end pipeline that collects, transforms, validates, stores, analyzes, and visualizes Taiwan stock market data. v2.0.0 is a maintainability-focused refactor: unified CLI, shared parsing utilities, TTM EPS standardization, quarterly scheduling, and fixed schema/load mismatches.

---

## 🏗 架構

```text
TWSE / Financial Data / Dividend CSV
        │
        ▼
Data Collection（src/api + src/collector）
        │
        ▼
Data Parsing & Validation（src/etl/validate）
        │
        ▼
PostgreSQL Database（src/database + sql/）
        │
        ▼
Business Logic / Indicators（src/indicators）
        │
        ▼
Streamlit Dashboard（dashboard/）
```

## 🚀 統一 CLI（v2.0 新增）

所有管線統一由 `src.cli` 進入：

```bash
python -m src.cli update              # 日行情 ETL（TWSE）
python -m src.cli fundamental         # 季報基本面（TWSE OpenAPI）
python -m src.cli fundamental --symbol 2330
python -m src.cli dividend            # 股利資料（CSV 匯入）
python -m src.cli dividend --csv data/dividends.csv
python -m src.cli realtime            # 即時報價單次觀測
python -m src.cli scheduler           # 自動排程器
```

Windows PowerShell 快速更新：

```powershell
.\scripts\update_data.ps1
```

## 🕐 自動化排程（v2.0 強化）

`scheduler/scheduler.py` 依市場時段運作：

| 時段 | 行為 |
|---|---|
| TRADING（09:00-13:30） | 每 `realtime_interval_seconds` 更新即時報價（不存 DB） |
| POST_CLOSE（13:30 後） | 依 `daily_pipeline_time` 執行日行情 ETL；失敗會依 `pipeline_retry_interval_minutes` 重試 |
| 季報觸發日 | 達 `fundamental_triggers` 設定日期後，自動執行季報＋股利管線（每日一次） |

`config/scheduler.yaml` 範例：

```yaml
scheduler:
  realtime_interval_seconds: 60
  daily_pipeline_time: "14:00"
  fundamental_triggers:      # 財報公佈期限後（Q1: 5/15、Q2: 8/14、Q3: 11/14、Q4: 次年 3/31）
    - "*-05-15"
    - "*-08-15"
    - "*-11-15"
    - "*-03-31"
  pipeline_retry_interval_minutes: 30
```

## 📐 統一量化標準（v2.0 重點）

季務（基本面）資料的計算標準在 v2.0 統一如下：

| 指標 | 標準 | 說明 |
|---|---|---|
| EPS（單季） | `fundamental_data.eps` | 當季單季 EPS（TWSE t187ap06 基本每股盈餘） |
| **PE** | **`close / EPS 基準`** | EPS 基準優先序：TTM（近四季累計）> 累計 EPS > 單季 EPS；TTM 資料不足四季時**逐列遞補**退回次一基準，不硬算也不留空 |
| PB | `close / BVPS` | BVPS 來自資產負債表（t187ap07 每股參考淨值） |
| 現金殖利率 | `DPS / close * 100` | DPS 來自股利資料 |
| 毛利率 / 營益率 / 淨利率 | 損益表欄位計算 | 有 revenue 等欄位時自動計算 |

> EPS 基準優先序：`eps_ttm` > `eps_ytd` > `eps`。避免「單季 vs 累計」混用造成 PE 不一致。

## 🗄 資料庫 Migration（重要）

v1.4.1 的 `fundamental_data` 表缺少損益表欄位，導致季報寫入失敗。v2.0 修正 `sql/init.sql`，**既有資料庫需執行 migration**：

```bash
# 在 postgres 容器內執行（或使用 psql）
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  -f /docker-entrypoint-initdb.d/../migrations/001_income_statement_columns.sql
```

`sql/migrations/001_income_statement_columns.sql` 內容為 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`（可重複執行）。

## 💰 股利資料（v2.0 改為 CSV 匯入）

MOPS（公開資訊觀測站）具反爬蟲機制（`FOR SECURITY REASONS`），requests 無法直接抓取。股利資料為年頻率且稀疏，v2.0 提供穩健的 CSV 匯入管線：

```bash
cp data/dividends.csv.example data/dividends.csv
# 編輯 data/dividends.csv 填入實際資料
python -m src.cli dividend
```

CSV 欄位：`symbol, dividend_year, cash_dividend, ex_dividend_date, payment_date`

> 自動抓取（如 Playwright 瀏覽器自動化）列為未來工作。

## ⚡ 即時報價

Dashboard 透過 TWSE 官方 API（mis.twse.com.tw）顯示即時報價，含價格變動、漲跌幅、成交量與最後成交時間；資料不落 DB。

## 🖥️ Dashboard

```bash
docker compose up -d dashboard
# http://localhost:8501/
```

顯示：即時報價、歷史價格、成交量、基本面（PE/PB/殖利率/三種利潤率）、技術指標、原始資料。

## 🧪 測試

```bash
# 需先設定 DATABASE_URL 與 TEST_DATABASE_URL（PostgreSQL）
pytest tests/ -q
```

v2.0 新增測試：TTM EPS、財報/股利驗證、股利 CSV 管線。

## 📁 專案結構（v2.0）

```
src/
├── cli.py                  # 統一命令列入口（新增）
├── api/twse.py             # TWSE OpenAPI（含指數退避重試，新增）
├── collector/
│   ├── parsing.py          # 共用解析工具（新增，消除重複）
│   ├── market_data.py      # 日行情抓取
│   ├── fundamental_data.py # 季報正規化/合併
│   └── dividend_data.py    # 股利解析（移除死碼 calculate_fundamentals）
├── pipelines/              # 管線編排（新增，取代 scripts 大腳本）
│   ├── market_daily.py
│   ├── fundamental.py
│   └── dividend.py
├── etl/                    # transform / validate / load（load 批次化）
├── indicators/fundamental.py  # TTM EPS + 利潤率
├── services/               # 查詢與指標服務
└── database/               # connection / query
scheduler/scheduler.py      # 自動排程（季報觸發 + 重試）
sql/init.sql                # 修正後的 schema
sql/migrations/             # migration SQL
scripts/run_pipeline.py     # 相容薄包裝（建議改用 CLI）
```

## ⚠️ 已知限制

- MOPS 反爬蟲：股利需 CSV 匯入（自動化列為未來工作）
- 掃描型/圖片 PDF 不在本專案範圍
- 歷史資料回溯需多次 API 呼叫（STOCK_DAY 為月粒度）
- dashboard 在 import 時即連線 DB（需要 DB 先就緒）

## API 使用與免責聲明

本專案為**個人學習與技術研究用途**。公開市場資料與 API 呼叫僅用於學習與測試；請遵守 TWSE 等資料來源的使用條款、授權條件與合理請求頻率。本專案**不構成投資建議**。
