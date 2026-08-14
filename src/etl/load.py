import pandas as pd
from sqlalchemy import text

from src.database.connection import engine


def load_stock_master(df: pd.DataFrame) -> int:
    """
    Insert new stocks into stock_master.

    Existing stocks will not be modified.

    Returns
    -------
    int
        Number of newly inserted stocks.
    """

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

    with engine.begin() as connection:

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


def load_daily_price(df: pd.DataFrame) -> int:
    """
    Load daily stock price data into PostgreSQL.

    Existing records with the same
    (stock_id, trade_date) will be updated.

    Returns
    -------
    int
        Number of processed records.
    """

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

    with engine.begin() as connection:

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