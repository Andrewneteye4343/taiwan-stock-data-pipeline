import pandas as pd

from src.collector.fundamental_data import (
    parse_financial_data,
)


def test_parse_financial_data():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "12.34",
            "eps_ytd": "25.00",
            "bvps": "125.67",
        }
    ]

    result = parse_financial_data(raw_data)

    assert isinstance(result, pd.DataFrame)

    assert list(result.columns) == [
        "symbol",
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

    assert result.loc[0, "symbol"] == "2330"
    assert result.loc[0, "report_year"] == 2026
    assert result.loc[0, "report_quarter"] == 2

    assert result.loc[0, "eps"] == 12.34
    assert result.loc[0, "eps_ytd"] == 25.00
    assert result.loc[0, "bvps"] == 125.67

def test_parse_financial_data_multiple_records():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "10.50",
            "eps_ytd": "10.50",
            "bvps": "120.00",
        },
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "12.34",
            "eps_ytd": "22.84",
            "bvps": "125.67",
        },
        {
            "symbol": "2317",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "8.20",
            "eps_ytd": "8.20",
            "bvps": "95.50",
        },
        {
            "symbol": "2317",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "9.10",
            "eps_ytd": "17.30",
            "bvps": "98.20",
        },
    ]

    result = parse_financial_data(raw_data)

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 4

    assert list(result.columns) == [
        "symbol",
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

    # Parser sorts by symbol, year, quarter.

    # 2317 Q1
    assert result.loc[0, "symbol"] == "2317"
    assert result.loc[0, "report_year"] == 2026
    assert result.loc[0, "report_quarter"] == 1
    assert result.loc[0, "eps"] == 8.20
    assert result.loc[0, "eps_ytd"] == 8.20
    assert result.loc[0, "bvps"] == 95.50

    # 2317 Q2
    assert result.loc[1, "symbol"] == "2317"
    assert result.loc[1, "report_year"] == 2026
    assert result.loc[1, "report_quarter"] == 2
    assert result.loc[1, "eps"] == 9.10
    assert result.loc[1, "eps_ytd"] == 17.30
    assert result.loc[1, "bvps"] == 98.20

    # 2330 Q1
    assert result.loc[2, "symbol"] == "2330"
    assert result.loc[2, "report_year"] == 2026
    assert result.loc[2, "report_quarter"] == 1
    assert result.loc[2, "eps"] == 10.50
    assert result.loc[2, "eps_ytd"] == 10.50
    assert result.loc[2, "bvps"] == 120.00

    # 2330 Q2
    assert result.loc[3, "symbol"] == "2330"
    assert result.loc[3, "report_year"] == 2026
    assert result.loc[3, "report_quarter"] == 2
    assert result.loc[3, "eps"] == 12.34
    assert result.loc[3, "eps_ytd"] == 22.84
    assert result.loc[3, "bvps"] == 125.67

def test_parse_financial_data_invalid_values():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "-",
            "bvps": "-",
        },
        {
            "symbol": "2317",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "",
            "bvps": None,
        },
        {
            "symbol": "2454",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "1,234.56",
            "bvps": "987.65",
        },
    ]

    result = parse_financial_data(raw_data)

    assert isinstance(result, pd.DataFrame)

    # "-" should become NaN.
    assert pd.isna(result.loc[0, "eps"])
    assert pd.isna(result.loc[0, "bvps"])

    # Empty string and None should become NaN.
    assert pd.isna(result.loc[1, "eps"])
    assert pd.isna(result.loc[1, "bvps"])

    # Numeric strings containing commas
    # should be converted to numeric values.
    assert result.loc[2, "eps"] == 1234.56
    assert result.loc[2, "bvps"] == 987.65

def test_parse_financial_data_preserves_records_with_invalid_values():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "-",
            "bvps": "120.00",
        },
        {
            "symbol": "2317",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "8.20",
            "bvps": None,
        },
    ]

    result = parse_financial_data(raw_data)

    assert len(result) == 2

    # 2317
    assert result.loc[0, "symbol"] == "2317"
    assert result.loc[0, "report_year"] == 2026
    assert result.loc[0, "report_quarter"] == 2
    assert result.loc[0, "eps"] == 8.20
    assert pd.isna(result.loc[0, "bvps"])

    # 2330
    assert result.loc[1, "symbol"] == "2330"
    assert result.loc[1, "report_year"] == 2026
    assert result.loc[1, "report_quarter"] == 1
    assert pd.isna(result.loc[1, "eps"])
    assert result.loc[1, "bvps"] == 120.00

def test_parse_financial_data_missing_required_field():
    raw_data = [
        {
            "symbol": "2330",
            "report_quarter": "2",
            "eps": "12.34",
            "bvps": "125.67",
        }
    ]

    result = parse_financial_data(raw_data)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_parse_financial_data_missing_optional_value():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "2",
        }
    ]

    result = parse_financial_data(raw_data)

    assert len(result) == 1

    assert result.loc[0, "symbol"] == "2330"
    assert result.loc[0, "report_year"] == 2026
    assert result.loc[0, "report_quarter"] == 2

    assert pd.isna(result.loc[0, "eps"])
    assert pd.isna(result.loc[0, "bvps"])

def test_parse_financial_data_sorts_records():
    raw_data = [
        {
            "symbol": "2317",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "9.10",
            "bvps": "98.20",
        },
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "12.34",
            "bvps": "125.67",
        },
        {
            "symbol": "2317",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "8.20",
            "bvps": "95.50",
        },
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "10.50",
            "bvps": "120.00",
        },
    ]

    result = parse_financial_data(raw_data)

    assert list(
        zip(
            result["symbol"],
            result["report_year"],
            result["report_quarter"],
        )
    ) == [
        ("2317", 2026, 1),
        ("2317", 2026, 2),
        ("2330", 2026, 1),
        ("2330", 2026, 2),
    ]

def test_parse_financial_data_duplicate_records():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "10.50",
            "bvps": "120.00",
        },
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "10.80",
            "bvps": "121.50",
        },
    ]

    result = parse_financial_data(raw_data)

    assert len(result) == 1

    assert result.loc[0, "symbol"] == "2330"
    assert result.loc[0, "report_year"] == 2026
    assert result.loc[0, "report_quarter"] == 1

    # Duplicate records should keep the last record.
    assert result.loc[0, "eps"] == 10.80
    assert result.loc[0, "bvps"] == 121.50

def test_parse_financial_data_with_cumulative_eps():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "3.00",
            "eps_ytd": "3.00",
            "bvps": "120.00",
        },
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "4.00",
            "eps_ytd": "7.00",
            "bvps": "125.00",
        },
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "3",
            "eps": "5.00",
            "eps_ytd": "12.00",
            "bvps": "130.00",
        },
    ]

    result = parse_financial_data(raw_data)

    assert len(result) == 3

    assert result.loc[0, "eps"] == 3.00
    assert result.loc[0, "eps_ytd"] == 3.00

    assert result.loc[1, "eps"] == 4.00
    assert result.loc[1, "eps_ytd"] == 7.00

    assert result.loc[2, "eps"] == 5.00
    assert result.loc[2, "eps_ytd"] == 12.00

def test_parse_financial_data_with_dps():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "3.00",
            "eps_ytd": "3.00",
            "bvps": "120.00",
            "dps": "5.00",
        },
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "4.00",
            "eps_ytd": "7.00",
            "bvps": "125.00",
            "dps": "5.00",
        },
    ]

    result = parse_financial_data(raw_data)

    assert len(result) == 2

    assert result.loc[0, "symbol"] == "2330"
    assert result.loc[0, "report_quarter"] == 1
    assert result.loc[0, "dps"] == 5.00

    assert result.loc[1, "symbol"] == "2330"
    assert result.loc[1, "report_quarter"] == 2
    assert result.loc[1, "dps"] == 5.00

def test_parse_financial_data_missing_dps():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "12.34",
            "eps_ytd": "25.00",
            "bvps": "125.67",
        }
    ]

    result = parse_financial_data(raw_data)

    assert len(result) == 1

    assert result.loc[0, "symbol"] == "2330"
    assert pd.isna(result.loc[0, "dps"])

def test_parse_financial_data_invalid_dps():
    raw_data = [
        {
            "symbol": "2330",
            "report_year": "2026",
            "report_quarter": "1",
            "eps": "3.00",
            "eps_ytd": "3.00",
            "bvps": "120.00",
            "dps": "-",
        },
        {
            "symbol": "2317",
            "report_year": "2026",
            "report_quarter": "2",
            "eps": "8.20",
            "eps_ytd": "16.00",
            "bvps": "95.50",
            "dps": "",
        },
    ]

    result = parse_financial_data(raw_data)

    assert len(result) == 2

    assert pd.isna(result.loc[0, "dps"])
    assert pd.isna(result.loc[1, "dps"])