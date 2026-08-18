import pandas as pd
from sqlalchemy import text

from src.database.connection import engine
from src.etl.load import load_fundamental_data


def test_load_fundamental_data():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 2,
                "eps": 12.34,
                "eps_ytd": 22.84,
                "bvps": 125.67,
                "dps": 5.00,
            }
        ]
    )

    processed_count = load_fundamental_data(df)

    assert processed_count == 1

    query = text(
        """
        SELECT
            sm.symbol,
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
          AND fd.report_year = :report_year
          AND fd.report_quarter = :report_quarter;
        """
    )

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 2,
            },
        ).fetchone()

    assert row is not None

    assert row.symbol == "2330"
    assert row.report_year == 2026
    assert row.report_quarter == 2
    assert float(row.eps) == 12.34
    assert float(row.eps_ytd) == 22.84
    assert float(row.bvps) == 125.67
    assert float(row.dps) == 5.00