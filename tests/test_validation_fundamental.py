import pandas as pd
import pytest

from src.etl.validate import (
    validate_dividend_data,
    validate_fundamental_data,
)


def test_validate_fundamental_data_valid():

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 2,
                "eps": 10.0,
                "bvps": 100.0,
            }
        ]
    )

    validate_fundamental_data(df)


def test_validate_fundamental_data_invalid_quarter():

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 5,
            }
        ]
    )

    with pytest.raises(
        ValueError,
        match="report_quarter",
    ):
        validate_fundamental_data(df)


def test_validate_fundamental_data_invalid_year():

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 1990,
                "report_quarter": 1,
            }
        ]
    )

    with pytest.raises(
        ValueError,
        match="report_year",
    ):
        validate_fundamental_data(df)


def test_validate_fundamental_data_duplicate():

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 1,
            },
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 1,
            },
        ]
    )

    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        validate_fundamental_data(df)


def test_validate_fundamental_data_negative_bvps():

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 1,
                "bvps": -5.0,
            }
        ]
    )

    with pytest.raises(
        ValueError,
        match="BVPS",
    ):
        validate_fundamental_data(df)


def test_validate_dividend_data_valid():

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "dividend_year": 2026,
                "cash_dividend": 5.0,
            }
        ]
    )

    validate_dividend_data(df)


def test_validate_dividend_data_negative():

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "dividend_year": 2026,
                "cash_dividend": -1.0,
            }
        ]
    )

    with pytest.raises(
        ValueError,
        match="cash_dividend",
    ):
        validate_dividend_data(df)


def test_validate_dividend_data_duplicate():

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "dividend_year": 2026,
                "cash_dividend": 5.0,
            },
            {
                "symbol": "2330",
                "dividend_year": 2026,
                "cash_dividend": 6.0,
            },
        ]
    )

    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        validate_dividend_data(df)
