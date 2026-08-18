import pandas as pd
import pytest

from src.services.fundamental_service import (
    calculate_latest_fundamentals,
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


def test_calculate_latest_fundamentals_without_fundamental_record():
    result = calculate_latest_fundamentals("2317")

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_calculate_latest_fundamentals_values():
    result = calculate_latest_fundamentals("2330")

    assert len(result) == 1

    row = result.iloc[0]

    assert row["symbol"] == "2330"

    assert float(row["pe"]) == pytest.approx(
        float(row["close"]) / float(row["eps"]),
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