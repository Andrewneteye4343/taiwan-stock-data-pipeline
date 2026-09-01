import pandas as pd

from src.etl.transform import derive_single_quarter_eps


def test_derive_q1_equals_cumulative():
    """Q1 單季 = 累計（年初至今即當季）。"""

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 1,
                "eps_ytd": 10.5,
            }
        ]
    )

    result = derive_single_quarter_eps(df)

    assert result.loc[0, "eps"] == 10.5


def test_derive_single_quarter_from_cumulative():
    """Q2/Q3 單季 = 本季累計 − 上季累計。"""

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 1,
                "eps_ytd": 3.0,
            },
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 2,
                "eps_ytd": 7.0,
            },
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 3,
                "eps_ytd": 12.0,
            },
        ]
    )

    result = derive_single_quarter_eps(df)

    result = result.sort_values("report_quarter")

    assert result.iloc[0]["eps"] == 3.0
    assert result.iloc[1]["eps"] == 4.0   # 7 − 3
    assert result.iloc[2]["eps"] == 5.0   # 12 − 7


def test_derive_missing_previous_quarter():
    """無前一季資料時，eps 應為 None（由 PE 遞補鏈處理）。"""

    from sqlalchemy import create_engine, text

    # 空資料庫：查得到「無上季資料」的情境
    engine = create_engine("sqlite://")

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                CREATE TABLE stock_master (
                    stock_id INTEGER PRIMARY KEY,
                    symbol TEXT
                )
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE TABLE fundamental_data (
                    stock_id INTEGER,
                    report_year INTEGER,
                    report_quarter INTEGER,
                    eps_ytd REAL
                )
                """
            )
        )

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 2,
                "eps_ytd": 7.0,
            }
        ]
    )

    result = derive_single_quarter_eps(
        df,
        db_engine=engine,
    )

    assert pd.isna(result.loc[0, "eps"])
