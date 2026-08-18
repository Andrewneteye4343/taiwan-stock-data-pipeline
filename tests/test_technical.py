import pandas as pd

from src.indicators.technical import (
    calculate_price_change,
    calculate_volume_ratio,
    calculate_moving_average,
    calculate_moving_averages,
    calculate_kd,
    calculate_rsi,
    calculate_rsis,
)


def create_test_data():
    return pd.DataFrame(
        [
            {
                "symbol": "2330",
                "trade_date": "2026-08-13",
                "close": 1115.0,
                "volume": 1000,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-14",
                "close": 1200.0,
                "volume": 2000,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-17",
                "close": 1260.0,
                "volume": 3000,
            },
        ]
    )


def test_price_change():
    df = create_test_data()

    result = calculate_price_change(df)

    assert pd.isna(result.loc[0, "change"])

    assert result.loc[1, "change"] == 85.0

    assert result.loc[2, "change"] == 60.0


def test_price_change_pct():
    df = create_test_data()

    result = calculate_price_change(df)

    assert pd.isna(result.loc[0, "change_pct"])

    assert round(result.loc[1, "change_pct"], 2) == 7.62

    assert round(result.loc[2, "change_pct"], 2) == 5.00


def test_volume_ratio():
    df = create_test_data()

    result = calculate_volume_ratio(
        df,
        window=2,
    )

    assert result.loc[0, "volume_ratio"] == 1.0

    assert round(
        result.loc[1, "volume_ratio"],
        2,
    ) == 1.33

    assert round(
        result.loc[2, "volume_ratio"],
        2,
    ) == 1.20
def create_ma_test_data():
    return pd.DataFrame(
        [
            {
                "symbol": "2330",
                "trade_date": "2026-08-03",
                "close": 100.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-04",
                "close": 110.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-05",
                "close": 120.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-06",
                "close": 130.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-07",
                "close": 140.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-10",
                "close": 150.0,
            },
        ]
    )


def test_moving_average():
    df = create_ma_test_data()

    result = calculate_moving_average(
        df,
        window=5,
    )

    # First four records do not have
    # enough data for MA5.
    assert pd.isna(result.loc[0, "ma5"])
    assert pd.isna(result.loc[1, "ma5"])
    assert pd.isna(result.loc[2, "ma5"])
    assert pd.isna(result.loc[3, "ma5"])

    # MA5 on 2026-08-07:
    # (100 + 110 + 120 + 130 + 140) / 5
    assert result.loc[4, "ma5"] == 120.0

    # MA5 on 2026-08-10:
    # (110 + 120 + 130 + 140 + 150) / 5
    assert result.loc[5, "ma5"] == 130.0


def test_moving_average_insufficient_data():
    df = create_ma_test_data()

    result = calculate_moving_average(
        df,
        window=20,
    )

    # Only 6 observations exist.
    # Therefore MA20 should not be calculated.
    assert result["ma20"].isna().all()

def test_moving_average_invalid_window():
    df = create_ma_test_data()

    try:
        calculate_moving_average(
            df,
            window=0,
        )
        assert False
    except ValueError:
        assert True

def test_moving_averages():
    df = create_test_data()

    result = calculate_moving_averages(
        df,
        windows=[2, 3],
    )

    assert "ma2" in result.columns
    assert "ma3" in result.columns

    assert pd.isna(result.loc[0, "ma2"])
    assert result.loc[1, "ma2"] == 1157.5
    assert result.loc[2, "ma2"] == 1230.0

    assert pd.isna(result.loc[0, "ma3"])
    assert pd.isna(result.loc[1, "ma3"])
    assert result.loc[2, "ma3"] == 1191.6666666666667

def create_kd_test_data():
    return pd.DataFrame(
        [
            {
                "symbol": "2330",
                "trade_date": "2026-08-03",
                "high": 110.0,
                "low": 90.0,
                "close": 100.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-04",
                "high": 112.0,
                "low": 92.0,
                "close": 104.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-05",
                "high": 114.0,
                "low": 94.0,
                "close": 108.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-06",
                "high": 116.0,
                "low": 96.0,
                "close": 110.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-07",
                "high": 118.0,
                "low": 98.0,
                "close": 112.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-10",
                "high": 120.0,
                "low": 100.0,
                "close": 115.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-11",
                "high": 122.0,
                "low": 102.0,
                "close": 118.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-12",
                "high": 124.0,
                "low": 104.0,
                "close": 120.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-13",
                "high": 126.0,
                "low": 106.0,
                "close": 122.0,
            },
        ]
    )

def test_kd():
    df = create_kd_test_data()

    result = calculate_kd(
        df,
        window=9,
    )

    # First 8 observations do not have
    # enough data for a 9-day RSV.
    assert result["rsv"].iloc[:8].isna().all()
    assert result["k"].iloc[:8].isna().all()
    assert result["d"].iloc[:8].isna().all()

    # On 2026-08-13:
    #
    # Highest high = 126
    # Lowest low = 90
    # Close = 122
    #
    # RSV = (122 - 90) / (126 - 90) * 100
    #     = 88.888...
    #
    # Initial K = 50
    # Initial D = 50
    #
    # K = 2/3 * 50 + 1/3 * 88.888...
    #   = 62.962...
    #
    # D = 2/3 * 50 + 1/3 * 62.962...
    #   = 54.320...

    assert round(
        result.loc[8, "rsv"],
        3,
    ) == 88.889

    assert round(
        float(result.loc[8, "k"]),
        3,
    ) == 62.963

    assert round(
        float(result.loc[8, "d"]),
        3,
    ) == 54.321

def create_rsi_test_data():
    return pd.DataFrame(
        [
            {
                "symbol": "2330",
                "trade_date": "2026-08-03",
                "close": 100.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-04",
                "close": 102.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-05",
                "close": 101.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-06",
                "close": 103.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-07",
                "close": 105.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-10",
                "close": 104.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-11",
                "close": 106.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-12",
                "close": 108.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-13",
                "close": 107.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-14",
                "close": 109.0,
            },
            {
                "symbol": "2330",
                "trade_date": "2026-08-17",
                "close": 111.0,
            },
        ]
    )

def test_rsi():
    df = create_rsi_test_data()

    result = calculate_rsi(
        df,
        window=5,
    )

    assert "rsi5" in result.columns

    assert result["rsi5"].iloc[:5].isna().all()

    assert result["rsi5"].iloc[5:].notna().all()

    assert (
        result["rsi5"].iloc[5:].between(0, 100).all()
    )

def test_rsi_insufficient_data():
    df = create_rsi_test_data()

    result = calculate_rsi(
        df,
        window=14,
    )

    assert result["rsi14"].isna().all()

def test_rsi_invalid_window():
    df = create_rsi_test_data()

    try:
        calculate_rsi(
            df,
            window=0,
        )
        assert False
    except ValueError:
        assert True

def test_rsis():
    df = create_rsi_test_data()

    result = calculate_rsis(
        df,
        windows=[5, 7],
    )

    assert "rsi5" in result.columns
    assert "rsi7" in result.columns

    assert result["rsi5"].notna().any()
    assert result["rsi7"].notna().any()

def test_rsi_value():
    df = create_rsi_test_data()

    result = calculate_rsi(
        df,
        window=5,
    )

    # Price changes:
    # +2, -1, +2, +2, -1, +2, +2, -1, +2, +2
    #
    # For the first RSI(5):
    # Gains = [2, 0, 2, 2, 0]
    # Losses = [0, 1, 0, 0, 1]
    #
    # Average gain = 6 / 5 = 1.2
    # Average loss = 2 / 5 = 0.4
    #
    # RS = 1.2 / 0.4 = 3
    #
    # RSI = 100 - 100 / (1 + 3)
    #     = 75

    assert round(
        result.loc[5, "rsi5"],
        3,
    ) == 75.000

def create_wilder_rsi_test_data():
    return pd.DataFrame(
        [
            {"symbol": "2330", "trade_date": "2026-08-03", "close": 44.0},
            {"symbol": "2330", "trade_date": "2026-08-04", "close": 44.15},
            {"symbol": "2330", "trade_date": "2026-08-05", "close": 43.90},
            {"symbol": "2330", "trade_date": "2026-08-06", "close": 44.35},
            {"symbol": "2330", "trade_date": "2026-08-07", "close": 44.20},
            {"symbol": "2330", "trade_date": "2026-08-10", "close": 44.55},
            {"symbol": "2330", "trade_date": "2026-08-11", "close": 44.90},
            {"symbol": "2330", "trade_date": "2026-08-12", "close": 44.70},
            {"symbol": "2330", "trade_date": "2026-08-13", "close": 45.10},
            {"symbol": "2330", "trade_date": "2026-08-14", "close": 45.35},
            {"symbol": "2330", "trade_date": "2026-08-17", "close": 45.00},
            {"symbol": "2330", "trade_date": "2026-08-18", "close": 45.40},
        ]
    )

def test_rsi_wilder_value():
    df = create_rsi_test_data()

    result = calculate_rsi(
        df,
        window=5,
    )

    assert "rsi5" in result.columns

    assert result["rsi5"].iloc[:5].isna().all()

    assert round(
        result.loc[5, "rsi5"],
        6,
    ) == 75.000000