import pandas as pd
import pytest
from sqlalchemy import text

from src.database.connection import engine
from src.etl.load import load_dividend_data


def test_load_dividend_data():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "dividend_year": 2026,
                "cash_dividend": 5.00,
                "ex_dividend_date": "2026-07-01",
                "payment_date": "2026-07-31",
            }
        ]
    )

    processed_count = load_dividend_data(df)

    assert processed_count == 1

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
          AND dd.dividend_year = :dividend_year;
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {
                "symbol": "2330",
                "dividend_year": 2026,
            },
        ).fetchone()

    assert row is not None

    assert row.symbol == "2330"
    assert row.dividend_year == 2026
    assert float(row.cash_dividend) == 5.00

    assert str(row.ex_dividend_date) == "2026-07-01"
    assert str(row.payment_date) == "2026-07-31"

def test_load_dividend_data_upsert():
    first_df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "dividend_year": 2027,
                "cash_dividend": 5.00,
                "ex_dividend_date": "2027-07-01",
                "payment_date": "2027-07-31",
            }
        ]
    )

    second_df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "dividend_year": 2027,
                "cash_dividend": 6.00,
                "ex_dividend_date": "2027-07-05",
                "payment_date": "2027-08-05",
            }
        ]
    )

    first_count = load_dividend_data(first_df)

    assert first_count == 1

    second_count = load_dividend_data(second_df)

    assert second_count == 1

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
          AND dd.dividend_year = :dividend_year;
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "symbol": "2330",
                "dividend_year": 2027,
            },
        ).fetchall()

    assert len(rows) == 1

    row = rows[0]

    assert row.symbol == "2330"
    assert row.dividend_year == 2027
    assert float(row.cash_dividend) == 6.00
    assert str(row.ex_dividend_date) == "2027-07-05"
    assert str(row.payment_date) == "2027-08-05"

def test_load_dividend_data_unknown_symbol():
    df = pd.DataFrame(
        [
            {
                "symbol": "9999",
                "dividend_year": 2027,
                "cash_dividend": 5.00,
                "ex_dividend_date": "2027-07-01",
                "payment_date": "2027-07-31",
            }
        ]
    )

    with pytest.raises(
        ValueError,
        match="Stock symbol not found: 9999",
    ):
        load_dividend_data(df)