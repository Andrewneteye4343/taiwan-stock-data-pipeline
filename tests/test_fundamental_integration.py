import pandas as pd

from src.indicators.fundamental import calculate_fundamentals


def test_calculate_fundamentals_integration():
    """
    Test the complete fundamental indicator calculation flow.

    The input DataFrame represents data that has already been
    integrated from:

    - daily price
    - quarterly fundamental data
    - dividend data

    calculate_fundamentals() is responsible only for calculating
    PE, PB, and dividend yield.
    """

    integrated_data = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "trade_date": "2026-08-14",
                "close": 1180.0,
                "report_year": 2026,
                "report_quarter": 2,
                "eps": 12.34,
                "eps_ytd": 22.84,
                "bvps": 125.67,
                "dividend_year": 2026,
                "dps": 5.00,
            }
        ]
    )

    result = calculate_fundamentals(integrated_data)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1

    assert result.loc[0, "symbol"] == "2330"
    assert result.loc[0, "close"] == 1180.0

    assert result.loc[0, "eps_ytd"] == 22.84
    assert result.loc[0, "bvps"] == 125.67
    assert result.loc[0, "dps"] == 5.00

    # PE 基準優先序（v2.0 統一量化標準）：
    # eps_ttm > eps_ytd > eps；此處無 eps_ttm，故用 eps_ytd
    assert result.loc[0, "pe"] == 1180.0 / 22.84

    # PB uses BVPS
    assert result.loc[0, "pb"] == 1180.0 / 125.67

    # Dividend Yield = DPS / Close * 100
    assert result.loc[0, "dividend_yield"] == (
        5.00 / 1180.0 * 100
    )


def test_calculate_fundamentals_multiple_stocks():
    """
    Test fundamental indicator calculation for multiple stocks.
    """

    integrated_data = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "trade_date": "2026-08-14",
                "close": 1180.0,
                "report_year": 2026,
                "report_quarter": 2,
                "eps": 12.34,
                "eps_ytd": 22.84,
                "bvps": 125.67,
                "dividend_year": 2026,
                "dps": 5.00,
            },
            {
                "symbol": "2317",
                "trade_date": "2026-08-14",
                "close": 185.0,
                "report_year": 2026,
                "report_quarter": 2,
                "eps": 9.10,
                "eps_ytd": 17.30,
                "bvps": 98.20,
                "dividend_year": 2026,
                "dps": 5.50,
            },
        ]
    )

    result = calculate_fundamentals(integrated_data)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2

    stock_2330 = result[
        result["symbol"] == "2330"
    ].iloc[0]

    stock_2317 = result[
        result["symbol"] == "2317"
    ].iloc[0]

    # 2330（PE 用 eps_ytd：優先序 eps_ttm > eps_ytd > eps）
    assert stock_2330["pe"] == 1180.0 / 22.84
    assert stock_2330["pb"] == 1180.0 / 125.67
    assert stock_2330["dividend_yield"] == (
        5.00 / 1180.0 * 100
    )

    # 2317（PE 用 eps_ytd）
    assert stock_2317["pe"] == 185.0 / 17.30
    assert stock_2317["pb"] == 185.0 / 98.20
    assert stock_2317["dividend_yield"] == (
        5.50 / 185.0 * 100
    )