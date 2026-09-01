import pandas as pd

from src.indicators.fundamental import (
    calculate_fundamentals,
    calculate_ttm_eps,
)


def test_ttm_eps_requires_four_quarters():
    """不足四季時 ttm_eps 應為 NaN（不硬算）。"""

    history = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2025,
                "report_quarter": 1,
                "eps": 10.0,
            },
            {
                "symbol": "2330",
                "report_year": 2025,
                "report_quarter": 2,
                "eps": 12.0,
            },
        ]
    )

    result = calculate_ttm_eps(history)

    assert result["ttm_eps"].isna().all().item()


def test_ttm_eps_rolling_sum():
    """滿四季後，ttm_eps = 最近四季單季 EPS 加總。"""

    history = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "report_year": 2025,
                "report_quarter": 1,
                "eps": 10.0,
            },
            {
                "symbol": "2330",
                "report_year": 2025,
                "report_quarter": 2,
                "eps": 12.0,
            },
            {
                "symbol": "2330",
                "report_year": 2025,
                "report_quarter": 3,
                "eps": 15.0,
            },
            {
                "symbol": "2330",
                "report_year": 2025,
                "report_quarter": 4,
                "eps": 20.0,
            },
            {
                "symbol": "2330",
                "report_year": 2026,
                "report_quarter": 1,
                "eps": 11.0,
            },
        ]
    )

    result = calculate_ttm_eps(history)

    result = result.sort_values(
        ["report_year", "report_quarter"]
    )

    assert result.iloc[3]["ttm_eps"] == 57.0
    assert result.iloc[4]["ttm_eps"] == 58.0


def test_pe_prefers_ttm_eps():
    """PE 應以 eps_ttm 為基準（優於 eps / eps_ytd）。"""

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 580.0,
                "eps_ttm": 58.0,
                "eps": 11.0,
                "eps_ytd": 50.0,
                "bvps": 100.0,
                "dps": 20.0,
            }
        ]
    )

    result = calculate_fundamentals(df)

    assert result.loc[0, "pe"] == 10.0


def test_fundamentals_include_margins():
    """有損益表欄位時應計算三種利潤率。"""

    df = pd.DataFrame(
        [
            {
                "symbol": "2330",
                "close": 580.0,
                "eps": 10.0,
                "bvps": 100.0,
                "dps": 20.0,
                "revenue": 1000.0,
                "gross_profit": 400.0,
                "operating_income": 300.0,
                "net_income": 200.0,
            }
        ]
    )

    result = calculate_fundamentals(df)

    assert result.loc[0, "gross_margin"] == 40.0
    assert result.loc[0, "operating_margin"] == 30.0
    assert result.loc[0, "net_margin"] == 20.0
