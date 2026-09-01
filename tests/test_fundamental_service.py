import pandas as pd
import pytest

from src.services.fundamental_service import (
    calculate_latest_fundamentals,
    get_fundamental_history,
)


def test_calculate_latest_fundamentals():
    result = calculate_latest_fundamentals("2330")

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 1

    assert "pe" in result.columns
    assert "pb" in result.columns
    assert "dividend_yield" in result.columns

    row = result.iloc[0]

    assert row["symbol"] == "2330"

def test_calculate_latest_fundamentals_unknown_symbol():
    result = calculate_latest_fundamentals("9999")

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_calculate_latest_fundamentals_without_fundamental_record(
    stock_without_fundamental,
):
    result = calculate_latest_fundamentals(
        stock_without_fundamental
    )

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_calculate_latest_fundamentals_values():
    result = calculate_latest_fundamentals("2330")

    assert len(result) == 1

    row = result.iloc[0]

    assert row["symbol"] == "2330"

    # PE 基準優先序（v2.0 統一量化標準）：
    # eps_ttm > eps_ytd > eps；測試資料無 eps_ttm，故用 eps_ytd
    assert float(row["pe"]) == pytest.approx(
        float(row["close"]) / float(row["eps_ytd"]),
        rel=1e-6,
    )

    assert float(row["pb"]) == pytest.approx(
        float(row["close"]) / float(row["bvps"]),
        rel=1e-6,
    )

    assert float(row["dividend_yield"]) == pytest.approx(
        float(row["dps"]) / float(row["close"]) * 100,
        rel=1e-6,
    )

def test_get_fundamental_history():
    result = get_fundamental_history("2330")

    assert isinstance(result, pd.DataFrame)

    assert not result.empty

    expected_columns = {
        "symbol",
        "name",
        "report_year",
        "report_quarter",
        "eps",
        "eps_ytd",
        "bvps",
        "dps",
    }

    assert expected_columns.issubset(
        result.columns
    )

def test_get_fundamental_history_unknown_symbol():
    result = get_fundamental_history("9999")

    assert isinstance(result, pd.DataFrame)

    assert result.empty

def test_get_fundamental_history_sorted():
    result = get_fundamental_history("2330")

    assert isinstance(result, pd.DataFrame)

    if len(result) >= 2:
        periods = list(
            zip(
                result["report_year"],
                result["report_quarter"],
            )
        )

        assert periods == sorted(
            periods,
            reverse=True,
        )