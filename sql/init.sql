CREATE TABLE IF NOT EXISTS stock_master (
    stock_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(20) NOT NULL,
    industry VARCHAR(100),
    listed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS daily_price (
    price_id BIGSERIAL PRIMARY KEY,

    stock_id INTEGER NOT NULL
        REFERENCES stock_master(stock_id),

    trade_date DATE NOT NULL,

    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),

    volume BIGINT,
    turnover NUMERIC(20, 2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(stock_id, trade_date)
);


CREATE TABLE IF NOT EXISTS market_index (
    index_id BIGSERIAL PRIMARY KEY,

    index_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,

    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),

    volume BIGINT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(index_code, trade_date)
);


CREATE TABLE IF NOT EXISTS technical_indicators (
    indicator_id BIGSERIAL PRIMARY KEY,

    stock_id INTEGER NOT NULL
        REFERENCES stock_master(stock_id),

    trade_date DATE NOT NULL,

    ma5 NUMERIC(12, 4),
    ma20 NUMERIC(12, 4),
    ma60 NUMERIC(12, 4),

    rsi14 NUMERIC(8, 4),

    macd NUMERIC(12, 6),
    macd_signal NUMERIC(12, 6),
    macd_hist NUMERIC(12, 6),

    volatility20 NUMERIC(12, 6),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(stock_id, trade_date)
);


CREATE TABLE IF NOT EXISTS pipeline_log (
    log_id BIGSERIAL PRIMARY KEY,

    pipeline_name VARCHAR(100) NOT NULL,

    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,

    status VARCHAR(20) NOT NULL,

    records_processed INTEGER DEFAULT 0,

    error_message TEXT
);


CREATE INDEX IF NOT EXISTS idx_daily_price_stock_date
ON daily_price(stock_id, trade_date);

CREATE INDEX IF NOT EXISTS idx_daily_price_date
ON daily_price(trade_date);

CREATE INDEX IF NOT EXISTS idx_indicators_stock_date
ON technical_indicators(stock_id, trade_date);