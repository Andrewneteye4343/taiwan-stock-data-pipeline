import pandas as pd

from src.database.query import get_latest_fundamental_data


def test_get_latest_fundamental_data():
    result = get_latest_fundamental_data("2330")

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 1

    assert list(result.columns) == [
        "symbol",
        "trade_date",
        "close",
        "report_year",
        "report_quarter",
        "eps",
        "eps_ytd",
        "bvps",
        "dps",
        "revenue",
        "gross_profit",
        "operating_income",
        "net_income",
    ]

    row = result.iloc[0]

    assert row["symbol"] == "2330"

def test_get_latest_fundamental_data_unknown_symbol():
    result = get_latest_fundamental_data("9999")

    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_get_latest_fundamental_data_without_fundamental_record(
    stock_without_fundamental,
):
    result = get_latest_fundamental_data(
        stock_without_fundamental
    )

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    
def test_get_latest_fundamental_data_returns_latest_report():
    result = get_latest_fundamental_data("2330")

    assert len(result) == 1

    row = result.iloc[0]

    assert row["report_year"] == 2026
    assert row["report_quarter"] == 2