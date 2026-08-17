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