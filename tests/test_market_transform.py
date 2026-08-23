import pandas as pd
import pytest

from src.etl.market_transform import (
    prepare_market_data,
)


def test_prepare_market_data_success():
    """
    Test that raw market records are converted
    into a DataFrame with stock metadata.
    """

    records = [
        {
            "symbol": "2330",
            "trade_date": "2026-08-21",
            "open": 1180.0,
            "high": 1190.0,
            "low": 1175.0,
            "close": 1185.0,
            "volume": 100000,
        }
    ]

    stocks = [
        {
            "symbol": "2330",
            "name": "台積電",
            "market": "TWSE",
            "industry": "半導體",
        }
    ]

    df = prepare_market_data(
        records=records,
        stocks=stocks,
    )

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert len(df) == 1

    assert df.loc[0, "symbol"] == "2330"

    assert df.loc[0, "market"] == "TWSE"

    assert df.loc[0, "industry"] == "半導體"


def test_prepare_market_data_multiple_stocks():
    """
    Test that metadata is correctly matched
    for multiple stocks.
    """

    records = [
        {
            "symbol": "2330",
            "trade_date": "2026-08-21",
            "close": 1185.0,
        },
        {
            "symbol": "2317",
            "trade_date": "2026-08-21",
            "close": 210.0,
        },
    ]

    stocks = [
        {
            "symbol": "2330",
            "name": "台積電",
            "market": "TWSE",
            "industry": "半導體",
        },
        {
            "symbol": "2317",
            "name": "鴻海",
            "market": "TWSE",
            "industry": "電子製造",
        },
    ]

    df = prepare_market_data(
        records=records,
        stocks=stocks,
    )

    assert len(df) == 2

    ts_mc = df[
        df["symbol"] == "2330"
    ].iloc[0]

    hon_hai = df[
        df["symbol"] == "2317"
    ].iloc[0]

    assert ts_mc["market"] == "TWSE"
    assert ts_mc["industry"] == "半導體"

    assert hon_hai["market"] == "TWSE"
    assert hon_hai["industry"] == "電子製造"


def test_prepare_market_data_empty_records():
    """
    Test that empty records raise ValueError.
    """

    stocks = [
        {
            "symbol": "2330",
            "name": "台積電",
            "market": "TWSE",
            "industry": "半導體",
        }
    ]

    with pytest.raises(
        ValueError,
        match="No market records provided",
    ):
        prepare_market_data(
            records=[],
            stocks=stocks,
        )


def test_prepare_market_data_missing_metadata_columns():
    """
    Test that missing stock metadata columns
    raise ValueError.
    """

    records = [
        {
            "symbol": "2330",
            "trade_date": "2026-08-21",
            "close": 1185.0,
        }
    ]

    stocks = [
        {
            "symbol": "2330",
            "name": "台積電",
            # market is intentionally missing
            "industry": "半導體",
        }
    ]

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        prepare_market_data(
            records=records,
            stocks=stocks,
        )


def test_prepare_market_data_unmatched_symbol():
    """
    Test that an unmatched symbol remains in the
    DataFrame but its metadata becomes NaN.
    """

    records = [
        {
            "symbol": "9999",
            "trade_date": "2026-08-21",
            "close": 100.0,
        }
    ]

    stocks = [
        {
            "symbol": "2330",
            "name": "台積電",
            "market": "TWSE",
            "industry": "半導體",
        }
    ]

    df = prepare_market_data(
        records=records,
        stocks=stocks,
    )

    assert len(df) == 1

    assert df.loc[0, "symbol"] == "9999"

    assert pd.isna(
        df.loc[0, "market"]
    )

    assert pd.isna(
        df.loc[0, "industry"]
    )