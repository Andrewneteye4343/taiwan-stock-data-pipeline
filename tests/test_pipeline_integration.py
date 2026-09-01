import pandas as pd
import pytest

from sqlalchemy import text

# Phase 2 重構後：管線邏輯已遷移至 src.pipelines.market_daily
# （scripts/run_pipeline.py 僅為相容薄包裝）
from src.pipelines import market_daily as run_pipeline


def test_pipeline_failed(
    test_engine,
    monkeypatch,
):
    """
    Verify that a failed pipeline execution is recorded
    in the test database.

    The test must never write to the production database.
    """

    # --------------------------------------------------
    # Arrange
    # --------------------------------------------------

    def mock_load_stocks():
        raise RuntimeError(
            "Simulated pipeline failure"
        )

    monkeypatch.setattr(
        run_pipeline,
        "load_stocks",
        mock_load_stocks,
    )

    # --------------------------------------------------
    # Act
    # --------------------------------------------------

    with pytest.raises(
        RuntimeError,
        match="Simulated pipeline failure",
    ):
        run_pipeline.main(
            db_engine=test_engine,
        )

    # --------------------------------------------------
    # Assert
    # --------------------------------------------------

    with test_engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    pipeline_name,
                    status,
                    records_processed,
                    error_message,
                    end_time
                FROM pipeline_log
                ORDER BY log_id DESC
                LIMIT 1;
                """
            )
        )

        row = result.fetchone()

    assert row is not None

    assert row.pipeline_name == (
        run_pipeline.PIPELINE_NAME
    )

    assert row.status == "FAILED"

    assert row.records_processed == 0

    assert row.error_message == (
        "Simulated pipeline failure"
    )

    assert row.end_time is not None


def test_pipeline_success(
    test_engine,
    pipeline_test_stock,
    monkeypatch,
):
    """
    Verify that a successful pipeline execution:

    1. Writes SUCCESS status to pipeline_log.
    2. Processes daily price data.
    3. Writes daily price data to the test database.
    4. Does not depend on the production database.
    """

    # --------------------------------------------------
    # Arrange
    # --------------------------------------------------

    test_stock = pipeline_test_stock

    test_symbol = test_stock["symbol"]

    test_records = [
        {
            "symbol": test_symbol,
            "name": "測試成功股票",
            "trade_date": "2026-08-21",
            "open": 100.0,
            "high": 105.0,
            "low": 99.0,
            "close": 103.0,
            "volume": 100000,
            "turnover": 10300000,
        }
    ]

    def mock_load_stocks():
        return [test_stock]

    def mock_collect_stock_data(
        stock,
        client,
        today,
    ):
        return test_records, "success"

    monkeypatch.setattr(
        run_pipeline,
        "load_stocks",
        mock_load_stocks,
    )

    monkeypatch.setattr(
        run_pipeline,
        "collect_stock_data",
        mock_collect_stock_data,
    )

    # --------------------------------------------------
    # Act
    # --------------------------------------------------

    run_pipeline.main(
        db_engine=test_engine,
    )

    # --------------------------------------------------
    # Assert: pipeline_log
    # --------------------------------------------------

    with test_engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    pipeline_name,
                    status,
                    records_processed,
                    error_message,
                    end_time
                FROM pipeline_log
                ORDER BY log_id DESC
                LIMIT 1;
                """
            )
        )

        log_row = result.fetchone()

    assert log_row is not None

    assert log_row.pipeline_name == (
        run_pipeline.PIPELINE_NAME
    )

    assert log_row.status == "SUCCESS"

    assert log_row.records_processed == 1

    assert log_row.error_message is None

    assert log_row.end_time is not None

    # --------------------------------------------------
    # Assert: daily_price
    # --------------------------------------------------

    with test_engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    sm.symbol,
                    dp.trade_date,
                    dp.open,
                    dp.high,
                    dp.low,
                    dp.close,
                    dp.volume,
                    dp.turnover
                FROM daily_price dp
                JOIN stock_master sm
                    ON dp.stock_id = sm.stock_id
                WHERE sm.symbol = :symbol
                AND dp.trade_date = :trade_date;
                """
            ),
            {
                "symbol": test_symbol,
                "trade_date": "2026-08-21",
            },
        )

        price_row = result.fetchone()

    assert price_row is not None

    assert price_row.symbol == test_symbol

    assert str(price_row.trade_date) == "2026-08-21"

    assert float(price_row.open) == 100.0

    assert float(price_row.high) == 105.0

    assert float(price_row.low) == 99.0

    assert float(price_row.close) == 103.0

    assert price_row.volume == 100000

    assert float(price_row.turnover) == 10300000.0

def test_pipeline_no_data(
    test_engine,
    monkeypatch,
):
    """
    Verify that a pipeline execution with no new market
    data is recorded as NO_DATA.

    The test must use the test database and must not
    write to the production database.
    """

    # --------------------------------------------------
    # Arrange
    # --------------------------------------------------

    test_symbol = "9996"

    test_stock = {
        "symbol": test_symbol,
        "name": "測試無資料股票",
        "market": "TWSE",
        "industry": "測試業",
        "enabled": True,
    }

    def mock_load_stocks():
        return [test_stock]

    def mock_collect_stock_data(
        stock,
        client,
        today,
    ):
        return [], "no_new_data"

    monkeypatch.setattr(
        run_pipeline,
        "load_stocks",
        mock_load_stocks,
    )

    monkeypatch.setattr(
        run_pipeline,
        "collect_stock_data",
        mock_collect_stock_data,
    )

    # --------------------------------------------------
    # Act
    # --------------------------------------------------

    run_pipeline.main(
        db_engine=test_engine,
    )

    # --------------------------------------------------
    # Assert: pipeline_log
    # --------------------------------------------------

    with test_engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    pipeline_name,
                    status,
                    records_processed,
                    error_message,
                    end_time
                FROM pipeline_log
                ORDER BY log_id DESC
                LIMIT 1;
                """
            )
        )

        log_row = result.fetchone()

    assert log_row is not None

    assert log_row.pipeline_name == (
        run_pipeline.PIPELINE_NAME
    )

    assert log_row.status == "NO_DATA"

    assert log_row.records_processed == 0

    assert log_row.error_message is None

    assert log_row.end_time is not None