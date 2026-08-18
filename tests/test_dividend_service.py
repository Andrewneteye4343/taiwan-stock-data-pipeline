import pytest

from src.services.fundamental_service import (
    calculate_latest_fundamentals,
)


def test_calculate_latest_fundamentals_uses_latest_dividend():
    result = calculate_latest_fundamentals("2330")

    assert len(result) == 1

    row = result.iloc[0]

    assert row["symbol"] == "2330"

    assert row["cash_dividend"] == pytest.approx(
        6.0,
        rel=1e-6,
    )

    assert row["dividend_yield"] == pytest.approx(
        float(row["cash_dividend"])
        / float(row["close"])
        * 100,
        rel=1e-6,
    )