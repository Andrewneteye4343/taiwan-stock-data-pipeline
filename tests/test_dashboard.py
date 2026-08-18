import pandas as pd
import pytest

from dashboard.app import (
    calculate_price_change,
    get_latest_price_summary,
    get_stock_options,
)

def test_get_stock_options():
    options = get_stock_options()

    assert isinstance(options, list)
    assert len(options) >= 3


def test_get_stock_options_contains_expected_stocks():
    options = get_stock_options()

    symbols = [item["symbol"] for item in options]

    assert "2330" in symbols
    assert "2317" in symbols
    assert "2454" in symbols


def test_get_stock_options_contains_stock_names():
    options = get_stock_options()

    stock_map = {
        item["symbol"]: item["name"]
        for item in options
    }

    assert stock_map["2330"] == "台積電"
    assert stock_map["2317"] == "鴻海"
    assert stock_map["2454"] == "聯發科"

def test_calculate_price_change():
    result = calculate_price_change(
        previous_close=100.0,
        current_close=105.0,
    )

    assert result["change"] == 5.0
    assert result["change_pct"] == 5.0


def test_calculate_price_change_loss():
    result = calculate_price_change(
        previous_close=100.0,
        current_close=95.0,
    )

    assert result["change"] == -5.0
    assert result["change_pct"] == -5.0


def test_calculate_price_change_zero_previous_close():
    result = calculate_price_change(
        previous_close=0.0,
        current_close=100.0,
    )

    assert result["change"] is None
    assert result["change_pct"] is None

def test_get_latest_price_summary():
    df = pd.DataFrame(
        [
            {
                "trade_date": "2026-08-17",
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000,
            },
            {
                "trade_date": "2026-08-18",
                "open": 104.0,
                "high": 110.0,
                "low": 102.0,
                "close": 108.0,
                "volume": 1500,
            },
        ]
    )

    result = get_latest_price_summary(df)

    assert result["trade_date"] == "2026-08-18"
    assert result["open"] == 104.0
    assert result["high"] == 110.0
    assert result["low"] == 102.0
    assert result["close"] == 108.0
    assert result["volume"] == 1500

    assert result["change"] == 5.0
    assert result["change_pct"] == pytest.approx(
        4.854368932,
        rel=1e-6,
    )


def test_get_latest_price_summary_requires_two_records():
    df = pd.DataFrame(
        [
            {
                "trade_date": "2026-08-18",
                "open": 104.0,
                "high": 110.0,
                "low": 102.0,
                "close": 108.0,
                "volume": 1500,
            }
        ]
    )

    result = get_latest_price_summary(df)

    assert result is None