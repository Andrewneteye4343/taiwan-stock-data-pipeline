import pandas as pd
from sqlalchemy import text

from src.database.connection import engine


def _load_records(
    df: pd.DataFrame,
    symbol_column: str,
    upsert_sql: str,
    bind_params,
    db_engine=None,
) -> int:
    """
    Batch upsert records with a single symbol lookup.

    Parameters
    ----------
    df : pd.DataFrame
        Data to load. Must contain symbol_column.

    symbol_column : str
        Column name holding the stock symbol.

    upsert_sql : str
        SQL with :stock_id and data bind parameters.

    bind_params : callable
        Function (row) -> dict of SQL bind parameters
        (without stock_id, which is added here).

    Returns
    -------
    int
        Number of processed records.
    """

    if db_engine is None:
        db_engine = engine

    if df.empty:
        return 0

    symbols = (
        df[symbol_column]
        .drop_duplicates()
        .tolist()
    )

    # ---------------------------------------------------------
    # 一次查詢所有 stock_id（取代逐列查詢的 N+1 模式）
    # ---------------------------------------------------------

    stock_id_sql = text(
        """
        SELECT stock_id, symbol
        FROM stock_master
        WHERE symbol = ANY(:symbols);
        """
    )

    with db_engine.connect() as connection:

        result = connection.execute(
            stock_id_sql,
            {"symbols": symbols},
        )

        stock_id_map = {
            row.symbol: row.stock_id
            for row in result.fetchall()
        }

    # ---------------------------------------------------------
    # 驗證所有 symbol 都存在
    # ---------------------------------------------------------

    for symbol in symbols:

        if symbol not in stock_id_map:

            raise ValueError(
                f"Stock symbol not found: {symbol}"
            )

    # ---------------------------------------------------------
    # 批次 upsert
    # ---------------------------------------------------------

    upsert = text(upsert_sql)

    processed_count = 0

    with db_engine.begin() as connection:

        params = [
            {
                **bind_params(row),
                "stock_id": stock_id_map[
                    row[symbol_column]
                ],
            }
            for _, row in df.iterrows()
        ]

        connection.execute(
            upsert,
            params,
        )

        processed_count = len(params)

    return processed_count


def load_stock_master(
    df: pd.DataFrame,
    db_engine=None,
) -> int:
    """
    Insert new stocks into stock_master.

    Existing stocks will not be modified.

    Returns
    -------
    int
        Number of newly inserted stocks.
    """

    if db_engine is None:
        db_engine = engine

    if df.empty:
        return 0

    required_columns = {
        "symbol",
        "name",
        "market",
        "industry",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing stock master columns: {missing_columns}"
        )

    stocks = (
        df[
            [
                "symbol",
                "name",
                "market",
                "industry",
            ]
        ]
        .drop_duplicates(
            subset=["symbol"]
        )
    )

    insert_sql = text(
        """
        INSERT INTO stock_master (
            symbol,
            name,
            market,
            industry
        )
        VALUES (
            :symbol,
            :name,
            :market,
            :industry
        )
        ON CONFLICT (symbol)
        DO NOTHING;
        """
    )

    inserted_count = 0

    with db_engine.begin() as connection:

        result = connection.execute(
            insert_sql,
            [
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "market": row["market"],
                    "industry": row["industry"],
                }
                for _, row in stocks.iterrows()
            ],
        )

        inserted_count = result.rowcount

    print(
        f"Stock master synchronized: "
        f"{inserted_count} new stock(s)."
    )

    return inserted_count


def load_daily_price(
    df: pd.DataFrame,
    db_engine=None,
) -> int:
    """
    Load daily stock price data into PostgreSQL.

    Existing records with the same
    (stock_id, trade_date) will be updated.

    Returns
    -------
    int
        Number of processed records.
    """

    if db_engine is None:
        db_engine = engine

    if df.empty:
        print("No data to load.")
        return 0

    upsert_sql = """
        INSERT INTO daily_price (
            stock_id,
            trade_date,
            open,
            high,
            low,
            close,
            volume,
            turnover
        )
        VALUES (
            :stock_id,
            :trade_date,
            :open,
            :high,
            :low,
            :close,
            :volume,
            :turnover
        )
        ON CONFLICT (
            stock_id,
            trade_date
        )
        DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            turnover = EXCLUDED.turnover;
    """

    def bind_params(row):

        return {
            "trade_date": row["trade_date"],
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],
            "turnover": row["turnover"],
        }

    processed_count = _load_records(
        df=df,
        symbol_column="symbol",
        upsert_sql=upsert_sql,
        bind_params=bind_params,
        db_engine=db_engine,
    )

    print(
        f"Successfully processed "
        f"{processed_count} daily price records."
    )

    return processed_count


def load_fundamental_data(
    df: pd.DataFrame,
    db_engine=None,
) -> int:
    """
    Load fundamental data into PostgreSQL.

    Existing records with the same
    (stock_id, report_year, report_quarter)
    will be updated.

    Returns
    -------
    int
        Number of processed records.
    """

    if db_engine is None:
        db_engine = engine

    if df.empty:
        print("No fundamental data to load.")
        return 0

    required_columns = {
        "symbol",
        "report_year",
        "report_quarter",
        "eps",
        "eps_ytd",
        "bvps",
        "dps",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing fundamental data columns: "
            f"{missing_columns}"
        )

    upsert_sql = """
        INSERT INTO fundamental_data (
            stock_id,
            report_year,
            report_quarter,
            eps,
            eps_ytd,
            bvps,
            dps,
            revenue,
            gross_profit,
            operating_income,
            net_income
        )
        VALUES (
            :stock_id,
            :report_year,
            :report_quarter,
            :eps,
            :eps_ytd,
            :bvps,
            :dps,
            :revenue,
            :gross_profit,
            :operating_income,
            :net_income
        )
        ON CONFLICT (
            stock_id,
            report_year,
            report_quarter
        )
        DO UPDATE SET
            eps = EXCLUDED.eps,
            eps_ytd = EXCLUDED.eps_ytd,
            bvps = EXCLUDED.bvps,
            dps = EXCLUDED.dps,
            revenue = EXCLUDED.revenue,
            gross_profit = EXCLUDED.gross_profit,
            operating_income = EXCLUDED.operating_income,
            net_income = EXCLUDED.net_income,
            updated_at = CURRENT_TIMESTAMP;
    """

    def bind_params(row):

        return {
            "report_year": row["report_year"],
            "report_quarter": row["report_quarter"],
            "eps": row["eps"],
            "eps_ytd": row["eps_ytd"],
            "bvps": row["bvps"],
            "dps": row["dps"],
            "revenue": row.get("revenue"),
            "gross_profit": row.get("gross_profit"),
            "operating_income": row.get("operating_income"),
            "net_income": row.get("net_income"),
        }

    processed_count = _load_records(
        df=df,
        symbol_column="symbol",
        upsert_sql=upsert_sql,
        bind_params=bind_params,
        db_engine=db_engine,
    )

    print(
        f"Successfully processed "
        f"{processed_count} fundamental records."
    )

    return processed_count


def load_dividend_data(
    df: pd.DataFrame,
    db_engine=None,
) -> int:
    """
    Load dividend data into PostgreSQL.

    Existing records with the same
    (stock_id, dividend_year) will be updated.

    Returns
    -------
    int
        Number of processed records.
    """

    if db_engine is None:
        db_engine = engine

    if df.empty:
        print("No dividend data to load.")
        return 0

    required_columns = {
        "symbol",
        "dividend_year",
        "cash_dividend",
        "ex_dividend_date",
        "payment_date",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing dividend data columns: "
            f"{missing_columns}"
        )

    upsert_sql = """
        INSERT INTO dividend_data (
            stock_id,
            dividend_year,
            cash_dividend,
            ex_dividend_date,
            payment_date
        )
        VALUES (
            :stock_id,
            :dividend_year,
            :cash_dividend,
            :ex_dividend_date,
            :payment_date
        )
        ON CONFLICT (
            stock_id,
            dividend_year
        )
        DO UPDATE SET
            cash_dividend = EXCLUDED.cash_dividend,
            ex_dividend_date = EXCLUDED.ex_dividend_date,
            payment_date = EXCLUDED.payment_date,
            updated_at = CURRENT_TIMESTAMP;
    """

    def bind_params(row):

        return {
            "dividend_year": row["dividend_year"],
            "cash_dividend": row["cash_dividend"],
            "ex_dividend_date": row["ex_dividend_date"],
            "payment_date": row["payment_date"],
        }

    processed_count = _load_records(
        df=df,
        symbol_column="symbol",
        upsert_sql=upsert_sql,
        bind_params=bind_params,
        db_engine=db_engine,
    )

    print(
        f"Successfully processed "
        f"{processed_count} dividend records."
    )

    return processed_count
