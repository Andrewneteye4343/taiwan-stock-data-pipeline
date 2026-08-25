import os

import pytest

from sqlalchemy import create_engine
from sqlalchemy import text


@pytest.fixture
def test_engine():
    """
    Create a SQLAlchemy engine for the test database.

    The test database URL is provided through
    TEST_DATABASE_URL.
    """

    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL is not configured"
        )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    yield engine

    engine.dispose()


@pytest.fixture
def stock_without_fundamental(test_engine):
    """
    Create a test stock with daily price data
    but without fundamental data.

    The test data is created in stock_test_db
    through TEST_DATABASE_URL.
    """

    symbol = "9998"

    with test_engine.begin() as connection:

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

    with test_engine.begin() as connection:

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

@pytest.fixture
def pipeline_test_stock(test_engine):
    """
    Create a test stock for pipeline integration tests.

    The fixture uses the test database provided by
    TEST_DATABASE_URL.

    The test stock is automatically removed after
    the test completes.
    """

    symbol = "9997"

    with test_engine.begin() as connection:

        # --------------------------------------------------
        # Cleanup previous test data
        # --------------------------------------------------

        connection.execute(
            text(
                """
                DELETE FROM dividend_data
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
    # Test stock configuration
    # --------------------------------------------------

    stock = {
        "symbol": symbol,
        "name": "測試成功股票",
        "market": "TWSE",
        "industry": "測試業",
        "enabled": True,
    }

    # Return stock configuration to the test
    yield stock

    # --------------------------------------------------
    # Cleanup after test
    # --------------------------------------------------

    with test_engine.begin() as connection:

        connection.execute(
            text(
                """
                DELETE FROM dividend_data
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

@pytest.fixture
def scheduler_test_dependencies(
    monkeypatch,
):
    """
    Provide mocked dependencies for scheduler unit tests.

    The real pipeline and time.sleep are replaced so that
    scheduler tests do not execute the production pipeline
    or wait for real time.
    """

    pipeline_calls = []
    sleep_calls = []

    def mock_pipeline():
        pipeline_calls.append(True)

    def mock_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(
        "scheduler.scheduler.main",
        mock_pipeline,
    )

    monkeypatch.setattr(
        "scheduler.scheduler.time.sleep",
        mock_sleep,
    )

    return {
        "pipeline_calls": pipeline_calls,
        "sleep_calls": sleep_calls,
    }