import pandas as pd
import pytest
from src.indicators.fundamental import calculate_fundamentals

from src.collector.dividend_data import (
    parse_dividend_data,
)


def test_parse_dividend_data():
    raw_data = [
        {
            "symbol": "2330",
            "dividend_year": "2026",
            "cash_dividend": "5.00",
            "ex_dividend_date": "2026-07-01",
            "payment_date": "2026-07-31",
        }
    ]

    result = parse_dividend_data(raw_data)

    assert isinstance(result, pd.DataFrame)

    assert list(result.columns) == [
        "symbol",
        "dividend_year",
        "cash_dividend",
        "ex_dividend_date",
        "payment_date",
    ]

    assert result.loc[0, "symbol"] == "2330"
    assert result.loc[0, "dividend_year"] == 2026
    assert result.loc[0, "cash_dividend"] == 5.00

    assert result.loc[0, "ex_dividend_date"] == pd.Timestamp(
        "2026-07-01"
    )

    assert result.loc[0, "payment_date"] == pd.Timestamp(
        "2026-07-31"
    )

def test_parse_dividend_data_multiple_records():
    raw_data = [
        {
            "symbol": "2330",
            "dividend_year": "2025",
            "cash_dividend": "4.50",
            "ex_dividend_date": "2025-07-01",
            "payment_date": "2025-07-31",
        },
        {
            "symbol": "2330",
            "dividend_year": "2026",
            "cash_dividend": "5.00",
            "ex_dividend_date": "2026-07-01",
            "payment_date": "2026-07-31",
        },
        {
            "symbol": "2317",
            "dividend_year": "2025",
            "cash_dividend": "5.20",
            "ex_dividend_date": "2025-07-15",
            "payment_date": "2025-08-15",
        },
        {
            "symbol": "2317",
            "dividend_year": "2026",
            "cash_dividend": "5.50",
            "ex_dividend_date": "2026-07-15",
            "payment_date": "2026-08-15",
        },
    ]

    result = parse_dividend_data(raw_data)

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 4

    assert list(result.columns) == [
        "symbol",
        "dividend_year",
        "cash_dividend",
        "ex_dividend_date",
        "payment_date",
    ]

    # 2317 - 2025
    assert result.loc[0, "symbol"] == "2317"
    assert result.loc[0, "dividend_year"] == 2025
    assert result.loc[0, "cash_dividend"] == 5.20

    # 2317 - 2026
    assert result.loc[1, "symbol"] == "2317"
    assert result.loc[1, "dividend_year"] == 2026
    assert result.loc[1, "cash_dividend"] == 5.50

    # 2330 - 2025
    assert result.loc[2, "symbol"] == "2330"
    assert result.loc[2, "dividend_year"] == 2025
    assert result.loc[2, "cash_dividend"] == 4.50

    # 2330 - 2026
    assert result.loc[3, "symbol"] == "2330"
    assert result.loc[3, "dividend_year"] == 2026
    assert result.loc[3, "cash_dividend"] == 5.00


def test_parse_dividend_data_invalid_values():
    raw_data = [
        {
            "symbol": "2330",
            "dividend_year": "2026",
            "cash_dividend": "-",
            "ex_dividend_date": "2026-07-01",
            "payment_date": "2026-07-31",
        },
        {
            "symbol": "2317",
            "dividend_year": "2026",
            "cash_dividend": "",
            "ex_dividend_date": "2026-07-15",
            "payment_date": "2026-08-15",
        },
        {
            "symbol": "2454",
            "dividend_year": "2026",
            "cash_dividend": None,
            "ex_dividend_date": "2026-07-20",
            "payment_date": "2026-08-20",
        },
        {
            "symbol": "2382",
            "dividend_year": "2026",
            "cash_dividend": "1,234.56",
            "ex_dividend_date": "2026-07-25",
            "payment_date": "2026-08-25",
        },
    ]

    result = parse_dividend_data(raw_data)

    assert len(result) == 4

    # 2317: empty string becomes NaN
    assert result.loc[0, "symbol"] == "2317"
    assert pd.isna(result.loc[0, "cash_dividend"])

    # 2330: "-" becomes NaN
    assert result.loc[1, "symbol"] == "2330"
    assert pd.isna(result.loc[1, "cash_dividend"])

    # 2382: comma-separated numeric value is parsed correctly
    assert result.loc[2, "symbol"] == "2382"
    assert result.loc[2, "cash_dividend"] == 1234.56

    # 2454: None becomes NaN
    assert result.loc[3, "symbol"] == "2454"
    assert pd.isna(result.loc[3, "cash_dividend"])


def test_parse_dividend_data_missing_optional_dates():
    raw_data = [
        {
            "symbol": "2330",
            "dividend_year": "2026",
            "cash_dividend": "5.00",
        },
        {
            "symbol": "2317",
            "dividend_year": "2026",
            "cash_dividend": "5.50",
            "ex_dividend_date": None,
            "payment_date": None,
        },
        {
            "symbol": "2454",
            "dividend_year": "2026",
            "cash_dividend": "6.00",
            "ex_dividend_date": "",
            "payment_date": "-",
        },
    ]

    result = parse_dividend_data(raw_data)

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 3

    # 2317: dates are explicitly None
    assert result.loc[0, "symbol"] == "2317"
    assert pd.isna(result.loc[0, "ex_dividend_date"])
    assert pd.isna(result.loc[0, "payment_date"])

    # 2330: dates are completely missing
    assert result.loc[1, "symbol"] == "2330"
    assert pd.isna(result.loc[1, "ex_dividend_date"])
    assert pd.isna(result.loc[1, "payment_date"])

    # 2454: dates are empty / "-"
    assert result.loc[2, "symbol"] == "2454"
    assert pd.isna(result.loc[2, "ex_dividend_date"])
    assert pd.isna(result.loc[2, "payment_date"])


def test_parse_dividend_data_missing_required_field():
    raw_data = [
        {
            "dividend_year": "2026",
            "cash_dividend": "5.00",
        }
    ]

    with pytest.raises(ValueError):
        parse_dividend_data(raw_data)


def test_parse_dividend_data_missing_dividend_year():
    raw_data = [
        {
            "symbol": "2330",
            "cash_dividend": "5.00",
        }
    ]

    with pytest.raises(ValueError):
        parse_dividend_data(raw_data)

def test_parse_dividend_data_sorts_records():
    raw_data = [
        {
            "symbol": "2330",
            "dividend_year": "2026",
            "cash_dividend": "5.00",
        },
        {
            "symbol": "2317",
            "dividend_year": "2025",
            "cash_dividend": "4.00",
        },
        {
            "symbol": "2330",
            "dividend_year": "2025",
            "cash_dividend": "4.50",
        },
        {
            "symbol": "2317",
            "dividend_year": "2026",
            "cash_dividend": "4.50",
        },
    ]

    result = parse_dividend_data(raw_data)

    assert len(result) == 4

    assert result.loc[0, "symbol"] == "2317"
    assert result.loc[0, "dividend_year"] == 2025

    assert result.loc[1, "symbol"] == "2317"
    assert result.loc[1, "dividend_year"] == 2026

    assert result.loc[2, "symbol"] == "2330"
    assert result.loc[2, "dividend_year"] == 2025

    assert result.loc[3, "symbol"] == "2330"
    assert result.loc[3, "dividend_year"] == 2026

def test_parse_dividend_data_duplicate_records():
    raw_data = [
        {
            "symbol": "2330",
            "dividend_year": "2026",
            "cash_dividend": "5.00",
        },
        {
            "symbol": "2330",
            "dividend_year": "2026",
            "cash_dividend": "5.00",
        },
        {
            "symbol": "2330",
            "dividend_year": "2025",
            "cash_dividend": "4.50",
        },
        {
            "symbol": "2317",
            "dividend_year": "2026",
            "cash_dividend": "5.50",
        },
    ]

    result = parse_dividend_data(raw_data)

    assert len(result) == 3

    # 2317 - 2026
    assert (
        len(
            result[
                (result["symbol"] == "2317")
                & (result["dividend_year"] == 2026)
            ]
        )
        == 1
    )

    # 2330 - 2025
    assert (
        len(
            result[
                (result["symbol"] == "2330")
                & (result["dividend_year"] == 2025)
            ]
        )
        == 1
    )

    # 2330 - 2026
    duplicate_rows = result[
        (result["symbol"] == "2330")
        & (result["dividend_year"] == 2026)
    ]

    assert len(duplicate_rows) == 1
    assert duplicate_rows.iloc[0]["cash_dividend"] == 5.00