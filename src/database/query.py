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
    - EPS
    - EPS YTD
    - BVPS
    - DPS
    - revenue
    - gross profit
    - operating income
    - net income
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
                fd.dps,
                fd.revenue,
                fd.gross_profit,
                fd.operating_income,
                fd.net_income
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
            sm.name,

            lp.trade_date,
            lp.close,

            lf.report_year,
            lf.report_quarter,

            lf.eps,
            lf.eps_ytd,
            lf.bvps,
            lf.dps,

            lf.revenue,
            lf.gross_profit,
            lf.operating_income,
            lf.net_income

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

def get_fundamental_history(
    symbol: str,
) -> pd.DataFrame:
    """
    Get historical quarterly fundamental data
    for a given stock symbol.
    """

    query = text(
        """
        SELECT
            sm.symbol,
            sm.name,
            fd.report_year,
            fd.report_quarter,

            fd.eps,
            fd.eps_ytd,
            fd.bvps,
            fd.dps,

            fd.revenue,
            fd.gross_profit,
            fd.operating_income,
            fd.net_income

        FROM fundamental_data fd

        JOIN stock_master sm
            ON fd.stock_id = sm.stock_id

        WHERE sm.symbol = :symbol

        ORDER BY
            fd.report_year DESC,
            fd.report_quarter DESC;
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

def get_latest_dividend_data(
    symbol: str,
) -> pd.DataFrame:
    """
    Get the latest dividend data stored in PostgreSQL
    for a given stock symbol.

    Parameters
    ----------
    symbol : str
        Stock symbol.

    Returns
    -------
    pd.DataFrame
        Latest dividend record for the stock.
        Returns an empty DataFrame if no dividend
        data exists.
    """

    query = text(
        """
        SELECT
            sm.symbol,
            dd.dividend_year,
            dd.cash_dividend,
            dd.ex_dividend_date,
            dd.payment_date
        FROM dividend_data dd
        JOIN stock_master sm
            ON dd.stock_id = sm.stock_id
        WHERE sm.symbol = :symbol
        ORDER BY dd.dividend_year DESC
        LIMIT 1;
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

    return pd.DataFrame(
        rows,
        columns=[
            "symbol",
            "dividend_year",
            "cash_dividend",
            "ex_dividend_date",
            "payment_date",
        ],
    )