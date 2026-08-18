import pandas as pd

from datetime import date

from sqlalchemy import text

from src.database.connection import engine


def get_latest_trade_date(symbol: str) -> date | None:
    """
    Get the latest trade date stored in PostgreSQL
    for a given stock symbol.

    Parameters
    ----------
    symbol : str
        Stock symbol.

    Returns
    -------
    date | None
        Latest stored trade date.
        Returns None if no price data exists.
    """

    query = text(
        """
        SELECT MAX(dp.trade_date) AS latest_trade_date
        FROM daily_price dp
        JOIN stock_master sm
            ON dp.stock_id = sm.stock_id
        WHERE sm.symbol = :symbol;
        """
    )

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {
                "symbol": symbol,
            },
        )

        row = result.fetchone()

    if row is None:
        return None

    return row.latest_trade_date

def get_latest_fundamental_data(
    symbol: str,
) -> pd.DataFrame:
    """
    Get the latest price and fundamental data
    for a given stock symbol.

    The returned data contains:
    - latest trading price
    - latest fundamental report
    - DPS from fundamental_data

    Parameters
    ----------
    symbol : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        One-row DataFrame containing the latest
        price and fundamental data.
    """

    query = text(
        """
        WITH latest_price AS (
            SELECT
                dp.stock_id,
                dp.trade_date,
                dp.close
            FROM daily_price dp
            JOIN stock_master sm
                ON dp.stock_id = sm.stock_id
            WHERE sm.symbol = :symbol
            ORDER BY dp.trade_date DESC
            LIMIT 1
        ),

        latest_fundamental AS (
            SELECT
                fd.stock_id,
                fd.report_year,
                fd.report_quarter,
                fd.eps,
                fd.eps_ytd,
                fd.bvps,
                fd.dps
            FROM fundamental_data fd
            JOIN stock_master sm
                ON fd.stock_id = sm.stock_id
            WHERE sm.symbol = :symbol
            ORDER BY
                fd.report_year DESC,
                fd.report_quarter DESC
            LIMIT 1
        )

        SELECT
            sm.symbol,
            lp.trade_date,
            lp.close,
            lf.report_year,
            lf.report_quarter,
            lf.eps,
            lf.eps_ytd,
            lf.bvps,
            lf.dps
        FROM stock_master sm
        JOIN latest_price lp
            ON sm.stock_id = lp.stock_id
        JOIN latest_fundamental lf
            ON sm.stock_id = lf.stock_id
        WHERE sm.symbol = :symbol;
        """
    )

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {
                "symbol": symbol,
            },
        )

        rows = result.fetchall()

        columns = result.keys()

    return pd.DataFrame(
        rows,
        columns=columns,
    )