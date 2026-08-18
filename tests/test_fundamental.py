import pandas as pd

from src.indicators.fundamental import (
calculate_pe,
calculate_pb,
calculate_dividend_yield,
calculate_fundamentals,
)

def create_pe_test_data():
    return pd.DataFrame(
    [
    {
    "symbol": "2330",
    "trade_date": "2026-08-13",
    "close": 2400.0,
    "eps": 75.0,
    },
    {
    "symbol": "2330",
    "trade_date": "2026-08-14",
    "close": 2435.0,
    "eps": 75.0,
    },
    {
    "symbol": "2330",
    "trade_date": "2026-08-17",
    "close": 2400.0,
    "eps": 75.0,
    },
    ]
)

def test_pe():
    df = create_pe_test_data()

    """
    result = calculate_pe(df)

    assert "pe" in result.columns

    assert result.loc[0, "pe"] == 32.0
    assert round(result.loc[1, "pe"], 4) == 32.4667
    assert result.loc[2, "pe"] == 32.0
    """

def test_pe_zero_eps():
    df = pd.DataFrame(
    [
    {
    "symbol": "2330",
    "trade_date": "2026-08-17",
    "close": 2400.0,
    "eps": 0.0,
    }
    ]
)

"""
result = calculate_pe(df)

assert pd.isna(result.loc[0, "pe"])
"""

def test_pe_negative_eps():
    df = pd.DataFrame(
    [
    {
    "symbol": "2330",
    "trade_date": "2026-08-17",
    "close": 2400.0,
    "eps": -10.0,
    }
    ]
)

"""
result = calculate_pe(df)

assert pd.isna(result.loc[0, "pe"])
"""

def test_pe_multiple_stocks():
    df = pd.DataFrame(
    [
    {
    "symbol": "2330",
    "trade_date": "2026-08-17",
    "close": 2400.0,
    "eps": 75.0,
    },
    {
    "symbol": "2317",
    "trade_date": "2026-08-17",
    "close": 255.0,
    "eps": 12.75,
    },
    ]
)

"""
result = calculate_pe(df)

assert result.loc[0, "pe"] == 32.0
assert result.loc[1, "pe"] == 20.0
"""

def test_pb():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 2400.0,
                "bvps": 120.0,
            }
        ]
    )

    result = calculate_pb(df)

    assert result.loc[0, "pb"] == 20.0


def test_pb_zero_bvps():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 2400.0,
                "bvps": 0.0,
            }
        ]
    )

    result = calculate_pb(df)

    assert pd.isna(result.loc[0, "pb"])


def test_pb_negative_bvps():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 2400.0,
                "bvps": -50.0,
            }
        ]
    )

    result = calculate_pb(df)

    assert pd.isna(result.loc[0, "pb"])


def test_pb_multiple_stocks():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 2400.0,
                "bvps": 120.0,
            },
            {
                "symbol": "2317",
                "close": 255.0,
                "bvps": 85.0,
            },
        ]
    )

    result = calculate_pb(df)

    assert result.loc[0, "pb"] == 20.0
    assert result.loc[1, "pb"] == 3.0

def test_dividend_yield():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 100.0,
                "dps": 5.0,
            }
        ]
    )

    result = calculate_dividend_yield(df)

    assert result.loc[0, "dividend_yield"] == 5.0


def test_dividend_yield_zero_dps():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 100.0,
                "dps": 0.0,
            }
        ]
    )

    result = calculate_dividend_yield(df)

    assert result.loc[0, "dividend_yield"] == 0.0


def test_dividend_yield_invalid_close():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 0.0,
                "dps": 5.0,
            }
        ]
    )

    result = calculate_dividend_yield(df)

    assert pd.isna(result.loc[0, "dividend_yield"])


def test_dividend_yield_multiple_stocks():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 100.0,
                "dps": 5.0,
            },
            {
                "symbol": "2317",
                "close": 200.0,
                "dps": 10.0,
            },
        ]
    )

    result = calculate_dividend_yield(df)

    assert result.loc[0, "dividend_yield"] == 5.0
    assert result.loc[1, "dividend_yield"] == 5.0

def test_calculate_fundamentals():
    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 1000.0,
                "eps": 50.0,
                "bvps": 200.0,
                "dps": 20.0,
            },
            {
                "symbol": "2317",
                "close": 200.0,
                "eps": 10.0,
                "bvps": 100.0,
                "dps": 8.0,
            },
        ]
    )

    result = calculate_fundamentals(df)

    assert "pe" in result.columns
    assert "pb" in result.columns
    assert "dividend_yield" in result.columns

    assert result.loc[0, "pe"] == 20.0
    assert result.loc[0, "pb"] == 5.0
    assert result.loc[0, "dividend_yield"] == 2.0

    assert result.loc[1, "pe"] == 20.0
    assert result.loc[1, "pb"] == 2.0
    assert result.loc[1, "dividend_yield"] == 4.0