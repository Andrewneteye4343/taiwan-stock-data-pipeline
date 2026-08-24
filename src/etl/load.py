import pandas as pd
from sqlalchemy import text

from src.database.connection import engine


def load_stock_master(
    df: pd.DataFrame,
    db_engine=None,
) -> int:
    """
    Insert new stocks into stock_master.

    Existing stocks will not be modified.

    Parameters
    ----------
    df : pd.DataFrame
        Stock data.

    db_engine : SQLAlchemy Engine, optional
        Database engine to use.
        If not provided, the production engine
        is used.

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

        for _, row in stocks.iterrows():

            result = connection.execute(
                insert_sql,
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "market": row["market"],
                    "industry": row["industry"],
                },
            )

            inserted_count += result.rowcount

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

    Parameters
    ----------
    df : pd.DataFrame
        Daily stock price data.

    db_engine : SQLAlchemy Engine, optional
        Database engine to use.
        If not provided, the production engine
        is used.

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

    upsert_sql = text(
        """
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
    )

    stock_id_sql = text(
        """
        SELECT stock_id
        FROM stock_master
        WHERE symbol = :symbol;
        """
    )

    processed_count = 0

    with db_engine.begin() as connection:

        for _, row in df.iterrows():

            result = connection.execute(
                stock_id_sql,
                {
                    "symbol": row["symbol"],
                },
            )

            stock = result.fetchone()

            if stock is None:
                raise ValueError(
                    f"Stock symbol not found: "
                    f"{row['symbol']}"
                )

            stock_id = stock.stock_id

            connection.execute(
                upsert_sql,
                {
                    "stock_id": stock_id,
                    "trade_date": row["trade_date"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                    "turnover": row["turnover"],
                },
            )

            processed_count += 1

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

    Parameters
    ----------
    df : pd.DataFrame
        Fundamental data.

    db_engine : SQLAlchemy Engine, optional
        Database engine to use.
        If not provided, the production engine
        is used.

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

    upsert_sql = text(
        """
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
    )

    stock_id_sql = text(
        """
        SELECT stock_id
        FROM stock_master
        WHERE symbol = :symbol;
        """
    )

    processed_count = 0

    with db_engine.begin() as connection:

        for _, row in df.iterrows():

            result = connection.execute(
                stock_id_sql,
                {
                    "symbol": row["symbol"],
                },
            )

            stock = result.fetchone()

            if stock is None:
                raise ValueError(
                    f"Stock symbol not found: "
                    f"{row['symbol']}"
                )

            stock_id = stock.stock_id

            connection.execute(
                upsert_sql,
                {
                    "stock_id": stock_id,
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
                },
            )

            processed_count += 1

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

    Parameters
    ----------
    df : pd.DataFrame
        Dividend data.

    db_engine : SQLAlchemy Engine, optional
        Database engine to use.
        If not provided, the production engine
        is used.

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

    upsert_sql = text(
        """
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
    )

    stock_id_sql = text(
        """
        SELECT stock_id
        FROM stock_master
        WHERE symbol = :symbol;
        """
    )

    processed_count = 0

    with db_engine.begin() as connection:

        for _, row in df.iterrows():

            result = connection.execute(
                stock_id_sql,
                {
                    "symbol": row["symbol"],
                },
            )

            stock = result.fetchone()

            if stock is None:
                raise ValueError(
                    f"Stock symbol not found: "
                    f"{row['symbol']}"
                )

            stock_id = stock.stock_id

            connection.execute(
                upsert_sql,
                {
                    "stock_id": stock_id,
                    "dividend_year": row["dividend_year"],
                    "cash_dividend": row["cash_dividend"],
                    "ex_dividend_date": row["ex_dividend_date"],
                    "payment_date": row["payment_date"],
                },
            )

            processed_count += 1

    print(
        f"Successfully processed "
        f"{processed_count} dividend records."
    )

    return processed_count