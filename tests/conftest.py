import pytest

from sqlalchemy import text

from src.database.connection import engine


@pytest.fixture
def stock_without_fundamental():
    symbol = "9998"

    with engine.begin() as connection:

        # --------------------------------------------------
        # Cleanup previous test data
        # --------------------------------------------------

        connection.execute(
            text(
                """
                DELETE FROM fundamental_data
                WHERE stock_id IN (
                    SELECT stock_id
                    FROM stock_master
                    WHERE symbol = :symbol
                );
                """
            ),
            {"symbol": symbol},
        )

        connection.execute(
            text(
                """
                DELETE FROM daily_price
                WHERE stock_id IN (
                    SELECT stock_id
                    FROM stock_master
                    WHERE symbol = :symbol
                );
                """
            ),
            {"symbol": symbol},
        )

        connection.execute(
            text(
                """
                DELETE FROM stock_master
                WHERE symbol = :symbol;
                """
            ),
            {"symbol": symbol},
        )

        # --------------------------------------------------
        # Create test stock
        # --------------------------------------------------

        connection.execute(
            text(
                """
                INSERT INTO stock_master (
                    symbol,
                    name,
                    market,
                    industry,
                    listed_date
                )
                VALUES (
                    :symbol,
                    '測試股票',
                    'TWSE',
                    '測試業',
                    '2026-01-01'
                );
                """
            ),
            {"symbol": symbol},
        )

        # --------------------------------------------------
        # Create test daily price
        # --------------------------------------------------

        connection.execute(
            text(
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
                SELECT
                    stock_id,
                    '2026-08-21',
                    100.00,
                    105.00,
                    99.00,
                    103.00,
                    100000,
                    10300000
                FROM stock_master
                WHERE symbol = :symbol;
                """
            ),
            {"symbol": symbol},
        )

    # Return the symbol to the test
    yield symbol

    # ------------------------------------------------------
    # Cleanup after test
    # ------------------------------------------------------

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                DELETE FROM fundamental_data
                WHERE stock_id IN (
                    SELECT stock_id
                    FROM stock_master
                    WHERE symbol = :symbol
                );
                """
            ),
            {"symbol": symbol},
        )

        connection.execute(
            text(
                """
                DELETE FROM daily_price
                WHERE stock_id IN (
                    SELECT stock_id
                    FROM stock_master
                    WHERE symbol = :symbol
                );
                """
            ),
            {"symbol": symbol},
        )

        connection.execute(
            text(
                """
                DELETE FROM stock_master
                WHERE symbol = :symbol;
                """
            ),
            {"symbol": symbol},
        )