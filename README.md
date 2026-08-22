# Taiwan Stock Data Pipeline

> **Current Version: v1.2.2**

A Taiwan stock market data engineering and analytics platform built with **Python, PostgreSQL, Docker, and Streamlit**.

This project builds an end-to-end pipeline that collects, transforms, validates, stores, analyzes, and visualizes Taiwan stock market data.

The current version supports **historical market data, fundamental data, dividend data, technical indicators, and realtime stock quotes**, with automated testing across the major data-processing and business-logic modules.

## Update Market Data

Update the latest stock market data configured in config/stocks.yaml

`.\scripts\update_data.ps1`  

The pipeline will:

* Read stock symbols from config/stocks.yaml
* Fetch the latest market data from TWSE
* Validate and transform the data
* Load the data into PostgreSQL
* Avoid inserting duplicate records

## Visualize with Dashboard  

Enter web browser with `http://localhost:8501/`

---

## 🎯 Project Value

The goal of this project is to build a **modular and extensible stock data pipeline**, rather than simply retrieving stock prices from an API.

```text
TWSE / Financial Data
        │
        ▼
Data Collection
        │
        ▼
Data Parsing & Validation
        │
        ▼
PostgreSQL Database
        │
        ▼
Business Logic / Indicators
        │
        ▼
Streamlit Dashboard
```

## 🚀 Key Features
## 📊 Market Data Pipeline

The project provides a complete workflow for Taiwan stock market data:

Historical daily market data
Incremental data updates
PostgreSQL relational database
Stock Master / Daily Price data model
Primary Key / Foreign Key / Unique Constraints
Upsert mechanism to prevent duplicate records
ETL workflow

## 📈 Fundamental & Dividend Analysis

EPS
DPS
P/E Ratio
P/B Ratio
Dividend Yield
Latest fundamental data
Latest dividend data

Raw financial data and calculation logic are separated into independent service modules, making the analysis logic easier to test and extend.

## 📉 Technical Analysis

The technical analysis layer currently supports:

Price Change
Price Change %
Volume Ratio
Moving Average
KD
RSI
Wilder RSI
Multiple-window indicators

These indicators are calculated from historical market data and can be integrated into the dashboard layer.

## ⚡Realtime Stock Quote

Starting from v1.2.2, the dashboard integrates realtime stock quotes through the TWSE official API.

Realtime data includes:

Last Price
Open Price
High Price
Low Price
Previous Close
Price Change
Price Change %
Volume
Trade Time

The realtime service also implements:

API response parsing
Data normalization
Invalid / empty data handling
HTTP error handling
Realtime data caching
Configurable refresh intervals

## 🖥️ Dashboard

The project uses Streamlit to provide a web-based stock dashboard.

Users can select a stock and view:

⚡ Realtime Quote
📈 Historical Price
📊 Trading Volume
💰 Fundamental Data
📉 Technical Indicators
🗃️ Raw Data

The dashboard connects the backend data pipeline with the analysis layer and presents the results through an interactive web interface.

---

## API 使用與免責聲明

本專案為**個人學習與技術研究用途**所建立的台灣股票資料整理與分析專案。

目前專案中的公開市場資料與 API 呼叫，主要用於：

* 學習 Python、API 串接、資料解析與資料工程。
* 測試股票市場資料的取得、轉換、驗證與儲存流程。
* 研究 PostgreSQL、Docker、Streamlit 等技術整合。
* 在個人本機環境中進行程式測試與功能驗證。

## 使用限制

本專案目前不以以下用途為目的：

* 不提供公開的股票即時行情服務。
* 不向第三方收費。
* 不販售或轉售市場資料。
* 不重新發布或再散布所取得的市場資料。
* 不建立商業化資料服務。
* 不將本專案取得的資料宣稱為官方投資資訊。

## API 與資料來源

本專案可能使用台灣證券交易所（TWSE）等公開資訊來源進行個人學習與技術測試。

公開可取得的資料，其使用仍應遵守資料來源所公布的：

* 使用條款
* 授權條件
* API 使用規範
* 智慧財產權相關規定
* 其他適用之法律與規範

**本專案不主張或保證任何第三方資料來源允許無限制地存取、下載、儲存、修改、再利用或重新發布其資料。**

使用者應自行確認所使用資料來源當時有效的服務條款與授權條件。

## API 請求頻率

本專案在進行 API 測試時，應採取合理且保守的請求頻率，避免對資料來源的服務造成不必要的負載。

除非資料來源明確允許，否則本專案不應：

* 進行高頻率輪詢。
* 大量平行請求。
* 大量下載歷史資料。
* 以自動化方式長時間持續抓取資料。
* 以本專案建立公開的即時資料轉發服務。

若資料來源對請求頻率、流量或使用方式有明確限制，應以資料來源最新公布的規範為準。

## 資料正確性

本專案取得的市場資料僅供程式設計與學習用途。

資料可能存在：

* 延遲
* 暫時無法取得
* API 格式變更
* 資料缺漏
* 資料更新延遲
* 網路錯誤
* 程式解析錯誤

因此，本專案不保證資料的完整性、即時性、正確性或可用性。

## 投資免責聲明

本專案**不是投資顧問服務，也不構成任何投資、交易、財務或其他專業建議**。

專案中的股票價格、基本面資料、技術指標、計算結果、圖表及其他資訊，不應作為：

* 買進或賣出股票的依據
* 投資決策的唯一依據
* 財務規劃依據
* 任何形式的投資報酬保證

任何投資決策均應由使用者自行判斷並承擔相關風險。

## 第三方服務

本專案可能使用第三方所提供的 API、資料服務或開放資訊。

第三方服務的：

* 可用性
* API 格式
* 請求限制
* 授權條件
* 資料內容
* 服務條款

均可能隨時變更。

本專案維護者不保證第三方服務可以持續使用，也不對第三方服務的內容或可用性負責。

## 最後更新

本聲明應隨本專案實際使用的 API、資料來源及服務條款變化而更新。

如果本專案未來改變用途，例如：

* 對外提供服務
* 公開展示即時資料
* 商業化
* 收費
* 轉售資料
* 大規模資料收集

則應在實施前重新檢視相關資料來源的授權、使用條款及適用法律規範。

---
